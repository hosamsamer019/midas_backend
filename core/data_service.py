"""
Unified Data Service
Provides centralized data access methods for all views.
All data queries should go through this service to ensure consistency.
"""

from typing import Dict, List, Any, Optional
from django.db.models import Count, Q, F, Avg, Max, Min, QuerySet
from django.db.models.functions import TruncMonth, TruncDate
from .filters import GlobalFilterEngine
import logging

logger = logging.getLogger(__name__)


class UnifiedDataService:
    """
    Unified data service that provides consistent data access across all views.
    This service ensures all data is properly filtered and normalized.
    """
    
    def __init__(self, filter_engine: Optional[GlobalFilterEngine] = None):
        """
        Initialize the data service.
        
        Args:
            filter_engine: GlobalFilterEngine instance for filtering data
        """
        self.filter_engine = filter_engine or GlobalFilterEngine()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get basic statistics with applied filters.

        Returns:
            Dictionary with statistics
        """
        try:
            from samples.models import Sample
            from bacteria.models import Bacteria
            from antibiotics.models import Antibiotic
            from results.models import TestResult

            # Apply filters to samples
            filtered_samples = self.filter_engine.apply_to_samples(Sample.objects.all())

            # Apply filters to test results
            filtered_results = self.filter_engine.apply_to_test_results(TestResult.objects.all())

            # Get unique bacteria and antibiotics from filtered results
            bacteria_ids = filtered_results.values_list('sample__bacteria_id', flat=True).distinct()
            antibiotic_ids = filtered_results.values_list('antibiotic_id', flat=True).distinct()

            return {
                'total_samples': filtered_samples.count(),
                'total_bacteria': bacteria_ids.count() if self.filter_engine.filters else Bacteria.objects.count(),
                'total_antibiotics': antibiotic_ids.count() if self.filter_engine.filters else Antibiotic.objects.count(),
                'total_results': filtered_results.count(),
                'resistant_count': filtered_results.filter(sensitivity__iexact='resistant').count(),
                'sensitive_count': filtered_results.filter(sensitivity__iexact='sensitive').count(),
                'intermediate_count': filtered_results.filter(sensitivity__iexact='intermediate').count(),
            }
        except Exception as e:
            logger.error(f"Error in get_statistics: {str(e)}", exc_info=True)
            # Return default values to prevent 500 errors
            return {
                'total_samples': 0,
                'total_bacteria': 0,
                'total_antibiotics': 0,
                'total_results': 0,
                'resistant_count': 0,
                'sensitive_count': 0,
                'intermediate_count': 0,
            }
    
    def get_sensitivity_distribution(self) -> List[Dict[str, Any]]:
        """
        Get sensitivity distribution data with applied filters.

        Returns:
            List of dictionaries with sensitivity distribution
        """
        try:
            from results.models import TestResult

            # Apply filters
            filtered_results = self.filter_engine.apply_to_test_results(TestResult.objects.all())

            # Get sensitivity counts
            sensitivity_counts = filtered_results.values('sensitivity').annotate(
                count=Count('id')
            ).order_by('-count')

            # Format data
            data = []
            for item in sensitivity_counts:
                if item['sensitivity']:
                    data.append({
                        'name': item['sensitivity'].capitalize(),
                        'value': item['count']
                    })

            return data
        except Exception as e:
            logger.error(f"Error in get_sensitivity_distribution: {str(e)}", exc_info=True)
            return []
    
    def get_antibiotic_effectiveness(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Get antibiotic effectiveness data with applied filters.

        Args:
            top_n: Number of top antibiotics to return

        Returns:
            List of dictionaries with antibiotic effectiveness
        """
        try:
            from results.models import TestResult

            # Apply filters
            filtered_results = self.filter_engine.apply_to_test_results(TestResult.objects.all())

            # Calculate effectiveness - filter out zero total to avoid division by zero
            effectiveness_data = filtered_results.values('antibiotic__name').annotate(
                effective=Count('id', filter=Q(sensitivity__iexact='sensitive')),
                total=Count('id')
            ).filter(total__gt=0).annotate(
                effectiveness=100.0 * F('effective') / F('total')
            ).order_by('-effectiveness')[:top_n]

            # Format data
            data = []
            for item in effectiveness_data:
                if item['antibiotic__name'] and item['total'] > 0:
                    data.append({
                        'antibiotic': item['antibiotic__name'],
                        'effectiveness': round(item['effectiveness'], 2),
                        'total_tests': item['total'],
                        'effective_tests': item['effective']
                    })

            return data
        except Exception as e:
            logger.error(f"Error in get_antibiotic_effectiveness: {str(e)}", exc_info=True)
            return []
    
    def get_resistance_over_time(self, group_by: str = 'month') -> List[Dict[str, Any]]:
        """
        Get resistance trend over time with applied filters.

        Args:
            group_by: Grouping period ('month' or 'date')

        Returns:
            List of dictionaries with resistance trends
        """
        try:
            from results.models import TestResult

            # Apply filters
            filtered_results = self.filter_engine.apply_to_test_results(
                TestResult.objects.filter(sensitivity__iexact='resistant')
            )

            # Group by time period
            if group_by == 'month':
                resistance_trend = filtered_results.annotate(
                    period=TruncMonth('sample__date')
                ).values('period').annotate(
                    count=Count('id')
                ).order_by('period')

                # Format data
                data = []
                for item in resistance_trend:
                    if item['period']:
                        data.append({
                            'month': item['period'].strftime('%Y-%m'),
                            'resistance': item['count']
                        })
            else:
                resistance_trend = filtered_results.annotate(
                    period=TruncDate('sample__date')
                ).values('period').annotate(
                    count=Count('id')
                ).order_by('period')

                # Format data
                data = []
                for item in resistance_trend:
                    if item['period']:
                        data.append({
                            'date': item['period'].strftime('%Y-%m-%d'),
                            'resistance': item['count']
                        })

            return data
        except Exception as e:
            logger.error(f"Error in get_resistance_over_time: {str(e)}", exc_info=True)
            return []
    
    def get_resistance_heatmap(self) -> List[Dict[str, Any]]:
        """
        Get resistance heatmap data with applied filters.

        Returns:
            List of dictionaries with heatmap data
        """
        try:
            from results.models import TestResult

            # Apply filters
            filtered_results = self.filter_engine.apply_to_test_results(TestResult.objects.all())

            # Get all combinations of bacteria and antibiotics with their resistance rates
            heatmap_data = filtered_results.values(
                'sample__bacteria__name',
                'antibiotic__name'
            ).annotate(
                total_tests=Count('id'),
                resistant_count=Count('id', filter=Q(sensitivity__iexact='resistant')),
                sensitive_count=Count('id', filter=Q(sensitivity__iexact='sensitive')),
                intermediate_count=Count('id', filter=Q(sensitivity__iexact='intermediate'))
            )

            # Calculate resistance percentage
            data = []
            for item in heatmap_data:
                if item['sample__bacteria__name'] and item['antibiotic__name'] and item['total_tests'] > 0:
                    resistance_percentage = (item['resistant_count'] / item['total_tests']) * 100

                    data.append({
                        'bacteria': item['sample__bacteria__name'],
                        'antibiotic': item['antibiotic__name'],
                        'resistance': round(resistance_percentage / 100, 2),  # Convert to decimal
                        'total_tests': item['total_tests'],
                        'resistant_count': item['resistant_count'],
                        'sensitive_count': item['sensitive_count'],
                        'intermediate_count': item['intermediate_count']
                    })

            return data
        except Exception as e:
            logger.error(f"Error in get_resistance_heatmap: {str(e)}", exc_info=True)
            return []
    
    def get_bacteria_statistics(self, bacteria_name: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific bacteria with applied filters.
        
        Args:
            bacteria_name: Name of the bacteria
            
        Returns:
            Dictionary with bacteria statistics
        """
        from results.models import TestResult
        from .data_normalization import normalize_bacteria_name
        
        normalized_name = normalize_bacteria_name(bacteria_name)
        
        # Apply filters and bacteria filter
        filtered_results = self.filter_engine.apply_to_test_results(
            TestResult.objects.filter(sample__bacteria__name__iexact=normalized_name)
        )
        
        total_tests = filtered_results.count()
        
        if total_tests == 0:
            return {
                'bacteria': bacteria_name,
                'total_tests': 0,
                'antibiotics_tested': 0,
                'resistance_rate': 0,
                'sensitivity_rate': 0,
                'intermediate_rate': 0
            }
        
        resistant_count = filtered_results.filter(sensitivity__iexact='resistant').count()
        sensitive_count = filtered_results.filter(sensitivity__iexact='sensitive').count()
        intermediate_count = filtered_results.filter(sensitivity__iexact='intermediate').count()
        
        antibiotics_tested = filtered_results.values('antibiotic').distinct().count()
        
        return {
            'bacteria': bacteria_name,
            'total_tests': total_tests,
            'antibiotics_tested': antibiotics_tested,
            'resistance_rate': round((resistant_count / total_tests) * 100, 2),
            'sensitivity_rate': round((sensitive_count / total_tests) * 100, 2),
            'intermediate_rate': round((intermediate_count / total_tests) * 100, 2),
            'resistant_count': resistant_count,
            'sensitive_count': sensitive_count,
            'intermediate_count': intermediate_count
        }
    
    def get_antibiotic_recommendations(self, bacteria_name: str, top_n: int = 10) -> Dict[str, Any]:
        """
        Get antibiotic recommendations for a specific bacteria with applied filters.
        This reads ALL data from the database, not just a subset.
        
        Args:
            bacteria_name: Name of the bacteria
            top_n: Number of top recommendations to return (None for all)
            
        Returns:
            Dictionary with recommendations
        """
        from results.models import TestResult
        from antibiotics.models import Antibiotic
        from .data_normalization import normalize_bacteria_name
        
        normalized_name = normalize_bacteria_name(bacteria_name)
        
        # Apply filters and bacteria filter
        filtered_results = self.filter_engine.apply_to_test_results(
            TestResult.objects.filter(sample__bacteria__name__iexact=normalized_name)
        )
        
        # Get all antibiotics (not just those with test results)
        all_antibiotics = Antibiotic.objects.all()
        
        recommendations = []
        for antibiotic in all_antibiotics:
            # Get test results for this antibiotic
            antibiotic_results = filtered_results.filter(antibiotic=antibiotic)
            
            total_tests = antibiotic_results.count()
            sensitive_count = antibiotic_results.filter(sensitivity__iexact='sensitive').count()
            
            # Calculate effectiveness
            effectiveness = (sensitive_count / total_tests * 100) if total_tests > 0 else 0
            
            recommendations.append({
                'antibiotic': antibiotic.name,
                'effectiveness': round(effectiveness, 2),
                'total_tests': total_tests,
                'sensitive_cases': sensitive_count,
                'category': antibiotic.category,
                'mechanism': antibiotic.mechanism
            })
        
        # Sort by effectiveness
        recommendations.sort(key=lambda x: x['effectiveness'], reverse=True)
        
        # Return top N or all
        result_recommendations = recommendations[:top_n] if top_n else recommendations
        
        return {
            'bacteria': bacteria_name,
            'recommendations': result_recommendations,
            'total_antibiotics': len(all_antibiotics),
            'tested_antibiotics': len([r for r in recommendations if r['total_tests'] > 0])
        }
    
    def get_department_statistics(self) -> List[Dict[str, Any]]:
        """
        Get statistics by department with applied filters.
        
        Returns:
            List of dictionaries with department statistics
        """
        from samples.models import Sample
        
        # Apply filters
        filtered_samples = self.filter_engine.apply_to_samples(Sample.objects.all())
        
        # Get department statistics
        dept_stats = filtered_samples.values('department').annotate(
            sample_count=Count('id')
        ).order_by('-sample_count')
        
        data = []
        for item in dept_stats:
            if item['department']:
                data.append({
                    'department': item['department'],
                    'sample_count': item['sample_count']
                })
        
        return data
    
    def get_filtered_results(self) -> 'QuerySet':
        """
        Get filtered test results queryset.
        
        Returns:
            Filtered TestResult queryset
        """
        from results.models import TestResult
        
        return self.filter_engine.apply_to_test_results(
            TestResult.objects.select_related('sample', 'sample__bacteria', 'antibiotic').all()
        )
    
    def get_filtered_samples(self) -> 'QuerySet':
        """
        Get filtered samples queryset.
        
        Returns:
            Filtered Sample queryset
        """
        from samples.models import Sample
        
        return self.filter_engine.apply_to_samples(
            Sample.objects.select_related('bacteria').all()
        )


def create_data_service(request) -> UnifiedDataService:
    """
    Create a data service from request parameters.
    
    Args:
        request: Django request object
        
    Returns:
        UnifiedDataService instance
    """
    from .filters import create_filter_engine
    
    filter_engine = create_filter_engine(request)
    return UnifiedDataService(filter_engine)
