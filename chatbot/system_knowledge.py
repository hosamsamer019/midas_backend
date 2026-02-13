"""
Comprehensive System Knowledge for AI Medical Assistant
This file contains all the knowledge about the antibiogram system,
medical procedures, bacteria, antibiotics, and user guidance.
"""

SYSTEM_KNOWLEDGE = """
# نظام تحليل المقاومة البكتيرية - مستشفى المنصورة الجامعي

## نظرة عامة على النظام
نظام متكامل لتحليل وإدارة بيانات المقاومة البكتيرية للمضادات الحيوية في المستشفى.

## صفحات النظام الرئيسية:
1. Dashboard - لوحة التحكم الرئيسية
2. Heatmap - خريطة الحرارة للمقاومة
3. Sensitivity Distribution - توزيع الحساسية
4. Resistance Over Time - المقاومة عبر الزمن
5. Samples Management - إدارة العينات
6. Test Results - نتائج الاختبارات
7. Reports - التقارير
8. Upload Data - رفع البيانات

## البكتيريا الشائعة:
- Staphylococcus aureus (MRSA)
- Escherichia coli (E. coli)
- Klebsiella pneumoniae
- Pseudomonas aeruginosa
- Acinetobacter baumannii

## المضادات الحيوية الرئيسية:
- Vancomycin
- Meropenem
- Ciprofloxacin
- Ceftriaxone
- Piperacillin-Tazobactam

## الإجراءات الطبية:
- MIC Testing
- CLSI Standards
- Antibiogram Reports

**تنبيه مهم**: هذا النظام للمساعدة فقط وليس بديلاً عن الاستشارة الطبية المتخصصة.
"""


def get_system_knowledge():
    """Return the complete system knowledge"""
    return SYSTEM_KNOWLEDGE


def get_bacteria_info(bacteria_name: str) -> str:
    """Get specific information about a bacteria"""
    bacteria_sections = {
        'staphylococcus aureus': """
**Staphylococcus aureus**
- بكتيريا موجبة الجرام كروية الشكل
- تسبب التهابات جلدية، تسمم دموي، التهاب شغاف
- MRSA مقاوم للميثيسيلين - مشكلة كبيرة في المستشفيات
- العلاج: Vancomycin, Linezolid, Daptomycin
        """,
        'escherichia coli': """
**Escherichia coli (E. coli)**
- بكتيريا سالبة الجرام عصوية الشكل
- أكثر أسباب التهابات المسالك البولية شيوعاً
- ESBL شائع - يتطلب Carbapenems
- العلاج: Nitrofurantoin, Ciprofloxacin, Ceftriaxone, Meropenem
        """,
        'klebsiella pneumoniae': """
**Klebsiella pneumoniae**
- بكتيريا سالبة الجرام عصوية
- سبب رئيسي للالتهاب الرئوي المكتسب من المستشفى
- KPC (مقاومة للكاربابينيم) خطير جداً
- العلاج: Ceftriaxone, Meropenem, Colistin, Tigecycline
        """,
        'pseudomonas aeruginosa': """
**Pseudomonas aeruginosa**
- بكتيريا سالبة الجرام عصوية
- مقاومة طبيعية للعديد من المضادات
- شائع في مرضى التنفس الصناعي والحروق
- العلاج: Piperacillin-Tazobactam, Ceftazidime, Meropenem, Ciprofloxacin
        """,
        'acinetobacter baumannii': """
**Acinetobacter baumannii**
- بكتيريا سالبة الجرام عصوية
- مشكلة كبيرة في وحدات العناية المركزة
- مقاومة شديدة للمضادات الحيوية
- العلاج: Colistin, Tigecycline, Ampicillin-Sulbactam
        """,
        'aeromonas hydrophila': """
**Aeromonas hydrophila**
- بكتيريا سالبة الجرام عصوية
- تسبب التهابات في الجروح، الإسهال، التهابات الدم
- شائعة في المياه الملوثة والأسماك
- العلاج: Ciprofloxacin, Ceftriaxone, Trimethoprim-Sulfamethoxazole
- ملاحظة: مقاومة للأمبيسيلين والكلورامفينيكول
        """
    }
    
    bacteria_lower = bacteria_name.lower()
    for key, info in bacteria_sections.items():
        if key in bacteria_lower or bacteria_lower in key:
            return info
    
    return f"معلومات عن {bacteria_name} غير متوفرة حالياً في قاعدة المعرفة."


