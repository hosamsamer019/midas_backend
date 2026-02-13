# Chatbot Database Connectivity Testing Procedures

## Overview
This document provides comprehensive testing procedures to verify that the smart chat is properly connected to and analyzing the antibiogram project's database.

## Prerequisites

### 1. Environment Setup
- Python 3.8+ installed
- Virtual environment activated
- All dependencies installed: `pip install -r requirements.txt`
- Database migrations applied: `python manage.py migrate`
- Initial data loaded (if applicable)

### 2. Server Running
- Django development server running: `python manage.py runserver 8000`
- Server accessible at `http://localhost:8000`

### 3. Test Data
- Ensure antibiogram database contains sample data
- Verify test datasets are loaded (ICU antibiotic.xlsx, Antibiogram_Test_Dataset.xlsx)

## Testing Procedures

### Phase 1: Basic Connectivity Tests

#### 1.1 Database Connection Test
```bash
cd Data_Analysis_Project
python manage.py check
```
**Expected Result:** No errors, successful Django system check

#### 1.2 Database Table Verification
```bash
python manage.py shell
```
```python
from samples.models import Sample
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from results.models import TestResult
from chatbot.models import ChatMessage, KnowledgeBase

# Check record counts
print("Samples:", Sample.objects.count())
print("Bacteria:", Bacteria.objects.count())
print("Antibiotics:", Antibiotic.objects.count())
print("Test Results:", TestResult.objects.count())
print("Chat Messages:", ChatMessage.objects.count())
print("Knowledge Base:", KnowledgeBase.objects.count())
```
**Expected Result:** Tables exist and contain data (may be 0 for chat-related tables)

### Phase 2: API Endpoint Tests

#### 2.1 Manual API Testing with curl
```bash
# Test basic stats endpoint
curl -X GET http://localhost:8000/api/stats/

# Test antibiotic effectiveness
curl -X GET http://localhost:8000/api/antibiotic-effectiveness/

# Test resistance over time
curl -X GET http://localhost:8000/api/resistance-over-time/

# Test departments list
curl -X GET http://localhost:8000/api/departments-list/

# Test resistance heatmap
curl -X GET http://localhost:8000/api/resistance-heatmap/

# Test sensitivity distribution
curl -X GET http://localhost:8000/api/sensitivity-distribution/
```

**Expected Result:** All endpoints return HTTP 200 with JSON data

#### 2.2 Chatbot API Testing
```bash
# Test chatbot endpoint with sample queries
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the resistance rate for E. coli?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me antibiotic effectiveness data"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the resistance trends over time?"}'
```

**Expected Result:** Chatbot returns relevant responses with database-derived information

### Phase 3: Automated Testing

#### 3.1 Run Comprehensive Test Script
```bash
cd Data_Analysis_Project
python test_chatbot_db_connectivity.py
```

**Expected Result:** Test script runs successfully and reports PASS status for all categories

#### 3.2 Review Test Results
- Check the generated JSON results file
- Verify all 5 test categories pass:
  - Database Connection: ✅ PASS
  - Django Models: X/6 passed
  - API Endpoints: X/6 passed
  - Chat Functionality: X/4 passed
  - Data Analysis: ✅ PASS

### Phase 4: Functional Testing

#### 4.1 Frontend Integration Test
1. Open browser to `http://localhost:3000` (Next.js frontend)
2. Navigate to chatbot interface
3. Test queries:
   - "What bacteria have the highest resistance rates?"
   - "Show me resistance patterns by department"
   - "Which antibiotics are most effective?"
   - "How has resistance changed over time?"

**Expected Result:** Chatbot provides accurate, data-driven responses

#### 4.2 Data Analysis Verification
1. Compare chatbot responses with direct database queries
2. Verify statistical calculations (resistance rates, percentages)
3. Check data filtering and aggregation
4. Validate time-based trend analysis

### Phase 5: Security and Privacy Testing

