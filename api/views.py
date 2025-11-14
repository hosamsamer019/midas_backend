from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from django.db.models import Count, Q, F
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import sys
sys.path.append('..')
from ai_engine.train_model import load_model, predict_antibiotic
from users.models import User
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from uploads.models import Upload
from ai_recommendations.models import AIRecommendation
from .serializers import (
    UserSerializer, BacteriaSerializer, AntibioticSerializer,
    SampleSerializer, TestResultSerializer, UploadSerializer,
    AIRecommendationSerializer, RegisterSerializer
)

@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    authentication_classes = []  # Disable authentication for login
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
            if user:
                refresh = RefreshToken.for_user(user)
                response.data['refresh'] = str(refresh)
                response.data['access'] = str(refresh.access_token)
                response.data['user'] = UserSerializer(user).data
        return response

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class BacteriaViewSet(viewsets.ModelViewSet):
    queryset = Bacteria.objects.all()
    serializer_class = BacteriaSerializer
    permission_classes = [IsAuthenticated]

class AntibioticViewSet(viewsets.ModelViewSet):
    queryset = Antibiotic.objects.all()
    serializer_class = AntibioticSerializer
    permission_classes = [IsAuthenticated]

class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = [IsAuthenticated]

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]

class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [IsAuthenticated]

class AIRecommendationViewSet(viewsets.ModelViewSet):
    queryset = AIRecommendation.objects.all()
    serializer_class = AIRecommendationSerializer
    permission_classes = [IsAuthenticated]

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_samples = Sample.objects.count()
        total_bacteria = Bacteria.objects.count()
        total_antibiotics = Antibiotic.objects.count()
        return Response({
            'total_samples': total_samples,
            'total_bacteria': total_bacteria,
            'total_antibiotics': total_antibiotics
        })

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Placeholder for analytics data
        return Response({"message": "Analytics data"})

class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Generate PDF report
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="antibiogram_report.pdf"'

        p = canvas.Canvas(response)
        p.drawString(100, 750, "Antibiogram Report")
        p.drawString(100, 730, f"Total Samples: {Sample.objects.count()}")
        p.drawString(100, 710, f"Total Bacteria: {Bacteria.objects.count()}")
        p.drawString(100, 690, f"Total Antibiotics: {Antibiotic.objects.count()}")
        p.showPage()
        p.save()
        return response

    def post(self, request):
        # Generate Excel report
        results = TestResult.objects.select_related('sample', 'bacteria', 'antibiotic').all()

        wb = Workbook()
        ws = wb.active
        ws.title = "Antibiogram Report"

        # Header
        ws.cell(row=1, column=1, value="Sample ID")
        ws.cell(row=1, column=2, value="Bacteria")
        ws.cell(row=1, column=3, value="Antibiotic")
        ws.cell(row=1, column=4, value="Sensitivity")
        ws.cell(row=1, column=5, value="Date")

        # Data
        for row_num, result in enumerate(results, start=2):
            ws.cell(row=row_num, column=1, value=result.sample.id)
            ws.cell(row=row_num, column=2, value=result.bacteria.name)
            ws.cell(row=row_num, column=3, value=result.antibiotic.name)
            ws.cell(row=row_num, column=4, value=result.sensitivity)
            ws.cell(row=row_num, column=5, value=result.sample.date.strftime('%Y-%m-%d'))

        # Save to response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="antibiogram_report.xlsx"'
        wb.save(response)
        return response

class SensitivityDistributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sensitivity_counts = TestResult.objects.values('sensitivity').annotate(count=Count('sensitivity'))
        data = [{'name': item['sensitivity'], 'value': item['count']} for item in sensitivity_counts]
        return Response(data)

class AntibioticEffectivenessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        effectiveness_data = TestResult.objects.values('antibiotic__name').annotate(
            effective=Count('id', filter=Q(sensitivity='Sensitive')),
            total=Count('id')
        ).annotate(
            effectiveness=100.0 * F('effective') / F('total')
        )
        data = [{'antibiotic': item['antibiotic__name'], 'effectiveness': round(item['effectiveness'], 2)} for item in effectiveness_data]
        return Response(data)

class ResistanceOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resistance_trend = TestResult.objects.filter(sensitivity='Resistant').values(
            'sample__date'
        ).annotate(count=Count('id')).order_by('sample__date')
        data = [{'month': item['sample__date'].strftime('%Y-%m'), 'resistance': item['count']} for item in resistance_trend]
        return Response(data)

class AIPredictView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        bacteria_name = request.data.get('bacteria_name')
        if not bacteria_name:
            return Response({"error": "Bacteria name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Load model and encoders
        model, encoders = load_model()
        if not model:
            return Response({"error": "AI model not available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Make prediction
        result = predict_antibiotic(bacteria_name, encoders, model)

        return Response(result)

class DigitalSignatureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Placeholder for digital signature verification
        try:
            # Implement digital signature verification logic here
            # For now, just return success
            return Response({"message": "Digital signature verified successfully"})
        except Exception as e:
            return Response({"error": f"Verification failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BacteriaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bacteria = Bacteria.objects.all()
        data = [{'id': b.id, 'name': b.name, 'type': b.bacteria_type} for b in bacteria]
        return Response(data)

class AntibioticListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        antibiotics = Antibiotic.objects.all()
        data = [{'id': a.id, 'name': a.name, 'category': a.category} for a in antibiotics]
        return Response(data)

class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        departments = Sample.objects.values_list('department', flat=True).distinct()
        data = [{'name': dept} for dept in departments if dept]
        return Response(data)