def get_antibiotic_info(antibiotic_name: str) -> str:
    """Get specific information about an antibiotic"""
    antibiotic_sections = {
        'vancomycin': """
**Vancomycin (فانكومايسين)**
- الفئة: Glycopeptide
- الطيف: بكتيريا موجبة الجرام فقط
- الاستخدام الرئيسي: MRSA, التهاب شغاف
- الجرعة: 15-20 mg/kg كل 8-12 ساعة
- المراقبة: مستويات الدواء في الدم (Trough 15-20 μg/mL)
- الآثار الجانبية: سمية كلوية، سمية سمعية
        """,
        'meropenem': """
**Meropenem (ميروبينيم)**
- الفئة: Carbapenem
- الطيف: واسع جداً (موجبة وسالبة الجرام)
- الاستخدام: عدوى شديدة، ESBL
- الجرعة: 1-2 جرام كل 8 ساعات
- ملاحظة: مضاد حيوي الخط الأخير
- الآثار الجانبية: نوبات صرع (جرعات عالية)
        """,
        'ciprofloxacin': """
**Ciprofloxacin (سيبروفلوكساسين)**
- الفئة: Fluoroquinolone
- الطيف: واسع (خاصة سالبة الجرام)
- الاستخدام: التهابات مسالك بولية، جهاز تنفسي
- الجرعة: 400 mg IV كل 12 ساعة أو 500-750 mg فموي
- موانع: الحمل، الأطفال، تاريخ تمزق أوتار
- الآثار الجانبية: تمزق الأوتار، اضطرابات هضمية
        """,
        'ceftriaxone': """
**Ceftriaxone (سيفترياكسون)**
- الفئة: Cephalosporin (الجيل الثالث)
- الطيف: واسع (خاصة سالبة الجرام)
- الاستخدام: التهاب رئوي، سحايا، تسمم دم
- الجرعة: 1-2 جرام كل 12-24 ساعة
- ميزة: جرعة واحدة يومياً
- الآثار الجانبية: إسهال، طفح جلدي
        """
    }
    
    antibiotic_lower = antibiotic_name.lower()
    for key, info in antibiotic_sections.items():
        if key in antibiotic_lower or antibiotic_lower in key:
            return info
    
    return f"معلومات عن {antibiotic_name} غير متوفرة حالياً في قاعدة المعرفة."


def get_procedure_info(procedure_name: str) -> str:
    """Get information about medical procedures"""
    procedures = {
        'mic': """
**MIC (Minimum Inhibitory Concentration)**
- التعريف: أقل تركيز من المضاد الحيوي يثبط نمو البكتيريا
- الطرق: Broth dilution, E-test, Automated systems
- التفسير: MIC منخفض = حساس، MIC مرتفع = مقاوم
- الأهمية: أدق من طريقة القرص
        """,
        'clsi': """
**CLSI (Clinical and Laboratory Standards Institute)**
- منظمة دولية تضع معايير تفسير نتائج الحساسية
- تصدر تحديثات سنوية (M100)
- تحدد نقاط القطع (Breakpoints)
- يجب متابعة أحدث المعايير
        """,
        'antibiogram': """
**Antibiogram (الأنتيبيوغرام)**
- تقرير سنوي يلخص أنماط الحساسية في المستشفى
- يتطلب 30 عزلة على الأقل لكل بكتيريا
- يستخدم لاختيار العلاج التجريبي
- يساعد في مراقبة المقاومة
        """
    }
    
    procedure_lower = procedure_name.lower()
    for key, info in procedures.items():
        if key in procedure_lower:
            return info
    
    return "معلومات عن هذا الإجراء غير متوفرة حالياً."
