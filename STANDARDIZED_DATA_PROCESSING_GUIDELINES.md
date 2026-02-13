# Standardized Data Processing - Development Guidelines

## Overview

This document provides guidelines for developers working on the Standardized Data Processing system (Unified Data Processing Layer). These guidelines ensure consistency, maintainability, and adherence to the core principles of case-insensitive data handling, full dataset utilization, and unified filtering.

## Core Principles

### 1. Unified Data Access
**All data access must go through the Unified Data Processing Layer.**

❌ **Incorrect:**
```python
# Direct database access
bacteria = Bacteria.objects.filter(name='Klebsiella')
```

✅ **Correct:**
```python
# Through unified layer
from core.data_service import create_data_service
service = create_data_service(request)
bacteria_data = service.get_bacteria_statistics()
```

### 2. Case-Insensitive Operations
**All text comparisons must be case-insensitive.**

❌ **Incorrect:**
```python
Bacteria.objects.filter(name='Klebsiella')
```

✅ **Correct:**
```python
from core.data_normalization import create_case_insensitive_query
Bacteria.objects.filter(create_case_insensitive_query('name', 'Klebsiella'))
```

### 3. Full Dataset Utilization
**AI and analysis functions must process all available data, not subsets.**

❌ **Incorrect:**
```python
# Reading only first 3 antibiotics
antibiotics = Antibiotic.objects.all()[:3]
```

✅ **Correct:**
```python
# Process all antibiotics
antibiotics = Antibiotic.objects.all()
```

## Development Workflow

### 1. Code Structure

#### File Organization
```
core/
├── __init__.py
├── data_normalization.py    # Text normalization utilities
├── master_data.py          # Master data management
├── filters.py              # Global filter engine
├── data_service.py         # Unified data access layer
├── management/commands/    # Management commands
└── tests.py               # Unit tests
```

#### Import Guidelines
```python
# Always import from core modules
from core.data_normalization import normalize_bacteria_name
from core.filters import create_filter_engine
from core.data_service import create_data_service
```

### 2. Adding New Features

#### Step 1: Check Unified Layer First
Before adding new data access code, check if the functionality exists in the unified layer:

```python
# Check data_service.py for existing methods
service = create_data_service(request)
existing_method = service.get_your_data_type()
```

#### Step 2: Extend Unified Layer if Needed
If new functionality is required, extend the unified layer:

```python
# In data_service.py
def get_new_feature_data(self):
    """Get data for new feature using normalized queries."""
    results = self.get_filtered_results()
    # Process with full dataset
    return self.process_all_data(results)
```

#### Step 3: Update All Consumers
Ensure all views/controllers use the new unified method:

```python
# In views.py
def new_feature_view(request):
    service = create_data_service(request)
    data = service.get_new_feature_data()  # Use unified method
    return Response(data)
```

### 3. Database Operations

#### Normalization on Save
Always normalize data before saving to database:

```python
# In models or forms
from core.data_normalization import normalize_bacteria_name

def save(self, *args, **kwargs):
    self.name = normalize_bacteria_name(self.name)
    super().save(*args, **kwargs)
```

#### Query Best Practices
```python
# Use normalized queries
from core.data_normalization import create_case_insensitive_query

def get_bacteria_by_name(name):
    return Bacteria.objects.filter(
        create_case_insensitive_query('name', name)
    )
```

## Testing Guidelines

### 1. Unit Tests

#### Test Data Normalization
```python
def test_bacteria_normalization():
    from core.data_normalization import normalize_bacteria_name

    assert normalize_bacteria_name('  KLEBSIELLA  ') == 'klebsiella'
    assert normalize_bacteria_name('Klebsiella Pneumoniae') == 'klebsiella pneumoniae'
```

#### Test Unified Service
```python
def test_unified_data_access():
    from core.data_service import UnifiedDataService
    from core.filters import GlobalFilterEngine

    engine = GlobalFilterEngine({'bacteria': 'E. coli'})
    service = UnifiedDataService(engine)

    stats = service.get_statistics()
    assert 'total_samples' in stats
    assert stats['total_samples'] > 0
```

### 2. Integration Tests

#### Test Cross-Section Consistency
```python
def test_filter_consistency():
    filters = {'bacteria': 'Klebsiella', 'date_from': '2024-01-01'}

    # All sections should return same filtered count
    service = UnifiedDataService(filters)
    stats_count = service.get_statistics()['total_samples']
    heatmap_count = len(service.get_resistance_heatmap())
    ai_count = service.get_ai_recommendations('Klebsiella')['total_analyzed']

    assert stats_count == heatmap_count == ai_count
```

#### Test Full Dataset Usage
```python
def test_ai_full_dataset():
    service = UnifiedDataService({'bacteria': 'MRSA'})

    # AI should analyze all antibiotics
    all_antibiotics = Antibiotic.objects.count()
    ai_analysis = service.get_ai_recommendations('MRSA')
    analyzed_antibiotics = len(ai_analysis['antibiotics_considered'])

    assert analyzed_antibiotics == all_antibiotics
```

### 3. Running Tests

