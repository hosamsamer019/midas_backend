# Working with and Testing the Unified Data Processing Layer

## Overview

This document provides comprehensive steps for working with and testing the various components of the antibiogram analysis system, which has been redesigned with a Unified Data Processing Layer to address core issues:

- **Case sensitivity** in element names (e.g., "Klebsiella" vs. "klebsiella")
- **Partial dataset reliance** (e.g., only 1-3 elements analyzed)
- **Lack of central filtering** and inconsistent data reading
- **Fragmented architecture** with no global control

The Unified Data Processing Layer ensures all sections (Data Filters, Generate Reports, Resistance Heatmap, AI Antibiotic Recommendations, Database-Based Antibiotic Recommendations) interface only with this layer, providing consistent, normalized, and full-dataset analysis.

## Unified Data Processing Layer Architecture

### Core Components

1. **Normalization Layer** (`core/data_normalization.py`)
   - Text normalization (lowercase, trim spaces)
   - Case-insensitive queries
   - Duplicate detection and merging

2. **Master Data Manager** (`core/master_data.py`)
   - Canonical name management
   - Alias handling for bacteria/antibiotics
   - Duplicate merging utilities

3. **Global Filter Engine** (`core/filters.py`)
   - Centralized filtering logic
   - Supports: date range, bacteria, department, antibiotic, sensitivity, hospital

4. **Unified Data Service** (`core/data_service.py`)
   - Single point of data access
   - Methods for statistics, heatmaps, recommendations, etc.
   - Ensures full dataset utilization

### Key Principles

- **No Direct Database Access**: All sections use the unified service
- **Case-Insensitive Operations**: All queries normalize input
- **Full Dataset Analysis**: AI and recommendations analyze all available data
- **Consistent Filtering**: Same filters apply across all sections

## 1. Data Filters Section

### Working with Data Filters

**Purpose**: Provides user interface for specifying search criteria (date range, bacteria, department, antibiotic) to customize all subsequent analyses.

**API Integration**:
```python
# In views.py or frontend API calls
from core.filters import create_filter_engine
from core.data_service import create_data_service

def data_filters_view(request):
    # Create filter engine from request parameters
    filter_engine = create_filter_engine(request.GET)

    # Create data service with filters applied
    data_service = create_data_service(request)

    # Get filtered results summary
    summary = filter_engine.get_filter_summary()
    results_count = data_service.get_filtered_results().count()

    return Response({
        'active_filters': summary,
        'results_count': results_count,
        'available_bacteria': data_service.get_bacteria_list(),
        'available_departments': data_service.get_department_list(),
        'available_antibiotics': data_service.get_antibiotic_list()
    })
```

**Frontend Usage**:
```javascript
// Example API call with filters
const response = await fetch('/api/data-filters/?date_from=2024-01-01&date_to=2024-12-31&bacteria=E.%20coli&department=ICU');
const data = await response.json();

// Display active filters and results count
console.log('Active Filters:', data.active_filters);
console.log('Results Count:', data.results_count);
```

### Testing Data Filters

**Manual Testing Steps**:
1. Access the data filters interface
2. Select date range (e.g., 2024-01-01 to 2024-12-31)
3. Choose bacteria (e.g., "Klebsiella" - verify case-insensitive)
4. Select department (e.g., "ICU")
5. Optionally select antibiotic
6. Click "Search"
7. Verify:
   - Results count updates
   - Active filters display correctly
   - No errors with case variations

**Automated Testing**:
```python
# test_data_filters.py
import pytest
from core.filters import GlobalFilterEngine
from core.data_service import UnifiedDataService

def test_case_insensitive_bacteria_filter():
    engine = GlobalFilterEngine({'bacteria': 'KLEBSIELLA'})
    results = engine.apply_to_test_results(TestResult.objects.all())
    # Should match 'Klebsiella', 'klebsiella', etc.
    assert results.filter(bacteria__name__iexact='klebsiella').exists()

def test_filter_consistency():
    # Same filters should produce same results across sections
    filters = {'bacteria': 'E. coli', 'date_from': '2024-01-01'}
    service1 = UnifiedDataService(filters)
    service2 = UnifiedDataService(filters)

    stats1 = service1.get_statistics()
    stats2 = service2.get_statistics()
    assert stats1 == stats2
```

