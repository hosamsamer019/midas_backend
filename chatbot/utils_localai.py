"""
Utility functions for interacting with Ollama/Gemma 3.4b local AI
"""
import requests
import json
import logging
from typing import Dict, Any, Generator

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma3:4b"


def generate_response(user_message: str, context: str = "", language: str = "ar") -> Dict[str, Any]:
    """
    Generate a response using Ollama with Gemma 3.4b model
    
    Args:
        user_message: The user's question
        context: System knowledge and database context
        language: Language code ('ar' for Arabic, 'en' for English)
    
    Returns:
        Dictionary with 'response' and 'sources' keys
    """
    
    # Build the prompt
    if language == "ar":
        system_prompt = """أنت مساعد ذكي متخصص في نظام تحليل المضادات الحيوية لمستشفى المنصورة.
مهمتك مساعدة الأطباء المقيمين في:
1. فهم كيفية استخدام النظام
2. تفسير نتائج الاختبارات
3. اختيار المضادات الحيوية المناسبة
4. فهم أنماط المقاومة البكتيرية

يجب أن تكون إجاباتك:
- دقيقة ومبنية على المعرفة الطبية
- واضحة وسهلة الفهم
- تحذر من أنها ليست بديلاً عن استشارة الطبيب المختص
- باللغة العربية الفصحى"""
    else:
        system_prompt = """You are an intelligent assistant specialized in the Antibiotic Analysis System for Mansoura Hospital.
Your mission is to help resident doctors with:
1. Understanding how to use the system
2. Interpreting test results
3. Selecting appropriate antibiotics
4. Understanding bacterial resistance patterns

Your answers should be:
- Accurate and based on medical knowledge
- Clear and easy to understand
- Include a warning that they are not a substitute for consulting a specialist doctor
- In clear English"""
    
    prompt = f"""{system_prompt}

المعرفة المتاحة / Available Knowledge:
{context}

السؤال / Question: {user_message}

الإجابة / Answer:"""
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "top_k": 1,
                    "num_predict": 500,
                    "repeat_penalty": 1.0
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            if ai_response:
                return {
                    'response': ai_response,
                    'sources': ['Ollama Gemma3:4b', 'System Knowledge Base']
                }
            else:
                return {
                    'response': 'عذراً، لم يتم توليد إجابة. يرجى المحاولة مرة أخرى.',
                    'sources': []
                }
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return {
                'response': f'عذراً، حدث خطأ في خدمة الذكاء الاصطناعي (رمز: {response.status_code})',
                'sources': []
            }
    
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama service")
        return {
            'response': 'عذراً، لا يمكن الاتصال بخدمة Ollama. يرجى التأكد من تشغيل Ollama على المنفذ 11434.',
            'sources': []
        }
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout")
        return {
            'response': 'عذراً، انتهت مهلة الانتظار. يرجى المحاولة مرة أخرى.',
            'sources': []
        }
    except Exception as e:
        logger.error("Error generating response", exc_info=True)
        return {
            'response': 'عذراً، حدث خطأ داخلي. نعمل على إصلاحه.',
            'sources': []
        }


def stream_response(user_message: str, context: str = "", language: str = "ar") -> Generator[str, None, None]:
    """
    Stream a response from Ollama with LLaMA 3.1
    
    Args:
        user_message: The user's question
        context: System knowledge and database context
        language: Language code ('ar' for Arabic, 'en' for English)
    
    Yields:
        Chunks of the response text
    """
    
    # Build the prompt (same as generate_response)
    if language == "ar":
        system_prompt = """أنت مساعد ذكي متخصص في نظام تحليل المضادات الحيوية لمستشفى المنصورة.
مهمتك مساعدة الأطباء المقيمين في:
1. فهم كيفية استخدام النظام
2. تفسير نتائج الاختبارات
3. اختيار المضادات الحيوية المناسبة
4. فهم أنماط المقاومة البكتيرية

يجب أن تكون إجاباتك:
- دقيقة ومبنية على المعرفة الطبية
- واضحة وسهلة الفهم
- تحذر من أنها ليست بديلاً عن استشارة الطبيب المختص
- باللغة العربية الفصحى"""
    else:
        system_prompt = """You are an intelligent assistant specialized in the Antibiotic Analysis System for Mansoura Hospital.
Your mission is to help resident doctors with:
1. Understanding how to use the system
2. Interpreting test results
3. Selecting appropriate antibiotics
4. Understanding bacterial resistance patterns

Your answers should be:
- Accurate and based on medical knowledge
- Clear and easy to understand
- Include a warning that they are not a substitute for consulting a specialist doctor
- In clear English"""
    
    prompt = f"""{system_prompt}

المعرفة المتاحة / Available Knowledge:
{context}

السؤال / Question: {user_message}

الإجابة / Answer:"""
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "top_k": 1,
                    "num_predict": 500,
                    "repeat_penalty": 1.0
                }
            },
            stream=True,
            timeout=120
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        chunk_data = json.loads(line)
                        if 'response' in chunk_data:
                            yield chunk_data['response']
                    except json.JSONDecodeError:
                        continue
        else:
            yield f"عذراً، حدث خطأ في خدمة الذكاء الاصطناعي (رمز: {response.status_code})"
    
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama service")
        yield "عذراً، لا يمكن الاتصال بخدمة Ollama. يرجى التأكد من تشغيل Ollama."
    except requests.exceptions.Timeout:
        logger.error("Ollama request timeout")
        yield "عذراً، انتهت مهلة الانتظار."
    except Exception as e:
        logger.error("Error streaming response", exc_info=True)
        yield "عذراً، حدث خطأ."


def check_ollama_status() -> Dict[str, Any]:
    """
    Check if Ollama service is running and available
    
    Returns:
        Dictionary with status information
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            # Safe lookup with filtering for malformed entries
            available_models = [m.get('name') for m in models if m.get('name')]
            return {
                'status': 'running',
                'available_models': available_models,
                'message': 'Ollama is running and available'
            }
        else:
            return {
                'status': 'error',
                'available_models': [],
                'message': f'Ollama returned status code: {response.status_code}'
            }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'offline',
            'available_models': [],
            'message': 'Cannot connect to Ollama. Please ensure it is running on port 11434.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'available_models': [],
            'message': f'Error checking Ollama status: {str(e)}'
        }