#### Run Unified Layer Tests
```bash
cd Data_Analysis_Project
python test_unified_layer.py
```

#### Run Django Tests
```bash
python manage.py test core
python manage.py test api
```

## Code Review Checklist

### ✅ Must-Have
- [ ] All data access uses `create_data_service(request)`
- [ ] All text queries are case-insensitive
- [ ] AI/analysis processes full dataset (not subsets)
- [ ] Filters applied consistently across sections
- [ ] Data normalized before saving

### ✅ Should-Have
- [ ] Unit tests for new normalization functions
- [ ] Integration tests for new features
- [ ] Documentation updated
- [ ] Performance impact assessed

### ✅ Nice-to-Have
- [ ] Caching implemented for expensive operations
- [ ] Logging added for debugging
- [ ] Error handling improved

## Common Pitfalls

### 1. Direct Database Queries
**Problem:** Bypassing the unified layer leads to inconsistent results.

**Solution:** Always use `create_data_service(request)`.

### 2. Case-Sensitive Comparisons
**Problem:** `Bacteria.objects.filter(name='Klebsiella')` misses 'klebsiella'.

**Solution:** Use `create_case_insensitive_query('name', 'Klebsiella')`.

### 3. Partial Data Analysis
**Problem:** AI analyzing only first N records.

**Solution:** Process `queryset.all()`, not `queryset[:N]`.

### 4. Filter Inconsistency
**Problem:** Different sections apply different filters.

**Solution:** Use same `GlobalFilterEngine` instance across sections.

## Performance Considerations

### 1. Database Indexes
Ensure indexes on frequently queried fields:

```sql
CREATE INDEX idx_bacteria_name_lower ON bacteria (lower(name));
CREATE INDEX idx_antibiotic_name_lower ON antibiotics (lower(name));
```

### 2. Caching
Cache expensive operations:

```python
from django.core.cache import cache

def get_bacteria_statistics(self):
    cache_key = f"bacteria_stats_{self.filter_engine.get_cache_key()}"
    result = cache.get(cache_key)
    if result is None:
        result = self._calculate_statistics()
        cache.set(cache_key, result, 3600)  # Cache for 1 hour
    return result
```

### 3. Query Optimization
Use select_related and prefetch_related:

```python
def get_filtered_results(self):
    return TestResult.objects.filter(
        self.filter_engine.get_query()
    ).select_related('bacteria', 'antibiotic', 'sample')
```

## Error Handling

### 1. Validation Errors
```python
from core.data_normalization import validate_sensitivity_value

def clean_sensitivity(self):
    self.sensitivity = validate_sensitivity_value(self.sensitivity)
    if self.sensitivity == 'unknown':
        raise ValidationError('Invalid sensitivity value')
```

### 2. Service Errors
```python
def get_data_with_fallback(self):
    try:
        return self.get_primary_data()
    except Exception as e:
        logger.error(f"Primary data failed: {e}")
        return self.get_fallback_data()
```

## Documentation

### 1. Code Documentation
```python
def get_antibiotic_recommendations(self, bacteria: str) -> dict:
    """
    Get antibiotic recommendations for a bacteria.

    Processes ALL available antibiotics for comprehensive analysis.

    Args:
        bacteria: Bacteria name (case-insensitive)

    Returns:
        Dict containing recommendations and analysis metadata
    """
```

### 2. API Documentation
Update API docs when adding new endpoints:

```python
# In views.py docstring
"""
GET /api/antibiotic-recommendations/
Get antibiotic recommendations with full dataset analysis.

Filters:
- bacteria: Case-insensitive bacteria name
- date_from/date_to: Date range
- department: Department filter
"""
```

## Deployment Checklist

### Pre-Deployment
- [ ] Run `python test_unified_layer.py`
- [ ] Run `python manage.py test`
- [ ] Run data cleanup: `python manage.py cleanup_data --dry-run`
- [ ] Check for case sensitivity issues
- [ ] Verify AI processes full datasets

### Post-Deployment
- [ ] Monitor performance metrics
- [ ] Check error logs for normalization issues
- [ ] Validate filter consistency across sections
- [ ] Run integration tests in production

## Maintenance

### Regular Tasks
1. **Weekly:** Run data cleanup command
2. **Monthly:** Review and optimize slow queries
3. **Quarterly:** Update normalization rules for new data patterns

### Monitoring
```python
# Add to monitoring
def check_data_consistency():
    """Ensure no case sensitivity issues exist."""
    service = UnifiedDataService()
    duplicates = service.check_for_duplicates()
    if duplicates:
        alert_admin(f"Data inconsistencies found: {duplicates}")
```

## Conclusion

Following these guidelines ensures the Standardized Data Processing system remains robust, consistent, and maintainable. The unified layer approach eliminates common issues and provides a solid foundation for future development.

**Key Reminders:**
- Always use the unified data service
- Ensure case-insensitive operations
- Process full datasets for analysis
- Apply filters consistently
- Test thoroughly before deployment

For questions or clarifications, refer to the `WORKING_AND_TESTING_STEPS.md` file or consult the development team.