## 2. Generate Reports Section

### Working with Report Generation

**Purpose**: Creates unified reports with graphs, trends, and AI-interpreted insights based on filtered data.

**API Integration**:
```python
# api/views.py - ReportView
from core.data_service import create_data_service
from core.filters import create_filter_engine

class ReportView(APIView):
    def get(self, request):
        data_service = create_data_service(request)
        filter_engine = create_filter_engine(request.GET)

        # Generate comprehensive report
        report_data = {
            'statistics': data_service.get_statistics(),
            'resistance_trends': data_service.get_resistance_over_time(),
            'heatmap_data': data_service.get_resistance_heatmap(),
            'ai_insights': data_service.get_ai_insights(),  # Uses Gemma 3:4B
            'filter_summary': filter_engine.get_filter_summary()
        }

        # Generate PDF/Excel if requested
        if request.GET.get('format') == 'pdf':
            return generate_pdf_report(report_data)
        elif request.GET.get('format') == 'excel':
            return generate_excel_report(report_data)

        return Response(report_data)
```

**Report Generation Functions**:
```python
def generate_pdf_report(data):
    # Use reportlab or similar for PDF generation
    from reportlab.pdfgen import canvas
    # Include charts, tables, AI insights
    pass

def generate_excel_report(data):
    # Use openpyxl for Excel generation
    from openpyxl import Workbook
    # Create worksheets for different data sections
    pass
```

### Testing Report Generation

**Manual Testing Steps**:
1. Navigate to report generation section
2. Apply filters (date range, bacteria, department, antibiotic)
3. Generate report in different formats (PDF, Excel, HTML)
4. Verify:
   - Report reflects applied filters
   - Charts and graphs display correctly
   - AI insights are medically relevant
   - No case sensitivity issues
   - Data matches other sections with same filters

**Automated Testing**:
```python
def test_report_consistency():
    filters = {'bacteria': 'Klebsiella', 'department': 'ICU'}
    service = UnifiedDataService(filters)

    # Generate report data
    report = service.generate_report()

    # Verify data matches filtered results
    filtered_count = service.get_filtered_results().count()
    assert report['total_samples'] == filtered_count

def test_ai_insights_in_reports():
    # Test that AI provides meaningful insights
    service = UnifiedDataService({'bacteria': 'MRSA'})
    insights = service.get_ai_insights()

    assert 'recommendation' in insights
    assert 'resistance_pattern' in insights
    assert len(insights['medical_notes']) > 0
```

## 3. Resistance Heatmap Section

### Working with Resistance Heatmap

**Purpose**: Displays resistance patterns with accurate, unified data (no case sensitivity issues).

**API Integration**:
```python
# api/views.py - ResistanceHeatmapView
class ResistanceHeatmapView(APIView):
    def get(self, request):
        data_service = create_data_service(request)

        # Get normalized heatmap data
        heatmap_data = data_service.get_resistance_heatmap()

        # Structure for frontend visualization
        return Response({
            'bacteria': heatmap_data['bacteria'],  # Normalized names
            'antibiotics': heatmap_data['antibiotics'],  # Normalized names
            'resistance_matrix': heatmap_data['matrix'],
            'filter_summary': data_service.filter_engine.get_filter_summary()
        })
```

**Normalization in Heatmap**:
```python
# core/data_service.py
def get_resistance_heatmap(self):
    # Use normalized queries
    results = self.get_filtered_results()

    # Group by normalized bacteria and antibiotic names
    heatmap = {}
    for result in results:
        bacteria_key = normalize_bacteria_name(result.bacteria.name)
        antibiotic_key = normalize_antibiotic_name(result.antibiotic.name)

        if bacteria_key not in heatmap:
            heatmap[bacteria_key] = {}
        heatmap[bacteria_key][antibiotic_key] = result.resistance_value

    return heatmap
```

