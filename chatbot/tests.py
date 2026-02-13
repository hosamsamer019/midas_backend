from django.test import TestCase
from django.contrib.auth import get_user_model
from chatbot.models import ChatMessage, KnowledgeBase

User = get_user_model()


class ChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.message = ChatMessage.objects.create(
            user=self.user,
            message='Test question',
            response='Test answer',
            source='KB'
        )

    def test_chat_message_creation(self):
        self.assertEqual(self.message.message, 'Test question')
        self.assertEqual(self.message.response, 'Test answer')
        self.assertEqual(self.message.source, 'KB')


class KnowledgeBaseModelTest(TestCase):
    def setUp(self):
        self.chunk = KnowledgeBase.objects.create(
            source='ICU antibiotic.xlsx',
            content='Sample content',
            embedding=[0.1, 0.2, 0.3]  # Mock embedding
        )

    def test_knowledge_base_creation(self):
        self.assertEqual(self.chunk.source, 'ICU antibiotic.xlsx')
        self.assertEqual(self.chunk.content, 'Sample content')
