from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from django.db.models import Q
import json
import logging

from .models import ChatMessage, KnowledgeBase
from .serializers import ChatMessageSerializer, KnowledgeBaseSerializer
from .utils_localai import generate_response, stream_response
from .system_knowledge import get_system_knowledge, get_bacteria_info, get_antibiotic_info, get_procedure_info

# Import models for database queries
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from results.models import TestResult
from samples.models import Sample

logger = logging.getLogger(__name__)


class ChatbotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling chatbot interactions with Ollama/LLaMA 3.1
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ChatbotUtils not needed - using Ollama directly via utils_localai
    
    def get_queryset(self):
        """Filter messages by current user"""
        return ChatMessage.objects.filter(user=self.request.user).order_by('-timestamp')
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Main chat endpoint - handles user questions and returns AI responses
        """
        try:
            user_message = request.data.get('message', '').strip()
            
            if not user_message:
                return Response(
                    {'error': 'الرجاء إدخال سؤال'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Detect language
            language = self._detect_language(user_message)
            
            # Build context from system knowledge and database
            context = self._build_context(user_message, language)
            
            # Generate response using Ollama via utils_localai
            ai_response = generate_response(
                user_message=user_message,
                context=context,
                language=language
            )
            
            # Save to database
            chat_message = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=ai_response.get('response', ''),
                sources=ai_response.get('sources', []),
                source_type='mixed'
            )
            
            return Response({
                'id': chat_message.id,
                'message': user_message,
                'response': ai_response.get('response', ''),
                'sources': ai_response.get('sources', []),
                'timestamp': chat_message.timestamp,
                'language': language
            })
            
        except Exception as e:
            logger.error("Chat error", exc_info=True)
            return Response(
                {'error': 'حدث خطأ في معالجة طلبك. يرجى المحاولة مجددا.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def stream_chat(self, request):
        """
        Streaming chat endpoint for real-time responses
        """
        try:
            user_message = request.data.get('message', '').strip()
            
            if not user_message:
                return Response(
                    {'error': 'الرجاء إدخال سؤال'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            language = self._detect_language(user_message)
            context = self._build_context(user_message, language)
            
            # Capture request user before defining generator
            request_user = request.user
            
            def generate():
                """Generator function for streaming response"""
                full_response = ""
                
                try:
                    # Stream from Ollama
                    for chunk in stream_response(
                        user_message=user_message,
                        context=context,
                        language=language
                    ):
                        full_response += chunk
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    
                    # Schedule message save after streaming completes
                    # In production, use Celery or queue this for async processing
                    ChatMessage.objects.create(
                        user=request_user,
                        message=user_message,
                        response=full_response,
                        source_type='mixed'
                    )
                    
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
                except Exception as e:
                    logger.error("Streaming error", exc_info=True)
                    yield f"data: {json.dumps({'error': 'Stream error occurred'})}\n\n"
            
            response = StreamingHttpResponse(
                generate(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
            
        except Exception as e:
            logger.error(f"Stream chat error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'حدث خطأ: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get chat history for current user
        """
        try:
            # Validate and sanitize limit parameter
            try:
                limit = int(request.query_params.get('limit', 50))
                # Enforce bounds: minimum 1, maximum 100
                limit = max(1, min(limit, 100))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid limit parameter'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            messages = self.get_queryset()[:limit]
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error("History error", exc_info=True)
            return Response(
                {'error': 'Failed to load history'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """
        Clear chat history for current user
        """
        try:
            deleted_count = self.get_queryset().delete()[0]
            return Response({
                'message': f'تم حذف {deleted_count} رسالة',
                'deleted_count': deleted_count
            })
        except Exception as e:
            logger.error(f"Clear history error: {str(e)}")
            return Response(
                {'error': 'فشل في حذف السجل'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def quick_query(self, request):
        """
        Quick database queries for specific information
        """
        try:
            query_type = request.data.get('type', '')
            params = request.data.get('params', {})
            
            result = self._execute_quick_query(query_type, params)
            
            return Response({
                'query_type': query_type,
                'result': result
            })
            
        except Exception as e:
            logger.error("Quick query error", exc_info=True)
            return Response(
                {'error': 'فشل في تنفيذ الاستعلام. يرجى المحاولة مجددا.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _detect_language(self, text):
        """Detect if text is Arabic or English"""
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    
    def _build_context(self, user_message, language):
        """
        Build comprehensive context from system knowledge and database
        """
        context_parts = []
        
        # Add system knowledge
        context_parts.append(get_system_knowledge())
        
        # Check for specific bacteria mentions
        bacteria_keywords = ['staphylococcus', 'escherichia', 'e. coli', 'klebsiella', 
                            'pseudomonas', 'acinetobacter', 'بكتيريا']
        if any(keyword in user_message.lower() for keyword in bacteria_keywords):
            bacteria_list = Bacteria.objects.all()[:10]
            if bacteria_list:
                context_parts.append("\n## البكتيريا المتوفرة في النظام:")
                for bacteria in bacteria_list:
                    context_parts.append(f"- {bacteria.name}")
        
        # Check for antibiotic mentions
        antibiotic_keywords = ['antibiotic', 'vancomycin', 'meropenem', 'ciprofloxacin',
                              'مضاد', 'علاج']
        if any(keyword in user_message.lower() for keyword in antibiotic_keywords):
            antibiotics_list = Antibiotic.objects.all()[:10]
            if antibiotics_list:
                context_parts.append("\n## المضادات الحيوية المتوفرة:")
                for antibiotic in antibiotics_list:
                    context_parts.append(f"- {antibiotic.name}")
        
        # Check for resistance/sensitivity queries
        if any(word in user_message.lower() for word in ['resistance', 'sensitive', 'مقاومة', 'حساسية']):
            recent_results = TestResult.objects.select_related('sample', 'antibiotic').order_by('-id')[:5]
            if recent_results:
                context_parts.append("\n## نتائج حديثة:")
                for result in recent_results:
                    antibiotic_name = result.antibiotic.name if result.antibiotic else 'Unknown antibiotic'
                    context_parts.append(
                        f"- {antibiotic_name}: {result.sensitivity}"
                    )
        
        # Check for system navigation queries
        navigation_keywords = ['how to', 'كيف', 'صفحة', 'page', 'navigate', 'استخدام']
        if any(keyword in user_message.lower() for keyword in navigation_keywords):
            context_parts.append("""
## إرشادات التنقل في النظام:
- لوحة التحكم: /dashboard
- خريطة الحرارة: /heatmap
- توزيع الحساسية: /sensitivity-distribution
- المقاومة عبر الزمن: /resistance-trends
- إدارة العينات: /samples
- نتائج الاختبارات: /results
- التقارير: /reports
- رفع البيانات: /upload
            """)
        
        return "\n".join(context_parts)
    
    def _execute_quick_query(self, query_type, params):
        """
        Execute specific database queries
        """
        if query_type == 'bacteria_count':
            return {'count': Bacteria.objects.count()}
        
        elif query_type == 'antibiotic_count':
            return {'count': Antibiotic.objects.count()}
        
        elif query_type == 'sample_count':
            return {'count': Sample.objects.count()}
        
        elif query_type == 'resistance_rate':
            bacteria_name = params.get('bacteria')
            antibiotic_name = params.get('antibiotic')
            
            # Validate required parameters
            if not bacteria_name or not antibiotic_name:
                return {'error': 'Required parameters: bacteria and antibiotic'}
            
            results = TestResult.objects.filter(
                sample__bacteria__name__icontains=bacteria_name,
                antibiotic__name__icontains=antibiotic_name
            )
            
            total = results.count()
            resistant = results.filter(sensitivity='resistant').count()
            
            return {
                'total': total,
                'resistant': resistant,
                'resistance_rate': (resistant / total * 100) if total > 0 else 0
            }
        
        elif query_type == 'recent_samples':
            # Validate and sanitize limit parameter
            try:
                limit = int(params.get('limit', 10))
                # Enforce bounds: minimum 1, maximum 100
                limit = max(1, min(limit, 100))
            except (ValueError, TypeError):
                limit = 10
            
            samples = Sample.objects.select_related('bacteria').order_by('-collection_date')[:limit]
            
            return {
                'samples': [
                    {
                        'id': s.id,
                        'bacteria': s.bacteria.name if s.bacteria else 'Unknown',
                        'date': s.collection_date.isoformat() if s.collection_date else None,
                        'department': s.department
                    }
                    for s in samples
                ]
            }
        
        else:
            return {'error': 'Unknown query type'}


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing knowledge base entries
    """
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def add_knowledge(self, request):
        """
        Add new knowledge to the knowledge base
        """
        try:
            content = request.data.get('content', '')
            source = request.data.get('source', 'manual')
            metadata = request.data.get('metadata', {})
            
            if not content:
                return Response(
                    {'error': 'المحتوى مطلوب'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create embedding (placeholder - implement actual embedding)
            embedding = []
            
            kb_entry = KnowledgeBase.objects.create(
                content=content,
                source=source,
                embedding=embedding,
                metadata=metadata
            )
            
            return Response({
                'id': kb_entry.id,
                'message': 'تمت إضافة المعرفة بنجاح'
            })
            
        except Exception as e:
            logger.error("Add knowledge error", exc_info=True)
            return Response(
                {'error': 'Failed to add knowledge'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search knowledge base
        """
        try:
            query = request.query_params.get('q', '')
            
            # Validate and sanitize limit parameter
            try:
                limit = int(request.query_params.get('limit', 10))
                # Enforce bounds: minimum 1, maximum 100
                limit = max(1, min(limit, 100))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid limit parameter'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not query:
                return Response(
                    {'error': 'Search query is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Simple text search (can be enhanced with vector search)
            # Convert queryset to list before slicing to avoid count() issues
            results_queryset = KnowledgeBase.objects.filter(
                Q(content__icontains=query) | Q(source__icontains=query)
            )
            results_list = list(results_queryset[:limit])
            
            return Response({
                'query': query,
                'count': len(results_list),
                'results': [
                    {
                        'id': r.id,
                        'content': r.content[:200] + '...' if len(r.content) > 200 else r.content,
                        'source': r.source
                    }
                    for r in results_list
                ]
            })
            
        except Exception as e:
            logger.error("Search knowledge error", exc_info=True)
            return Response(
                {'error': 'Search failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