#### 5.1 PHI Detection Test
```bash
# Test with sensitive information
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about patient John Doe with MRSA"}'
```

**Expected Result:** Sensitive information is detected and anonymized

#### 5.2 Data Sanitization Test
- Test queries containing potential PHI
- Verify chatbot responses don't expose sensitive data
- Check data anonymization in logs and responses

## Test Case Matrix

| Test Category | Test Case | Expected Result | Priority |
|---------------|-----------|-----------------|----------|
| Database | Connection | Successful connection | Critical |
| Database | Model Queries | All models accessible | Critical |
| API | Stats Endpoint | Returns statistics JSON | High |
| API | Effectiveness Endpoint | Returns effectiveness data | High |
| API | Time Trends Endpoint | Returns trend data | High |
| API | Department Endpoint | Returns department list | Medium |
| API | Heatmap Endpoint | Returns heatmap data | Medium |
| API | Distribution Endpoint | Returns distribution data | Medium |
| Chatbot | Basic Queries | Relevant responses | Critical |
| Chatbot | Data Analysis | Accurate calculations | High |
| Chatbot | Knowledge Base | Uses stored knowledge | Medium |
| Security | PHI Detection | Anonymizes sensitive data | Critical |
| Frontend | UI Integration | Chat interface works | High |

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: `ModuleNotFoundError: No module named 'rest_framework_simplejwt'`
**Solution:** Dependencies not fully installed. Wait for `pip install -r requirements.txt` to complete.

#### Issue: `Connection refused` on API calls
**Solution:** Django server not running. Start with `python manage.py runserver 8000`.

#### Issue: Empty responses from API endpoints
**Solution:** Database may be empty. Load initial data using data loading scripts.

#### Issue: Chatbot gives generic responses
**Solution:** Knowledge base may be empty or FAISS model not loaded. Check chatbot configuration.

#### Issue: Test script fails with import errors
**Solution:** Django environment not properly set up. Ensure virtual environment is activated.

### Performance Considerations

- **Large Datasets:** Test with substantial data volumes
- **Concurrent Users:** Test multiple simultaneous chat sessions
- **Response Time:** Verify responses are generated within reasonable time (< 30 seconds)
- **Memory Usage:** Monitor for memory leaks during extended testing

## Success Criteria

### Minimum Viable Test (MVT)
- ✅ Database connection successful
- ✅ At least 3 API endpoints working
- ✅ Chatbot responds to basic queries
- ✅ No critical security vulnerabilities

### Full Success Criteria
- ✅ All 5 test categories pass (100% score)
- ✅ All API endpoints functional
- ✅ Chatbot provides accurate data analysis
- ✅ Security measures working (PHI detection)
- ✅ Frontend integration complete
- ✅ Performance meets requirements

## Reporting

### Test Report Format
```
Test Execution Summary
======================
Date: YYYY-MM-DD HH:MM:SS
Tester: [Name]
Environment: [Details]

Overall Score: X/5 categories passed

Detailed Results:
- Database Connection: [PASS/FAIL]
- Django Models: [X/6 passed]
- API Endpoints: [X/6 passed]
- Chat Functionality: [X/4 passed]
- Data Analysis: [PASS/FAIL]

Issues Found:
- [List any issues discovered]

Recommendations:
- [Any improvements or fixes needed]
```

### Automated Report Generation
The test script automatically generates a JSON report file with timestamp:
`chatbot_db_test_results_YYYYMMDD_HHMMSS.json`

## Maintenance

### Regular Testing Schedule
- **Daily:** Basic connectivity checks
- **Weekly:** Full test suite execution
- **Monthly:** Performance and security audits
- **After Updates:** Complete regression testing

### Monitoring
- Set up automated tests in CI/CD pipeline
- Monitor API response times
- Track error rates and user feedback
- Regular database health checks

## Conclusion

Following these testing procedures ensures the smart chat is properly connected to and effectively analyzing the antibiogram database. The comprehensive test suite covers connectivity, functionality, security, and performance aspects critical for production deployment.
