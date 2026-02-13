from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import Message, MessageAttachment
from .serializers import MessageSerializer, MessageCreateSerializer, MessageAttachmentSerializer
from api.permissions import MessagingPermissions

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [MessagingPermissions]

    def get_queryset(self):
        user = self.request.user
        # Exclude archived messages unless admin
        queryset = Message.objects.filter(Q(sender=user) | Q(recipient=user) | Q(message_type='broadcast'))
        if not user.is_admin:
            queryset = queryset.filter(is_archived=False)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Override destroy to archive instead of delete
        instance = self.get_object()
        instance.is_archived = True
        instance.save()
        return Response({'status': 'message archived'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient == request.user or message.message_type == 'broadcast':
            message.read_status = True
            message.save()
            return Response({'status': 'message marked as read'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        message = self.get_object()
        if request.user.is_admin or message.sender == request.user:
            message.is_archived = True
            message.save()
            return Response({'status': 'message archived'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        message = self.get_object()
        if request.user.is_admin:
            message.is_archived = False
            message.save()
            return Response({'status': 'message unarchived'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        messages = self.get_queryset().filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        messages = self.get_queryset().filter(Q(recipient=request.user) | Q(message_type='broadcast'))
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        messages = self.get_queryset().filter(
            Q(recipient=request.user, read_status=False) |
            Q(message_type='broadcast', read_status=False)
        )
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def archived(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        messages = Message.objects.filter(is_archived=True)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def broadcast(self, request):
        if not request.user.is_admin:
            return Response({'error': 'Only admins can send broadcast messages'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save(message_type='broadcast')
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        sender = request.query_params.get('sender', '')
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')
        message_type = request.query_params.get('message_type', '')

        queryset = self.get_queryset()

        if query:
            queryset = queryset.filter(
                Q(subject__icontains=query) |
                Q(content__icontains=query)
            )

        if sender:
            queryset = queryset.filter(sender__username__icontains=sender)

        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        if message_type:
            queryset = queryset.filter(message_type=message_type)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def contextual(self, request):
        content_type_id = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')

        if not content_type_id or not object_id:
            return Response({'error': 'content_type and object_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get(id=content_type_id)
            queryset = self.get_queryset().filter(
                content_type=content_type,
                object_id=object_id
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ContentType.DoesNotExist:
            return Response({'error': 'Invalid content_type'}, status=status.HTTP_400_BAD_REQUEST)

class MessageAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = MessageAttachmentSerializer
    permission_classes = [MessagingPermissions]

    def get_queryset(self):
        user = self.request.user
        return MessageAttachment.objects.filter(
            Q(message__sender=user) | Q(message__recipient=user) | Q(message__message_type='broadcast')
        )
