"""
Unified Filter Engine
Provides centralized filtering logic for all data queries.
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
from django.db.models import QuerySet, Q
from .data_normalization import normalize_bacteria_name, normalize_antibiotic_name, normalize_department_name
import logging

logger = logging.getLogger(__name__)


class GlobalFilterEngine:
    """
    Global filter engine that provides consistent filtering across all views.
    All data queries should use this engine to ensure consistency.
    """
    
    def __init__(self, filters: Dict[str, Any] = None):
        """
        Initialize the filter engine with filter parameters.
        
        Args:
            filters: Dictionary of filter parameters
                - date_from: Start date (string or date object)
                - date_to: End date (string or date object)
                - bacteria: Bacteria name (case-insensitive)
                - department: Department name (case-insensitive)
                - antibiotic: Antibiotic name (case-insensitive)
                - sensitivity: Sensitivity value (sensitive/intermediate/resistant)
                - hospital: Hospital name
        """
        self.filters = filters or {}
        self._validate_filters()
    
    def _validate_filters(self):
        """Validate and normalize filter parameters."""
        # Normalize date filters
        if 'date_from' in self.filters and self.filters['date_from']:
            self.filters['date_from'] = self._parse_date(self.filters['date_from'])
        
        if 'date_to' in self.filters and self.filters['date_to']:
            self.filters['date_to'] = self._parse_date(self.filters['date_to'])
        
        # Normalize text filters
        if 'bacteria' in self.filters and self.filters['bacteria']:
            if self.filters['bacteria'].lower() != 'all':
                self.filters['bacteria'] = normalize_bacteria_name(self.filters['bacteria'])
            else:
                self.filters['bacteria'] = None
        
        if 'antibiotic' in self.filters and self.filters['antibiotic']:
            if self.filters['antibiotic'].lower() != 'all':
                self.filters['antibiotic'] = normalize_antibiotic_name(self.filters['antibiotic'])
            else:
                self.filters['antibiotic'] = None
        
        if 'department' in self.filters and self.filters['department']:
            if self.filters['department'].lower() != 'all':
                self.filters['department'] = normalize_department_name(self.filters['department'])
            else:
                self.filters['department'] = None
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """
        Parse date from various formats.
        
        Args:
            date_value: Date value (string, date, or datetime)
            
        Returns:
            date object or None
        """
        if isinstance(date_value, date):
            return date_value
        
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            try:
                # Try parsing ISO format (YYYY-MM-DD)
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # Try parsing other common formats
                    return datetime.strptime(date_value, '%m/%d/%Y').date()
                except ValueError:
                    logger.warning(f"Could not parse date: {date_value}")
                    return None
        
        return None
    
    def apply_to_samples(self, queryset: QuerySet) -> QuerySet:
        """
        Apply filters to a Sample queryset.
        
        Args:
            queryset: Sample queryset to filter
            
        Returns:
            Filtered queryset
        """
        # Date range filter
        if self.filters.get('date_from'):
            queryset = queryset.filter(date__gte=self.filters['date_from'])
        
        if self.filters.get('date_to'):
            queryset = queryset.filter(date__lte=self.filters['date_to'])
        
        # Bacteria filter (case-insensitive)
        if self.filters.get('bacteria'):
            queryset = queryset.filter(bacteria__name__iexact=self.filters['bacteria'])
        
        # Department filter (case-insensitive)
        if self.filters.get('department'):
            queryset = queryset.filter(department__iexact=self.filters['department'])
        
        # Hospital filter
        if self.filters.get('hospital'):
            queryset = queryset.filter(hospital__icontains=self.filters['hospital'])
        
        return queryset
    
    def apply_to_test_results(self, queryset: QuerySet) -> QuerySet:
        """
        Apply filters to a TestResult queryset.
        
        Args:
            queryset: TestResult queryset to filter
            
        Returns:
            Filtered queryset
        """
        # Date range filter (through sample relationship)
        if self.filters.get('date_from'):
            queryset = queryset.filter(sample__date__gte=self.filters['date_from'])
        
        if self.filters.get('date_to'):
            queryset = queryset.filter(sample__date__lte=self.filters['date_to'])
        
        # Bacteria filter (case-insensitive, through sample relationship)
        if self.filters.get('bacteria'):
            queryset = queryset.filter(sample__bacteria__name__iexact=self.filters['bacteria'])
        
        # Department filter (case-insensitive, through sample relationship)
        if self.filters.get('department'):
            queryset = queryset.filter(sample__department__iexact=self.filters['department'])
        
        # Hospital filter (through sample relationship)
        if self.filters.get('hospital'):
            queryset = queryset.filter(sample__hospital__icontains=self.filters['hospital'])
        
        # Antibiotic filter (case-insensitive)
        if self.filters.get('antibiotic'):
            queryset = queryset.filter(antibiotic__name__iexact=self.filters['antibiotic'])
        
        # Sensitivity filter
        if self.filters.get('sensitivity'):
            queryset = queryset.filter(sensitivity__iexact=self.filters['sensitivity'])
        
        return queryset
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Get a summary of active filters.
        
        Returns:
            Dictionary with filter summary
        """
        active_filters = {}
        
        if self.filters.get('date_from'):
            active_filters['date_from'] = str(self.filters['date_from'])
        
        if self.filters.get('date_to'):
            active_filters['date_to'] = str(self.filters['date_to'])
        
        if self.filters.get('bacteria'):
            active_filters['bacteria'] = self.filters['bacteria']
        
        if self.filters.get('department'):
            active_filters['department'] = self.filters['department']
        
        if self.filters.get('antibiotic'):
            active_filters['antibiotic'] = self.filters['antibiotic']
        
        if self.filters.get('sensitivity'):
            active_filters['sensitivity'] = self.filters['sensitivity']
        
        if self.filters.get('hospital'):
            active_filters['hospital'] = self.filters['hospital']
        
        return {
            'active_filters': active_filters,
            'filter_count': len(active_filters),
            'has_filters': len(active_filters) > 0
        }
    
    def build_query_params(self) -> str:
        """
        Build URL query parameters from filters.
        
        Returns:
            Query parameter string
        """
        params = []
        
        if self.filters.get('date_from'):
            params.append(f"date_from={self.filters['date_from']}")
        
        if self.filters.get('date_to'):
            params.append(f"date_to={self.filters['date_to']}")
        
        if self.filters.get('bacteria'):
            params.append(f"bacteria={self.filters['bacteria']}")
        
        if self.filters.get('department'):
            params.append(f"department={self.filters['department']}")
        
        if self.filters.get('antibiotic'):
            params.append(f"antibiotic={self.filters['antibiotic']}")
        
        if self.filters.get('sensitivity'):
            params.append(f"sensitivity={self.filters['sensitivity']}")
        
        if self.filters.get('hospital'):
            params.append(f"hospital={self.filters['hospital']}")
        
        return '&'.join(params) if params else ''


