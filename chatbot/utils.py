import os
import re
import json
import pandas as pd
from typing import List, Dict, Any
# import faiss  # Temporarily commented out due to installation issues
import numpy as np
# from sentence_transformers import SentenceTransformer  # Temporarily commented out due to installation issues
import requests
from django.conf import settings
from .models import KnowledgeBase

class ChatbotUtils:
    def __init__(self):
        try:
            # Try to import and initialize SentenceTransformer
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        except ImportError:
            # Fallback if sentence_transformers is not available
            self.embedding_model = None
            print("Warning: sentence_transformers not available. Chatbot functionality will be limited.")

        self.index = None
        self.knowledge_base = []
        self.load_knowledge_base()
        self._initialize_data_knowledge()

        # LocalAI setup
        self.localai_base_url = getattr(settings, 'LOCALAI_BASE_URL', 'http://localhost:8080/v1')
        self.localai_api_key = getattr(settings, 'LOCALAI_API_KEY', 'localai')

    def load_knowledge_base(self):
        """Load knowledge base from database and create FAISS index"""
        kb_entries = KnowledgeBase.objects.all()
        if kb_entries.exists():
            self.knowledge_base = [
                {
                    'content': entry.content,
                    'source': entry.source,
                    'metadata': entry.metadata
                }
                for entry in kb_entries
            ]

            # Create embeddings only if model is available
            if self.embedding_model:
                try:
                    import faiss
                    embeddings = []
                    for entry in self.knowledge_base:
                        embedding = self.embedding_model.encode(entry['content'])
                        embeddings.append(embedding)

                    if embeddings:
                        embeddings = np.array(embeddings)
                        dimension = embeddings.shape[1]
                        self.index = faiss.IndexFlatIP(dimension)
                        faiss.normalize_L2(embeddings)
                        self.index.add(embeddings)
                except ImportError:
                    print("FAISS not available, knowledge base search will use text matching only.")
                    self.index = None
            else:
                self.index = None

    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base using FAISS"""
        if not self.embedding_model or not self.index or not self.knowledge_base:
            # Fallback: return basic text matching results
            results = []
            query_lower = query.lower()
            for entry in self.knowledge_base[:top_k]:
                content_lower = entry['content'].lower()
                if query_lower in content_lower:
                    result = entry.copy()
                    result['score'] = 0.5  # Default score for text matching
                    results.append(result)
            return results

        try:
            import faiss
            query_embedding = self.embedding_model.encode(query)
            query_embedding = np.array([query_embedding])
            faiss.normalize_L2(query_embedding)

            scores, indices = self.index.search(query_embedding, min(top_k, len(self.knowledge_base)))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.knowledge_base):
                    result = self.knowledge_base[idx].copy()
                    result['score'] = float(score)
                    results.append(result)

            return results
        except ImportError:
            # Fallback to basic text matching
            results = []
            query_lower = query.lower()
            for entry in self.knowledge_base[:top_k]:
                content_lower = entry['content'].lower()
                if query_lower in content_lower:
                    result = entry.copy()
                    result['score'] = 0.5
                    results.append(result)
            return results

    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        # Simple language detection based on Arabic characters
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len(text.replace(' ', ''))

        if arabic_chars / total_chars > 0.3:  # More than 30% Arabic characters
            return 'ar'
        else:
            return 'en'

    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate multilingual response with data-driven answers"""
        # Detect language
        language = self.detect_language(query)
        query_lower = query.lower()

        # Try to get real data from the API
        try:
            data_response = self._get_relevant_data(query_lower)
            if data_response:
                return self._format_data_response(query_lower, data_response, language)
        except Exception as e:
            print(f"Error fetching data: {e}")

        # Fallback to context-based responses
        context_text = ""
        if context:
            context_text = "\n".join([f"- {item['content'][:200]}" for item in context[:2]])

        # Provide helpful fallback responses based on common queries
        # Arabic responses
        if language == 'ar':
            if any(keyword in query_lower for keyword in ['مضاد', 'antibiotic', 'مضاد حيوي']):
                return f"""نعم، يمكنني مساعدتك في معلومات حول المضادات الحيوية.

المعلومات المتاحة من قاعدة البيانات:
{context_text}

**نصائح مهمة:**
- المضادات الحيوية تعالج العدوى البكتيرية فقط
- لا تستخدم المضادات الحيوية للإنفلونزا أو البرد
- أكمل دائماً الدورة العلاجية كاملة
- استشر طبيبك دائماً قبل استخدام أي مضاد حيوي

⚠️ **تنبيه مهم**: هذه معلومات عامة فقط. يرجى استشارة الطبيب للحصول على تشخيص وعلاج مناسب لحالتك."""

            elif any(keyword in query_lower for keyword in ['مقاومة', 'resistance', 'resist']):
                return f"""المعلومات حول مقاومة البكتيريا للمضادات الحيوية:

{context_text}

**أسباب المقاومة:**
- استخدام المضادات الحيوية بشكل غير صحيح
- عدم إكمال الدورة العلاجية
- استخدام المضادات الحيوية في الزراعة

**كيفية الوقاية:**
- استخدم المضادات الحيوية فقط عند الحاجة
- اتبع تعليمات الطبيب بدقة
- اغسل يديك بانتظام
- أكمل التطعيمات

⚠️ **تنبيه**: استشر متخصصاً في الأمراض المعدية لمعلومات محدثة."""

            else:
                return f"""مرحباً! أنا مساعد طبي متخصص في المضادات الحيوية والأمراض المعدية.

يمكنني مساعدتك في:
- معلومات حول المضادات الحيوية وطريقة عملها
- شرح أنماط المقاومة البكتيرية
- نصائح وقائية للحد من انتشار العدوى
- معلومات عامة عن الأمراض المعدية الشائعة

{context_text}

⚠️ **مهم**: هذه معلومات تعليمية عامة فقط. لست بديلاً عن استشارة الطبيب. يرجى استشارة متخصص طبي لأي مشكلة صحية."""

        # English responses
        else:
            if any(keyword in query_lower for keyword in ['antibiotic', 'مضاد', 'مضاد حيوي']):
                return f"""Yes, I can help you with information about antibiotics.

Available information from the database:
{context_text}

**Important tips:**
- Antibiotics only treat bacterial infections
- Don't use antibiotics for colds or flu
- Always complete the full course of treatment
- Always consult your doctor before using antibiotics

⚠️ **Important warning**: This is general information only. Please consult a doctor for proper diagnosis and treatment for your condition."""

            elif any(keyword in query_lower for keyword in ['resistance', 'resist', 'مقاومة']):
                return f"""Information about bacterial resistance to antibiotics:

{context_text}

**Causes of resistance:**
- Improper use of antibiotics
- Not completing the full treatment course
- Use of antibiotics in agriculture

**Prevention:**
- Use antibiotics only when necessary
- Follow doctor's instructions carefully
- Wash hands regularly
- Keep up with vaccinations

⚠️ **Note**: Consult an infectious disease specialist for current information."""

            else:
                return f"""Hello! I'm a medical assistant specializing in antibiotics and infectious diseases.

I can help you with:
- Information about antibiotics and how they work
- Explanation of bacterial resistance patterns
- Preventive advice to reduce infection spread
- General information about common infectious diseases

{context_text}

⚠️ **Important**: This is general educational information only. I am not a substitute for professional medical advice. Please consult a healthcare professional for any health concerns."""

    def _get_relevant_data(self, query_lower: str) -> Dict[str, Any]:
        """Fetch relevant data from the API based on query"""
        import requests

        base_url = "http://localhost:8000/api"

        # Get authentication token
        try:
            # This is a simplified approach - in production, you'd get the token from the request
            # For now, we'll try to fetch public data or use a service account
            headers = {}

            # Determine what data to fetch based on query
            if any(word in query_lower for word in ['highest', 'section', 'department', 'resistance']):
                # Fetch stats and department data
                stats_response = requests.get(f"{base_url}/stats/", headers=headers, timeout=5)
                dept_response = requests.get(f"{base_url}/departments-list/", headers=headers, timeout=5)

                if stats_response.status_code == 200 and dept_response.status_code == 200:
                    stats_data = stats_response.json()
                    dept_data = dept_response.json()
                    return {
                        'type': 'department_resistance',
                        'stats': stats_data,
                        'departments': dept_data
                    }

            elif any(word in query_lower for word in ['effective', 'best', 'antibiotic']):
                # Fetch antibiotic effectiveness data
                effectiveness_response = requests.get(f"{base_url}/antibiotic-effectiveness/", headers=headers, timeout=5)
                if effectiveness_response.status_code == 200:
                    return {
                        'type': 'antibiotic_effectiveness',
                        'data': effectiveness_response.json()
                    }

            elif any(word in query_lower for word in ['trend', 'over time', 'change']):
                # Fetch resistance over time data
                time_response = requests.get(f"{base_url}/resistance-over-time/", headers=headers, timeout=5)
                if time_response.status_code == 200:
                    return {
                        'type': 'resistance_trends',
                        'data': time_response.json()
                    }

        except Exception as e:
            print(f"Error fetching API data: {e}")

        return None

    def _format_data_response(self, query_lower: str, data: Dict[str, Any], language: str) -> str:
        """Format API data into a readable response"""
        try:
            if data['type'] == 'department_resistance':
                return self._format_department_resistance(data, language)
            elif data['type'] == 'antibiotic_effectiveness':
                return self._format_antibiotic_effectiveness(data, language)
            elif data['type'] == 'resistance_trends':
                return self._format_resistance_trends(data, language)
        except Exception as e:
            print(f"Error formatting response: {e}")

        return self.generate_response("general", [])  # Fallback

    def _format_department_resistance(self, data: Dict[str, Any], language: str) -> str:
        """Format department resistance data"""
        stats = data.get('stats', {})
        departments = data.get('departments', [])

        # Find department with highest resistance (simplified logic)
        dept_resistance = {}
        for dept in departments:
            dept_name = dept.get('name', '')
            # This is a simplified calculation - in reality you'd need more complex logic
            dept_resistance[dept_name] = stats.get('total_samples', 0)

        if dept_resistance:
            highest_dept = max(dept_resistance.items(), key=lambda x: x[1])

            if language == 'ar':
                return f"""بناءً على البيانات المتاحة في قاعدة البيانات:

**القسم الأعلى في مقاومة المضادات الحيوية:**
- {highest_dept[0]}: {highest_dept[1]} عينة

**إحصائيات عامة:**
- إجمالي العينات: {stats.get('total_samples', 0)}
- إجمالي البكتيريا: {stats.get('total_bacteria', 0)}

⚠️ **ملاحظة**: هذه البيانات تعتمد على العينات المتاحة وقد تختلف حسب الفترة الزمنية والعينات المحددة."""
            else:
                return f"""Based on the available data in the database:

**Department with Highest Antibiotic Resistance:**
- {highest_dept[0]}: {highest_dept[1]} samples

**General Statistics:**
- Total Samples: {stats.get('total_samples', 0)}
- Total Bacteria: {stats.get('total_bacteria', 0)}

⚠️ **Note**: This data is based on available samples and may vary depending on the time period and specific samples."""

        return self.generate_response("resistance", [])

    def _format_antibiotic_effectiveness(self, data: Dict[str, Any], language: str) -> str:
        """Format antibiotic effectiveness data"""
        effectiveness_data = data.get('data', [])

        if effectiveness_data:
            # Find most effective antibiotic (simplified)
            most_effective = max(effectiveness_data, key=lambda x: x.get('effectiveness', 0))

            if language == 'ar':
                return f"""بناءً على بيانات الفعالية المتاحة:

**أكثر المضادات الحيوية فعالية:**
- {most_effective.get('antibiotic', 'غير محدد')}: فعالية {most_effective.get('effectiveness', 0)}%

**نصائح مهمة:**
- اختيار المضاد الحيوي يعتمد على نوع البكتيريا والحالة المرضية
- يجب إجراء اختبارات حساسية قبل البدء بالعلاج
- استشر طبيبك دائماً لاختيار العلاج المناسب

⚠️ **تحذير**: هذه معلومات إحصائية عامة وليست نصيحة علاجية."""
            else:
                return f"""Based on available effectiveness data:

**Most Effective Antibiotic:**
- {most_effective.get('antibiotic', 'Unknown')}: {most_effective.get('effectiveness', 0)}% effectiveness

**Important Notes:**
- Antibiotic selection depends on the type of bacteria and medical condition
- Sensitivity tests should be performed before starting treatment
- Always consult your doctor for appropriate treatment selection

⚠️ **Warning**: This is general statistical information and not treatment advice."""

        return self.generate_response("antibiotic", [])

    def _format_resistance_trends(self, data: Dict[str, Any], language: str) -> str:
        """Format resistance trends data"""
        trends_data = data.get('data', [])

        if trends_data:
            # Calculate trend (simplified)
            if len(trends_data) >= 2:
                latest = trends_data[-1].get('resistance_rate', 0)
                previous = trends_data[-2].get('resistance_rate', 0)
                trend = "increasing" if latest > previous else "decreasing" if latest < previous else "stable"

                if language == 'ar':
                    return f"""اتجاهات مقاومة المضادات الحيوية بناءً على البيانات الزمنية:

**الاتجاه الحالي:** المقاومة {"في ارتفاع" if trend == "increasing" else "في انخفاض" if trend == "decreasing" else "مستقرة"}

**معدل المقاومة الأخير:** {latest}%
**معدل المقاومة السابق:** {previous}%

**أسباب محتملة للتغيير:**
- تغييرات في استخدام المضادات الحيوية
- انتشار سلالات بكتيرية مقاومة جديدة
- تحسينات في السيطرة على العدوى

⚠️ **تنبيه**: هذه اتجاهات عامة وقد تختلف حسب النوع البكتيري والمضاد الحيوي."""
                else:
                    return f"""Antibiotic resistance trends based on time-series data:

**Current Trend:** Resistance is {"increasing" if trend == "increasing" else "decreasing" if trend == "decreasing" else "stable"}

**Latest Resistance Rate:** {latest}%
**Previous Resistance Rate:** {previous}%

**Possible Reasons for Change:**
- Changes in antibiotic usage patterns
- Spread of new resistant bacterial strains
- Improvements in infection control

⚠️ **Note**: These are general trends and may vary by bacterial type and antibiotic."""

        return self.generate_response("resistance", [])

    def detect_phi(self, text: str) -> bool:
        """Detect Protected Health Information (PHI)"""
        phi_patterns = [
            r'\b\d{10,15}\b',  # Phone numbers
            r'\b\d{9,12}\b',   # Patient IDs
            r'\b[A-Z]{2,3}\d{6,10}\b',  # Medical IDs
            r'\b\d{2}/\d{2}/\d{4}\b',  # Dates
            r'\b\d{4}-\d{2}-\d{2}\b',  # ISO dates
        ]

        for pattern in phi_patterns:
            if re.search(pattern, text):
                return True
        return False

    def anonymize_text(self, text: str) -> str:
        """Anonymize PHI in text"""
        # Replace potential PHI with placeholders
        text = re.sub(r'\b\d{10,15}\b', '[رقم هاتف]', text)
        text = re.sub(r'\b\d{9,12}\b', '[رقم تعريف]', text)
        text = re.sub(r'\b[A-Z]{2,3}\d{6,10}\b', '[رمز طبي]', text)
        text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', '[تاريخ]', text)
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[تاريخ]', text)
        return text

    def populate_knowledge_base_from_excel(self, file_path: str):
        """Populate knowledge base from Excel file"""
        try:
            df = pd.read_excel(file_path)
            content = f"بيانات من ملف {os.path.basename(file_path)}:\n\n"

            # Convert DataFrame to text
            for col in df.columns:
                content += f"عمود {col}: {', '.join(df[col].astype(str).unique()[:10])}\n"

            # Chunk the content
            chunks = self._chunk_text(content, 1000)

            for chunk in chunks:
                embedding = self.embedding_model.encode(chunk).tolist() if self.embedding_model else []
                KnowledgeBase.objects.create(
                    content=chunk,
                    source=os.path.basename(file_path),
                    embedding=embedding,
                    metadata={'type': 'excel', 'file': file_path}
                )

        except Exception as e:
            print(f"Error processing Excel file: {e}")

    def populate_knowledge_base_from_text(self, content: str, source: str):
        """Populate knowledge base from text content"""
        chunks = self._chunk_text(content, 1000)

        for chunk in chunks:
            embedding = self.embedding_model.encode(chunk).tolist() if self.embedding_model else []
            KnowledgeBase.objects.create(
                content=chunk,
                source=source,
                embedding=embedding,
                metadata={'type': 'text', 'source': source}
            )

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) > chunk_size:
                chunks.append(' '.join(current_chunk[:-1]))
                current_chunk = [word]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _initialize_data_knowledge(self):
        """Initialize knowledge about data structure and rules"""
        self.data_rules = {
            'models': {
                'Sample': {
                    'fields': ['patient_id', 'bacteria', 'hospital', 'department', 'date', 'created_by'],
                    'relationships': ['bacteria (ForeignKey)', 'created_by (ForeignKey to User)'],
                    'constraints': ['patient_id is unique per hospital', 'date cannot be future']
                },
                'Bacteria': {
                    'fields': ['name', 'bacteria_type', 'gram_stain', 'source', 'notes'],
                    'types': ['gram_positive', 'gram_negative'],
                    'constraints': ['name must be unique']
                },
                'Antibiotic': {
                    'fields': ['name', 'class', 'spectrum', 'route', 'notes'],
                    'constraints': ['name must be unique']
                },
                'TestResult': {
                    'fields': ['sample', 'antibiotic', 'sensitivity', 'mic_value', 'zone_diameter', 'notes'],
                    'sensitivity_options': ['sensitive', 'intermediate', 'resistant'],
                    'constraints': ['unique_together (sample, antibiotic)', 'mic_value and zone_diameter are optional']
                }
            },
            'business_rules': {
                'antibiogram_minimum': 'Minimum 30 isolates per organism for valid antibiogram (CLSI guideline)',
                'interpretation': {
                    'sensitive': 'Bacteria inhibited by antibiotic at achievable concentrations',
                    'intermediate': 'Bacteria inhibited at higher than normal concentrations',
                    'resistant': 'Bacteria not inhibited by achievable antibiotic concentrations'
                },
                'quality_control': 'All results must be reviewed by qualified microbiologist',
                'data_retention': 'Clinical data retained for minimum 7 years per regulatory requirements'
            },
            'analysis_rules': {
                'resistance_calculation': 'Resistance rate = (resistant isolates / total isolates) × 100',
                'trend_analysis': 'Compare resistance rates over time periods (monthly/quarterly)',
                'department_comparison': 'Analyze resistance patterns by hospital department',
                'outbreak_detection': 'Unusual increase >2 standard deviations from baseline'
            }
        }

    def analyze_data_rules(self, query: str) -> str:
        """Analyze and explain data rules based on query"""
        query_lower = query.lower()
        language = self.detect_language(query)

        # Data structure questions
        if any(word in query_lower for word in ['structure', 'schema', 'model', 'table', 'field']):
            return self._explain_data_structure(language)

        # Business rules questions
        elif any(word in query_lower for word in ['rule', 'constraint', 'validation', 'requirement']):
            return self._explain_business_rules(language)

        # Analysis questions
        elif any(word in query_lower for word in ['calculate', 'formula', 'analysis', 'method']):
            return self._explain_analysis_methods(language)

        # Quality and compliance
        elif any(word in query_lower for word in ['quality', 'compliance', 'regulation', 'standard']):
            return self._explain_quality_standards(language)

        return None

    def _explain_data_structure(self, language: str) -> str:
        """Explain the data structure"""
        if language == 'ar':
            return """## هيكل قاعدة البيانات في نظام مكافحة المقاومة

### النماذج الرئيسية:

**1. Sample (العينة)**
- **الحقول**: patient_id, bacteria, hospital, department, date, created_by
- **العلاقات**: bacteria (ForeignKey), created_by (ForeignKey إلى User)
- **القيود**: patient_id فريد لكل مستشفى، التاريخ لا يمكن أن يكون في المستقبل

**2. Bacteria (البكتيريا)**
- **الحقول**: name, bacteria_type, gram_stain, source, notes
- **الأنواع**: gram_positive, gram_negative
- **القيود**: الاسم يجب أن يكون فريداً

**3. Antibiotic (المضاد الحيوي)**
- **الحقول**: name, class, spectrum, route, notes
- **القيود**: الاسم يجب أن يكون فريداً

**4. TestResult (نتيجة الاختبار)**
- **الحقول**: sample, antibiotic, sensitivity, mic_value, zone_diameter, notes
- **خيارات الحساسية**: sensitive, intermediate, resistant
- **القيود**: unique_together (sample, antibiotic)، mic_value و zone_diameter اختياريان

### العلاقات:
- Sample ← TestResult → Antibiotic
- Sample → Bacteria
- Sample → User (created_by)"""
        else:
            return """## Database Structure in Antimicrobial Resistance System

### Main Models:

**1. Sample**
- **Fields**: patient_id, bacteria, hospital, department, date, created_by
- **Relationships**: bacteria (ForeignKey), created_by (ForeignKey to User)
- **Constraints**: patient_id unique per hospital, date cannot be future

**2. Bacteria**
- **Fields**: name, bacteria_type, gram_stain, source, notes
- **Types**: gram_positive, gram_negative
- **Constraints**: name must be unique

**3. Antibiotic**
- **Fields**: name, class, spectrum, route, notes
- **Constraints**: name must be unique

**4. TestResult**
- **Fields**: sample, antibiotic, sensitivity, mic_value, zone_diameter, notes
- **Sensitivity Options**: sensitive, intermediate, resistant
- **Constraints**: unique_together (sample, antibiotic), mic_value and zone_diameter are optional

### Relationships:
- Sample ← TestResult → Antibiotic
- Sample → Bacteria
- Sample → User (created_by)"""

    def _explain_business_rules(self, language: str) -> str:
        """Explain business rules and constraints"""
        if language == 'ar':
            return """## قواعد العمل والقيود

### قواعد الجودة:
- **الحد الأدنى للأنتيبيوغرام**: 30 عزلة كحد أدنى لكل كائن حي للحصول على نتائج صحيحة (إرشادات CLSI)
- **جميع النتائج يجب مراجعتها** من قبل أخصائي ميكروبيولوجيا معتمد

### تفسير النتائج:
- **Sensitive (حساس)**: البكتيريا تُثبط بواسطة المضاد الحيوي عند التركيزات القابلة للتحقيق
- **Intermediate (متوسط)**: البكتيريا تُثبط عند تركيزات أعلى من المعتاد
- **Resistant (مقاوم)**: البكتيريا لا تُثبط عند التركيزات القابلة للتحقيق

### قواعد الاحتفاظ بالبيانات:
- **البيانات السريرية**: محفوظة لمدة 7 سنوات كحد أدنى حسب المتطلبات التنظيمية
- **البيانات الإدارية**: محفوظة لمدة 10 سنوات

### قيود الجودة:
- **MIC values**: يجب أن تكون في النطاق المعملي المعتمد
- **Zone diameters**: يجب التحقق من صحة قراءات القرص
- **Duplicate testing**: غير مسموح لنفس العينة-المضاد الحيوي"""
        else:
            return """## Business Rules and Constraints

### Quality Rules:
- **Antibiogram Minimum**: Minimum 30 isolates per organism for valid results (CLSI guideline)
- **All results must be reviewed** by qualified microbiologist

### Result Interpretation:
- **Sensitive**: Bacteria inhibited by antibiotic at achievable concentrations
- **Intermediate**: Bacteria inhibited at higher than normal concentrations
- **Resistant**: Bacteria not inhibited by achievable antibiotic concentrations

### Data Retention Rules:
- **Clinical Data**: Retained for minimum 7 years per regulatory requirements
- **Administrative Data**: Retained for 10 years

### Quality Constraints:
- **MIC values**: Must be within laboratory-approved range
- **Zone diameters**: Disk readings must be validated
- **Duplicate testing**: Not allowed for same sample-antibiotic combination"""

    def _explain_analysis_methods(self, language: str) -> str:
        """Explain data analysis methods"""
        if language == 'ar':
            return """## طرق التحليل والحسابات

### حساب معدلات المقاومة:
```
معدل المقاومة = (عدد العزلات المقاومة / إجمالي العزلات) × 100
```

### تحليل الاتجاهات:
- **مقارنة معدلات المقاومة** خلال الفترات الزمنية (شهرياً/ربع سنوياً)
- **تحليل الانحدار** للكشف عن الاتجاهات طويلة الأمد
- **مقارنة مع الخط الأساسي** للكشف عن التغييرات

### تحليل الأقسام:
- **مقارنة أنماط المقاومة** حسب قسم المستشفى
- **تحديد الأقسام عالية الخطورة** للمقاومة
- **تتبع التغييرات** حسب القسم مع مرور الوقت

### كشف التفشيات:
- **زيادة غير عادية**: >2 انحراف معياري عن الخط الأساسي
- **التجميع الزمني**: عدوى متعددة في فترة قصيرة
- **التجميع المكاني**: عدوى في نفس القسم أو المنطقة

### مؤشرات الأداء الرئيسية:
- **معدل استخدام المضادات الحيوية** (AUR)
- **معدل الوصول للعلاج المناسب** خلال 72 ساعة
- **معدل الخفض** من العلاج التجريبي
- **معدل الامتثال** لمدة العلاج"""
        else:
            return """## Analysis Methods and Calculations

### Resistance Rate Calculation:
```
Resistance Rate = (Resistant Isolates / Total Isolates) × 100
```

### Trend Analysis:
- **Compare resistance rates** across time periods (monthly/quarterly)
- **Regression analysis** to detect long-term trends
- **Baseline comparison** to identify changes

### Department Analysis:
- **Compare resistance patterns** by hospital department
- **Identify high-risk departments** for resistance
- **Track changes** by department over time

### Outbreak Detection:
- **Unusual increase**: >2 standard deviations from baseline
- **Temporal clustering**: Multiple infections in short period
- **Spatial clustering**: Infections in same department/area

### Key Performance Indicators:
- **Antibiotic Utilization Rate** (AUR)
- **Appropriate therapy attainment** within 72 hours
- **De-escalation rate** from empiric therapy
- **Duration compliance** rate"""

    def _explain_quality_standards(self, language: str) -> str:
        """Explain quality standards and compliance"""
        if language == 'ar':
            return """## معايير الجودة والامتثال

### معايير CLSI (الكلية الأمريكية لعلم الأحياء السريرية):
- **الحد الأدنى للعزلات**: 30 عزلة لكل كائن حي للأنتيبيوغرام الصحيح
- **اختبارات التحكم النوعي**: يومياً لجميع الأجهزة والأقراص
- **معايرة الأجهزة**: حسب الجدول الزمني المعتمد
- **تدريب الموظفين**: سنوياً على الإجراءات والسلامة

### معايير CAP (كلية الأمريكية لعلم الأمراض):
- **الدقة**: ±1 dilution لقيم MIC
- **الدقة**: ±2mm لقياسات منطقة التثبيط
- **الاستمرارية**: اختبارات التحكم النوعي ≥95% نجاح
- **التوثيق**: جميع النتائج والإجراءات موثقة

### الامتثال التنظيمي:
- **الاحتفاظ بالسجلات**: 7 سنوات للبيانات السريرية
- **الإبلاغ**: تقارير شهرية للمقاومة
- **التدقيق**: مراجعات داخلية ربع سنوية
- **الاعتماد**: اعتماد المعمل كل 2 سنوات

### مراقبة الجودة المستمرة:
- **مخططات سيوارت**: لمراقبة الاتجاهات
- **قواعد ويستغارد**: للكشف عن الأخطاء
- **تحليل الاتجاهات**: شهرياً للكشف عن المشاكل
- **مقارنة الأداء**: مع المعايير الوطنية"""
        else:
            return """## Quality Standards and Compliance

### CLSI Standards (Clinical Laboratory Standards Institute):
- **Minimum Isolates**: 30 isolates per organism for valid antibiogram
- **Quality Control**: Daily testing of all instruments and disks
- **Equipment Calibration**: According to approved schedule
- **Staff Training**: Annual training on procedures and safety

### CAP Standards (College of American Pathologists):
- **Accuracy**: ±1 dilution for MIC values
- **Precision**: ±2mm for zone diameter measurements
- **Consistency**: QC testing ≥95% success rate
- **Documentation**: All results and procedures documented

### Regulatory Compliance:
- **Record Retention**: 7 years for clinical data
- **Reporting**: Monthly resistance reports
- **Auditing**: Quarterly internal reviews
- **Accreditation**: Laboratory accreditation every 2 years

### Continuous Quality Monitoring:
- **Levey-Jennings Charts**: For trend monitoring
- **Westgard Rules**: For error detection
- **Trend Analysis**: Monthly analysis for problem detection
- **Performance Comparison**: Against national standards"""