### Testing Resistance Heatmap

**Manual Testing Steps**:
1. Access resistance heatmap
2. Apply filters
3. Verify:
   - Case variations of bacteria names are consolidated
   - Heatmap shows unified data (no duplicate entries)
   - Filtering works correctly
   - Visual representation is accurate

**Automated Testing**:
```python
def test_heatmap_normalization():
    # Create test data with case variations
    TestResult.objects.create(bacteria='Klebsiella', antibiotic='Amoxicillin', resistance=0.8)
    TestResult.objects.create(bacteria='klebsiella', antibiotic='amoxicillin', resistance=0.8)
    TestResult.objects.create(bacteria='KLEBSIELLA', antibiotic='AMOXICILLIN', resistance=0.8)

    service = UnifiedDataService()
    heatmap = service.get_resistance_heatmap()

    # Should have only one entry for each normalized name
    assert len(heatmap) == 1  # Only 'klebsiella'
    assert 'klebsiella' in heatmap
    assert 'amoxicillin' in heatmap['klebsiella']
```

## 4. AI Antibiotic Recommendations Section

### Working with AI Recommendations

**Purpose**: Provides intelligent antibiotic recommendations using Gemma 3:4B, analyzing full datasets with medical insights.

**Integration with Gemma 3:4B**:
```python
# ai_engine/gemma_service.py
from chatbot.utils_localai import query_localai

class GemmaAIService:
    def __init__(self):
        self.model = "gemma:3b"  # or appropriate model name

    def get_recommendations(self, bacteria, full_dataset, filters):
        prompt = f"""
        Analyze the following antibiogram data for {bacteria}:

        Full Dataset: {full_dataset}
        Applied Filters: {filters}

        Provide:
        1. Best antibiotic recommendations
        2. Resistance patterns explanation
        3. MDR/XDR risk assessment
        4. Medical notes and rationale

        Consider all available antibiotics, not just a subset.
        """

        response = query_localai(prompt, model=self.model)
        return self.parse_ai_response(response)
```

**API Integration**:
```python
# api/views.py - AIPredictView
class AIPredictView(APIView):
    def get(self, request):
        data_service = create_data_service(request)
        ai_service = GemmaAIService()

        bacteria = request.GET.get('bacteria')
        full_dataset = data_service.get_full_dataset_for_ai(bacteria)

        recommendations = ai_service.get_recommendations(
            bacteria=bacteria,
            full_dataset=full_dataset,
            filters=data_service.filter_engine.get_filter_summary()
        )

        return Response(recommendations)
```

### Testing AI Recommendations

**Manual Testing Steps**:
1. Access AI recommendations section
2. Select bacteria (try case variations)
3. Apply filters
4. Verify:
   - Recommendations analyze all antibiotics (not just 3-4)
   - Output includes medical notes and rationale
   - MDR/XDR warnings when applicable
   - Category/Mechanism is properly inferred
   - Case-insensitive bacteria matching

**Automated Testing**:
```python
def test_ai_full_dataset_usage():
    service = UnifiedDataService({'bacteria': 'E. coli'})

    # Get all antibiotics in dataset
    all_antibiotics = service.get_all_antibiotics_for_bacteria('E. coli')
    ai_recommendations = service.get_ai_recommendations('E. coli')

    # AI should consider all antibiotics, not just a subset
    assert len(ai_recommendations['considered_antibiotics']) >= len(all_antibiotics)

def test_ai_medical_insights():
    recommendations = get_ai_recommendations('MRSA')

    assert 'medical_notes' in recommendations
    assert 'resistance_explanation' in recommendations
    assert 'recommendation_rationale' in recommendations
    assert len(recommendations['medical_notes']) > 50  # Substantial content
```

## 5. Database-Based Antibiotic Recommendations Section

### Working with Database Recommendations

**Purpose**: Provides recommendations based on full database analysis with normalized queries.

