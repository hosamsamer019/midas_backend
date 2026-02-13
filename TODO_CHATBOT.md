# TODO: Intelligent Chatbot Implementation

## Overview
Implement an intelligent chatbot for the Smart Antibiogram System with Arabic support, RAG, PHI privacy, and system awareness.

## Steps

### 1. Backend Setup
- [x] Create new Django app 'chatbot' with `python manage.py startapp chatbot`
- [x] Add 'chatbot' to INSTALLED_APPS in settings.py
- [x] Create models: ChatMessage (for history), KnowledgeBase (for chunks)
- [x] Run migrations for new models

### 2. Vector Database and Embeddings
- [x] Install FAISS and sentence-transformers (add to requirements.txt)
- [x] Set up FAISS vector store in chatbot app
- [x] Implement Arabic embeddings using OpenAI text-embedding-3-small or AraBERT
- [x] Create utility functions for text chunking and embedding

### 3. Knowledge Base Population
- [x] Extract and chunk system docs (help pages, FAQs from existing files)
- [x] Chunk and embed ICU antibiotic.xlsx and other medical data
- [x] Implement script to populate vector DB with chunks
- [x] Add endpoint to update KB when new files are uploaded

### 4. RAG and LLM Integration
- [x] Implement retriever: search vector DB for top-k relevant chunks
- [x] Set up OpenAI API integration for LLM generation
- [x] Create RAG prompt template for Arabic responses
- [x] Implement fallback logic: local KB -> external LLM

### 5. PHI Anonymization and Safety
- [x] Implement PHI detection (names, phones, patient IDs)
- [x] Create anonymization function to remove/replace PHI
- [x] Add safety checks before external LLM calls
- [x] Implement warning for sensitive queries

### 6. Logging and Audit
- [x] Create ChatLog model for storing conversations
- [x] Log questions, answers, sources, user ID
- [x] Add audit trail for PHI-related queries

### 7. Chat Endpoints
- [x] Create /api/chat/ endpoint for sending messages
- [x] Create /api/chat/history/ for conversation history
- [x] Add authentication and role-based permissions

### 8. Frontend Chat Widget
- [x] Create ChatWidget component in Next.js
- [x] Implement text input, quick buttons (system, bacteria, etc.)
- [x] Display responses with sources and citations
- [x] Add history sidebar and action buttons (open patient, generate report)

### 9. Integration and UI
- [x] Integrate ChatWidget into main layout (bottom right fixed)
- [x] Add Arabic text normalization in frontend
- [x] Implement voice activation and text-to-speech (optional)

### 10. Testing and Validation
- [ ] Test Arabic responses for 50 medical/system questions
- [ ] PHI anonymization test
- [ ] Fallback to external LLM test
- [ ] Latency tests (<1.5s retrieval, <3s LLM)
- [ ] Permissions test for patient data access
- [ ] Clinical review with physicians

### 11. Dependencies and Deployment
- [x] Update requirements.txt with new packages (faiss-cpu, openai, etc.)
- [x] Update package.json for frontend if needed
- [x] Update Docker setup for new services
- [x] Production deployment considerations (vector DB persistence)

## Notes
- Ensure all responses are in Modern Standard Arabic
- Respect privacy: no PHI to external LLMs without anonymization
- Cite sources in answers
- Legal disclaimer in responses
