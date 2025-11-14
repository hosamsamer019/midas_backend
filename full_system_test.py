"""
Comprehensive System Test Script
Tests all components of the Smart Antibiogram System
"""

import os
import sys
import django
import json
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

# Import models
from users.models import User
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from uploads.models import Upload
from ai_recommendations.models import AIRecommendation

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_test(name, passed, message=""):
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} - {name}")
    if message:
        print(f"       {message}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

class SystemTester:
    def __init__(self):
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        self.client = APIClient()
        self.token = None
        self.test_user = None

    def test(self, name, condition, message=""):
        """Record a test result"""
        self.results['total'] += 1
        if condition:
            self.results['passed'] += 1
            print_test(name, True, message)
        else:
            self.results['failed'] += 1
            print_test(name, False, message)
        return condition

    def warning(self, message):
        """Record a warning"""
        self.results['warnings'] += 1
        print_warning(message)

    # ==================== INFRASTRUCTURE TESTS ====================
    
    def test_django_setup(self):
        print_header("DJANGO INFRASTRUCTURE TESTS")
        
        # Test Django version
        import django
        self.test("Django Installation", True, f"Django version: {django.get_version()}")
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.test("Database Connection", True, "SQLite database connected")
        except Exception as e:
            self.test("Database Connection", False, str(e))
        
        # Test migrations
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            self.test("Database Migrations", len(plan) == 0, 
                     f"Pending migrations: {len(plan)}")
        except Exception as e:
            self.test("Database Migrations", False, str(e))
        
        # Test installed apps
        from django.conf import settings
        required_apps = [
            'rest_framework',
            'rest_framework_simplejwt',
            'corsheaders',
            'users',
            'bacteria',
            'antibiotics',
            'samples',
            'results',
            'ai_recommendations',
            'uploads'
        ]
        
        for app in required_apps:
            installed = app in settings.INSTALLED_APPS
            self.test(f"App Installed: {app}", installed)

    def test_models(self):
        print_header("DATABASE MODEL TESTS")
        
        # Test User model
        user_count = User.objects.count()
        self.test("User Model", True, f"Users in database: {user_count}")
        
        # Test Bacteria model
        bacteria_count = Bacteria.objects.count()
        self.test("Bacteria Model", True, f"Bacteria in database: {bacteria_count}")
        if bacteria_count == 0:
            self.warning("No bacteria data found. Run load_initial_data.py")
        
        # Test Antibiotic model
        antibiotic_count = Antibiotic.objects.count()
        self.test("Antibiotic Model", True, f"Antibiotics in database: {antibiotic_count}")
        if antibiotic_count == 0:
            self.warning("No antibiotic data found. Run load_initial_data.py")
        
        # Test Sample model
        sample_count = Sample.objects.count()
        self.test("Sample Model", True, f"Samples in database: {sample_count}")
        if sample_count == 0:
            self.warning("No sample data found. Run load_initial_data.py")
        
        # Test TestResult model
        result_count = TestResult.objects.count()
        self.test("TestResult Model", True, f"Test results in database: {result_count}")
        if result_count == 0:
            self.warning("No test result data found. Run load_initial_data.py")
        
        # Test Upload model
        upload_count = Upload.objects.count()
        self.test("Upload Model", True, f"Uploads in database: {upload_count}")
        
        # Test AIRecommendation model
        ai_count = AIRecommendation.objects.count()
        self.test("AIRecommendation Model", True, f"AI recommendations in database: {ai_count}")

    def test_data_integrity(self):
        print_header("DATA INTEGRITY TESTS")
        
        # Test foreign key relationships
        try:
            # Check if all samples have valid bacteria references
            samples_with_bacteria = Sample.objects.filter(bacteria__isnull=False).count()
            total_samples = Sample.objects.count()
            self.test("Sample-Bacteria Relationship", 
                     samples_with_bacteria == total_samples or total_samples == 0,
                     f"{samples_with_bacteria}/{total_samples} samples have bacteria")
            
            # Check if all test results have valid references
            results_with_sample = TestResult.objects.filter(sample__isnull=False).count()
            results_with_antibiotic = TestResult.objects.filter(antibiotic__isnull=False).count()
            total_results = TestResult.objects.count()
            
            self.test("TestResult-Sample Relationship",
                     results_with_sample == total_results or total_results == 0,
                     f"{results_with_sample}/{total_results} results have samples")
            
            self.test("TestResult-Antibiotic Relationship",
                     results_with_antibiotic == total_results or total_results == 0,
                     f"{results_with_antibiotic}/{total_results} results have antibiotics")
            
        except Exception as e:
            self.test("Data Integrity Check", False, str(e))

    def setup_test_user(self):
        """Create or get test user and token"""
        try:
            self.test_user = User.objects.first()
            if not self.test_user:
                self.test_user = User.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='testpass123'
                )
                print_info("Created test user")
            
            self.token = str(AccessToken.for_user(self.test_user))
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
            return True
        except Exception as e:
            print_error(f"Failed to setup test user: {e}")
            return False

    def test_api_endpoints(self):
        print_header("API ENDPOINT TESTS")
        
        if not self.setup_test_user():
            print_error("Cannot test API endpoints without test user")
            return
        
        # Test public endpoints (no auth required)
        public_endpoints = [
            ('GET', '/api/welcome/', 200),
            ('GET', '/api/stats/', 200),
            ('GET', '/api/sensitivity-distribution/', 200),
            ('GET', '/api/antibiotic-effectiveness/', 200),
            ('GET', '/api/resistance-over-time/', 200),
            ('GET', '/api/resistance-heatmap/', 200),
            ('GET', '/api/bacteria-list/', 200),
            ('GET', '/api/departments-list/', 200),
        ]
        
        for method, endpoint, expected_status in public_endpoints:
            try:
                if method == 'GET':
                    response = self.client.get(endpoint)
                
                success = response.status_code == expected_status
                self.test(f"{method} {endpoint}", success,
                         f"Status: {response.status_code} (Expected: {expected_status})")
            except Exception as e:
                self.test(f"{method} {endpoint}", False, str(e))
        
        # Test authenticated endpoints
        auth_endpoints = [
            ('GET', '/api/users/', 200),
            ('GET', '/api/bacteria/', 200),
            ('GET', '/api/antibiotics/', 200),
            ('GET', '/api/samples/', 200),
            ('GET', '/api/results/', 200),
            ('GET', '/api/uploads/', 200),
            ('GET', '/api/ai-recommendations/', 200),
            ('GET', '/api/analytics/', 200),
            ('GET', '/api/antibiotics-list/', 200),
        ]
        
        for method, endpoint, expected_status in auth_endpoints:
            try:
                if method == 'GET':
                    response = self.client.get(endpoint)
                
                success = response.status_code == expected_status
                self.test(f"{method} {endpoint} (Auth)", success,
                         f"Status: {response.status_code} (Expected: {expected_status})")
            except Exception as e:
                self.test(f"{method} {endpoint} (Auth)", False, str(e))

    def test_ai_functionality(self):
        print_header("AI/ML FUNCTIONALITY TESTS")
        
        # Check if model files exist
        model_path = 'ai_engine/model.pkl'
        encoders_path = 'ai_engine/encoders.pkl'
        
        model_exists = os.path.exists(model_path)
        encoders_exist = os.path.exists(encoders_path)
        
        self.test("AI Model File Exists", model_exists, 
                 f"Path: {model_path}")
        self.test("AI Encoders File Exists", encoders_exist,
                 f"Path: {encoders_path}")
        
        if not model_exists or not encoders_exist:
            self.warning("AI model not trained. Run: python ai_engine/train_model.py")
        
        # Test AI prediction endpoint
        if Bacteria.objects.exists():
            bacteria = Bacteria.objects.first()
            try:
                response = self.client.post('/api/ai/predict/', 
                                           {'bacteria_name': bacteria.name},
                                           format='json')
                self.test("AI Prediction Endpoint", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    has_recommendations = 'recommendations' in data
                    self.test("AI Prediction Response Format", has_recommendations,
                             f"Keys: {list(data.keys())}")
            except Exception as e:
                self.test("AI Prediction Endpoint", False, str(e))
        else:
            self.warning("No bacteria data to test AI predictions")

    def test_report_generation(self):
        print_header("REPORT GENERATION TESTS")
        
        # Test PDF report generation
        try:
            response = self.client.get('/api/reports/')
            self.test("PDF Report Generation", 
                     response.status_code == 200,
                     f"Status: {response.status_code}")
            
            if response.status_code == 200:
                is_pdf = response.get('Content-Type') == 'application/pdf'
                self.test("PDF Content Type", is_pdf,
                         f"Content-Type: {response.get('Content-Type')}")
        except Exception as e:
            self.test("PDF Report Generation", False, str(e))
        
        # Test Excel report generation
        try:
            response = self.client.post('/api/reports/')
            self.test("Excel Report Generation",
                     response.status_code == 200,
                     f"Status: {response.status_code}")
            
            if response.status_code == 200:
                is_excel = 'spreadsheet' in response.get('Content-Type', '')
                self.test("Excel Content Type", is_excel,
                         f"Content-Type: {response.get('Content-Type')}")
        except Exception as e:
            self.test("Excel Report Generation", False, str(e))

    def test_dependencies(self):
        print_header("DEPENDENCY TESTS")
        
        # Test Python dependencies
        required_packages = [
            'django',
            'rest_framework',  # djangorestframework package imports as rest_framework
            'rest_framework_simplejwt',  # djangorestframework-simplejwt package imports as rest_framework_simplejwt
            'corsheaders',
            'pandas',
            'numpy',
            'sklearn',
            'openpyxl',
            'reportlab',
            'cryptography',
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.test(f"Python Package: {package}", True)
            except ImportError:
                self.test(f"Python Package: {package}", False, "Not installed")
        
        # Test optional dependencies
        optional_packages = [
            ('pytesseract', 'OCR functionality'),
            ('cv2', 'Image processing'),
            ('matplotlib', 'Chart generation'),
        ]
        
        for package, purpose in optional_packages:
            try:
                __import__(package)
                self.test(f"Optional Package: {package}", True, f"For {purpose}")
            except ImportError:
                self.warning(f"Optional package '{package}' not installed (for {purpose})")

    def test_security(self):
        print_header("SECURITY CONFIGURATION TESTS")
        
        from django.conf import settings
        
        # Test JWT configuration
        self.test("JWT Configuration", hasattr(settings, 'SIMPLE_JWT'),
                 "JWT settings configured")
        
        # Test CORS configuration
        self.test("CORS Configuration", hasattr(settings, 'CORS_ALLOWED_ORIGINS'),
                 "CORS origins configured")
        
        # Test CSRF configuration
        self.test("CSRF Configuration", hasattr(settings, 'CSRF_TRUSTED_ORIGINS'),
                 "CSRF trusted origins configured")
        
        # Test authentication classes
        rest_config = getattr(settings, 'REST_FRAMEWORK', {})
        auth_classes = rest_config.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        has_jwt = any('JWT' in cls for cls in auth_classes)
        self.test("JWT Authentication Enabled", has_jwt,
                 f"Auth classes: {len(auth_classes)}")
        
        # Check DEBUG mode
        if settings.DEBUG:
            self.warning("DEBUG mode is ON - should be OFF in production")
        else:
            self.test("Production Mode", True, "DEBUG is OFF")

    def test_file_structure(self):
        print_header("FILE STRUCTURE TESTS")
        
        # Check critical files
        critical_files = [
            'manage.py',
            'requirements.txt',
            'antibiogram/settings.py',
            'antibiogram/urls.py',
            'api/views.py',
            'api/urls.py',
            'api/serializers.py',
        ]
        
        for file_path in critical_files:
            exists = os.path.exists(file_path)
            self.test(f"File exists: {file_path}", exists)
        
        # Check app directories
        app_dirs = [
            'users',
            'bacteria',
            'antibiotics',
            'samples',
            'results',
            'ai_recommendations',
            'uploads',
            'api',
        ]
        
        for app_dir in app_dirs:
            exists = os.path.isdir(app_dir)
            self.test(f"App directory: {app_dir}", exists)
            
            if exists:
                # Check for models.py
                models_exists = os.path.exists(f"{app_dir}/models.py")
                self.test(f"  - {app_dir}/models.py", models_exists)

    def print_summary(self):
        print_header("TEST SUMMARY")
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        warnings = self.results['warnings']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests:    {total}")
        print(f"{Colors.OKGREEN}Passed:         {passed} ({pass_rate:.1f}%){Colors.ENDC}")
        print(f"{Colors.FAIL}Failed:         {failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings:       {warnings}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Overall Status: ", end="")
        if failed == 0:
            print(f"{Colors.OKGREEN}✓ ALL TESTS PASSED{Colors.ENDC}")
        elif pass_rate >= 80:
            print(f"{Colors.WARNING}⚠ MOSTLY PASSING (Some issues found){Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ CRITICAL ISSUES FOUND{Colors.ENDC}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'results': self.results,
                'pass_rate': pass_rate
            }, f, indent=2)
        
        print(f"\n{Colors.OKCYAN}Detailed report saved to: {report_file}{Colors.ENDC}")

    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                  SMART ANTIBIOGRAM SYSTEM                                  ║")
        print("║                  COMPREHENSIVE SYSTEM TEST                                 ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_info(f"Working directory: {os.getcwd()}")
        
        # Run all test suites
        self.test_django_setup()
        self.test_models()
        self.test_data_integrity()
        self.test_dependencies()
        self.test_file_structure()
        self.test_security()
        self.test_api_endpoints()
        self.test_ai_functionality()
        self.test_report_generation()
        
        # Print summary
        self.print_summary()

def main():
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
