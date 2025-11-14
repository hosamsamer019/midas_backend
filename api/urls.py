from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'bacteria', views.BacteriaViewSet)
router.register(r'antibiotics', views.AntibioticViewSet)
router.register(r'samples', views.SampleViewSet)
router.register(r'results', views.TestResultViewSet)
router.register(r'uploads', views.UploadViewSet)
router.register(r'ai-recommendations', views.AIRecommendationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('sensitivity-distribution/', views.SensitivityDistributionView.as_view(), name='sensitivity_distribution'),
    path('antibiotic-effectiveness/', views.AntibioticEffectivenessView.as_view(), name='antibiotic_effectiveness'),
    path('resistance-over-time/', views.ResistanceOverTimeView.as_view(), name='resistance_over_time'),
    path('reports/', views.ReportView.as_view(), name='reports'),
    path('reports/<str:report_type>/', views.ReportView.as_view(), name='reports_by_type'),
    path('ai/predict/', views.AIPredictView.as_view(), name='ai_predict'),
    path('digital-signature/', views.DigitalSignatureView.as_view(), name='digital_signature'),
    path('ocr/', views.OCRView.as_view(), name='ocr'),
    path('bacteria-list/', views.BacteriaListView.as_view(), name='bacteria_list'),
    path('antibiotics-list/', views.AntibioticListView.as_view(), name='antibiotics_list'),
    path('departments-list/', views.DepartmentListView.as_view(), name='departments_list'),
    path('resistance-heatmap/', views.ResistanceHeatmapView.as_view(), name='resistance_heatmap'),
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
]