**API Integration**:
```python
# api/views.py - DatabaseRecommendationView
class DatabaseRecommendationView(APIView):
    def get(self, request):
        data_service = create_data_service(request)

        bacteria = request.GET.get('bacteria')
        recommendations = data_service.get_antibiotic_recommendations(bacteria)

        return Response({
            'bacteria': bacteria,
            'recommendations': recommendations,
            'data_source': 'full_database',
            'filter_summary': data_service.filter_engine.get_filter_summary()
        })
```

**Recommendation Logic**:
```python
# core/data_service.py
def get_antibiotic_recommendations(self, bacteria):
    # Get ALL test results for this bacteria (normalized)
    results = self.get_filtered_results().filter(
        bacteria__name__iexact=normalize_bacteria_name(bacteria)
    )

    # Analyze all antibiotics, not just subset
    recommendations = []
    for antibiotic in results.values('antibiotic__name').distinct():
        antibiotic_results = results.filter(antibiotic__name__iexact=antibiotic['antibiotic__name'])

        effectiveness = self.calculate_effectiveness(antibiotic_results)
        resistance_rate = self.calculate_resistance_rate(antibiotic_results)

        recommendations.append({
            'antibiotic': antibiotic['antibiotic__name'],
            'effectiveness': effectiveness,
            'resistance_rate': resistance_rate,
            'sample_size': antibiotic_results.count()
        })

    # Sort by effectiveness
    return sorted(recommendations, key=lambda x: x['effectiveness'], reverse=True)
```

### Testing Database Recommendations

**Manual Testing Steps**:
1. Access database recommendations
2. Select bacteria (test case variations)
3. Apply filters
4. Verify:
   - All antibiotics are considered (not just 3-4)
   - Recommendations match filtered data
   - Case-insensitive matching works
   - Results consistent with other sections

**Automated Testing**:
```python
def test_database_full_analysis():
    service = UnifiedDataService({'bacteria': 'Klebsiella'})

    # Get recommendations
    recs = service.get_antibiotic_recommendations('Klebsiella')

    # Should analyze all antibiotics, not just subset
    all_antibiotics = service.get_all_antibiotics_for_bacteria('Klebsiella')
    assert len(recs) == len(all_antibiotics)

def test_case_insensitive_recommendations():
    # Test with different case variations
    recs1 = service.get_antibiotic_recommendations('Klebsiella')
    recs2 = service.get_antibiotic_recommendations('klebsiella')
    recs3 = service.get_antibiotic_recommendations('KLEBSIELLA')

    assert recs1 == recs2 == recs3
```

## Integration with Gemma 3:4B

### Setup Steps

1. **Install and Configure Ollama/LocalAI**:
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull Gemma 3:4B model
   ollama pull gemma:3b  # Adjust model name as needed
   ```

2. **Configure LocalAI Service**:
   ```python
   # chatbot/utils_localai.py
   LOCALAI_BASE_URL = "http://localhost:8080"  # Adjust port
   MODEL_NAME = "gemma:3b"
   ```

3. **Test AI Integration**:
   ```python
   from chatbot.utils_localai import query_localai

   # Test basic connectivity
   response = query_localai("Hello, test message")
   print("AI Response:", response)
   ```

### AI Enhancement Implementation

1. **Create AI Service**:
   ```python
   # ai_engine/gemma_service.py
   class GemmaAIService:
       def analyze_resistance_patterns(self, data):
           prompt = f"Analyze these resistance patterns: {data}"
           return query_localai(prompt)

       def generate_medical_notes(self, bacteria, antibiotics):
           prompt = f"Provide medical insights for {bacteria} treatment with {antibiotics}"
           return query_localai(prompt)
   ```

2. **Integrate with Data Service**:
   ```python
   # core/data_service.py
   def get_ai_enhanced_recommendations(self, bacteria):
       base_recs = self.get_antibiotic_recommendations(bacteria)
       ai_insights = self.ai_service.generate_medical_notes(bacteria, base_recs)

       return {
           'recommendations': base_recs,
           'ai_insights': ai_insights,
           'comprehensive_analysis': True
       }
   ```

## Validation and Consistency Testing

### Cross-Section Consistency Tests

**Test Case: Identical Filters Across Sections**
```python
def test_cross_section_consistency():
    filters = {
        'bacteria': 'Klebsiella',
        'date_from': '2024-01-01',
        'date_to': '2024-12-31',
        'department': 'ICU'
    }

    service = UnifiedDataService(filters)

    # Get data from all sections
    stats = service.get_statistics()
    heatmap = service.get_resistance_heatmap()
    ai_recs = service.get_ai_recommendations('Klebsiella')
    db_recs = service.get_antibiotic_recommendations('Klebsiella')

    # Verify sample counts match
    assert stats['total_samples'] == heatmap['total_samples']
    assert stats['total_samples'] == len(ai_recs['analyzed_samples'])

    # Verify bacteria normalization
    assert heatmap['bacteria_key'] == 'klebsiella'  # Normalized
    assert ai_recs['bacteria_normalized'] == 'klebsiella'