def create_filter_engine(request) -> GlobalFilterEngine:
    """
    Create a filter engine from request parameters.
    
    Args:
        request: Django request object
        
    Returns:
        GlobalFilterEngine instance
    """
    filters = {}
    
    # Extract filter parameters from request
    if hasattr(request, 'query_params'):
        # DRF request
        params = request.query_params
    else:
        # Standard Django request
        params = request.GET
    
    # Date filters
    if params.get('date_from') or params.get('start_date'):
        filters['date_from'] = params.get('date_from') or params.get('start_date')
    
    if params.get('date_to') or params.get('end_date'):
        filters['date_to'] = params.get('date_to') or params.get('end_date')
    
    # Entity filters
    if params.get('bacteria'):
        filters['bacteria'] = params.get('bacteria')
    
    if params.get('department'):
        filters['department'] = params.get('department')
    
    if params.get('antibiotic'):
        filters['antibiotic'] = params.get('antibiotic')
    
    if params.get('sensitivity'):
        filters['sensitivity'] = params.get('sensitivity')
    
    if params.get('hospital'):
        filters['hospital'] = params.get('hospital')
    
    return GlobalFilterEngine(filters)


def apply_filters_to_queryset(queryset: QuerySet, filters: Dict[str, Any], 
                               queryset_type: str = 'test_results') -> QuerySet:
    """
    Convenience function to apply filters to a queryset.
    
    Args:
        queryset: Queryset to filter
        filters: Dictionary of filter parameters
        queryset_type: Type of queryset ('samples' or 'test_results')
        
    Returns:
        Filtered queryset
    """
    engine = GlobalFilterEngine(filters)
    
    if queryset_type == 'samples':
        return engine.apply_to_samples(queryset)
    elif queryset_type == 'test_results':
        return engine.apply_to_test_results(queryset)
    else:
        raise ValueError(f"Unknown queryset type: {queryset_type}")