```

**Case Sensitivity Validation**:
```python
def test_case_sensitivity_fix():
    variations = ['Klebsiella', 'klebsiella', 'KLEBSIELLA']

    for variant in variations:
        service = UnifiedDataService({'bacteria': variant})
        results = service.get_filtered_results()

        # All should return same normalized results
        assert all(r.bacteria.name.lower() == 'klebsiella' for r in results)
```

### Performance and Data Integrity Tests

**Data Cleanup Validation**:
```bash
# Run cleanup command
python manage.py cleanup_data --dry-run --output=validation_report.json

# Verify no data loss
python manage.py cleanup_data --validate-only
```

**Full Dataset Utilization Test**:
```python
def test_full_dataset_usage():
    # Ensure AI reads all records, not subset
    total_records = TestResult.objects.filter(bacteria__name__iexact='e coli').count()
    ai_analysis = get_ai_recommendations('E. coli')

    assert ai_analysis['records_analyzed'] == total_records
    assert 'all_antibiotics_considered' in ai_analysis
```

## End-to-End Testing Workflow

1. **Setup Test Data**:
   ```bash
   python manage.py loaddata test_antibiogram_data.json
   ```

2. **Run Unified Layer Tests**:
   ```bash
   python manage.py test core.tests.UnifiedLayerTests
   ```

3. **Test Individual Sections**:
   ```bash
   python manage.py test api.tests.DataFiltersTests
   python manage.py test api.tests.ReportGenerationTests
   python manage.py test api.tests.HeatmapTests
   python manage.py test api.tests.AIRecommendationTests
   ```

4. **Integration Testing**:
   ```bash
   python manage.py test integration_tests
   ```

5. **Frontend Testing**:
   - Test filter application across all components
   - Verify consistent data display
   - Test case-insensitive search

## Troubleshooting Common Issues

### Case Sensitivity Still Appearing
- Check that all views use `create_data_service(request)`
- Verify normalization functions are applied
- Run cleanup command: `python manage.py cleanup_data`

### Partial Data Reading
- Ensure AI service receives full dataset from `get_full_dataset_for_ai()`
- Check that database queries don't have LIMIT clauses
- Verify `get_antibiotic_recommendations()` processes all antibiotics

### Filter Inconsistencies
- Confirm all sections use same filter engine instance
- Check that `create_filter_engine(request)` is called consistently
- Validate filter parameters are parsed correctly

### AI Integration Issues
- Verify Ollama/LocalAI is running: `curl http://localhost:8080/health`
- Check model loading: `ollama list`
- Test basic AI query in isolation

## Conclusion

Following these steps ensures the Unified Data Processing Layer provides consistent, accurate, and comprehensive analysis across all sections. The architecture eliminates root causes of data inconsistency and enables intelligent, full-dataset AI analysis with Gemma 3:4B integration.

Key achievements:
- Case-insensitive data handling
- Full dataset utilization
- Centralized filtering
- Unified architecture
- AI-enhanced medical insights

Regular testing and validation maintain system integrity as the project evolves.
