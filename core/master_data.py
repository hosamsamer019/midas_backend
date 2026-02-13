"""
Master Data Management
Handles master reference tables for bacteria and antibiotics.
"""

from typing import Optional, List, Dict, Tuple, TYPE_CHECKING
from django.db import transaction
from django.db.models import Q
import logging

if TYPE_CHECKING:
    from bacteria.models import Bacteria
    from antibiotics.models import Antibiotic

logger = logging.getLogger(__name__)


class MasterDataManager:
    """
    Manages master reference data for bacteria and antibiotics.
    Provides methods to get canonical names and manage aliases.
    """
    
    def __init__(self):
        """Initialize the master data manager."""
        self._bacteria_cache = {}
        self._antibiotic_cache = {}
    
    def get_or_create_bacteria(self, name: str, bacteria_type: str = None, 
                               gram_stain: str = None, source: str = None) -> 'Bacteria':
        """
        Get or create a bacteria record with normalized name.
        
        Args:
            name: Bacteria name
            bacteria_type: Type of bacteria (gram_positive/gram_negative)
            gram_stain: Gram stain result
            source: Source of the bacteria
            
        Returns:
            Bacteria model instance
        """
        from bacteria.models import Bacteria
        from .data_normalization import normalize_bacteria_name
        
        if not name:
            raise ValueError("Bacteria name cannot be empty")
        
        normalized_name = normalize_bacteria_name(name)
        
        # Check cache first
        if normalized_name in self._bacteria_cache:
            return self._bacteria_cache[normalized_name]
        
        # Try to find existing bacteria (case-insensitive)
        bacteria = Bacteria.objects.filter(
            Q(name__iexact=normalized_name) | 
            Q(name__iexact=name)
        ).first()
        
        if bacteria:
            # Update cache
            self._bacteria_cache[normalized_name] = bacteria
            return bacteria
        
        # Create new bacteria
        bacteria = Bacteria.objects.create(
            name=normalized_name,
            bacteria_type=bacteria_type or 'gram_negative',
            gram_stain=gram_stain or 'Unknown',
            source=source or 'Unknown'
        )
        
        # Update cache
        self._bacteria_cache[normalized_name] = bacteria
        
        logger.info(f"Created new bacteria: {normalized_name}")
        return bacteria
    
    def get_or_create_antibiotic(self, name: str, category: str = None,
                                 mechanism: str = None, common_use: str = None) -> 'Antibiotic':
        """
        Get or create an antibiotic record with normalized name.
        
        Args:
            name: Antibiotic name
            category: Antibiotic category
            mechanism: Mechanism of action
            common_use: Common use description
            
        Returns:
            Antibiotic model instance
        """
        from antibiotics.models import Antibiotic
        from .data_normalization import normalize_antibiotic_name
        
        if not name:
            raise ValueError("Antibiotic name cannot be empty")
        
        normalized_name = normalize_antibiotic_name(name)
        
        # Check cache first
        if normalized_name in self._antibiotic_cache:
            return self._antibiotic_cache[normalized_name]
        
        # Try to find existing antibiotic (case-insensitive)
        antibiotic = Antibiotic.objects.filter(
            Q(name__iexact=normalized_name) | 
            Q(name__iexact=name)
        ).first()
        
        if antibiotic:
            # Update cache
            self._antibiotic_cache[normalized_name] = antibiotic
            return antibiotic
        
        # Create new antibiotic
        antibiotic = Antibiotic.objects.create(
            name=normalized_name,
            category=category or 'Unknown',
            mechanism=mechanism or 'Unknown',
            common_use=common_use or 'Unknown'
        )
        
        # Update cache
        self._antibiotic_cache[normalized_name] = antibiotic
        
        logger.info(f"Created new antibiotic: {normalized_name}")
        return antibiotic
    
    def find_bacteria_by_name(self, name: str) -> Optional['Bacteria']:
        """
        Find bacteria by name (case-insensitive).
        
        Args:
            name: Bacteria name to search for
            
        Returns:
            Bacteria instance or None
        """
        from bacteria.models import Bacteria
        from .data_normalization import normalize_bacteria_name
        
        if not name:
            return None
        
        normalized_name = normalize_bacteria_name(name)
        
        # Check cache first
        if normalized_name in self._bacteria_cache:
            return self._bacteria_cache[normalized_name]
        
        # Search database (case-insensitive)
        bacteria = Bacteria.objects.filter(
            Q(name__iexact=normalized_name) | 
            Q(name__iexact=name)
        ).first()
        
        if bacteria:
            self._bacteria_cache[normalized_name] = bacteria
        
        return bacteria
    
    def find_antibiotic_by_name(self, name: str) -> Optional['Antibiotic']:
        """
        Find antibiotic by name (case-insensitive).
        
        Args:
            name: Antibiotic name to search for
            
        Returns:
            Antibiotic instance or None
        """
        from antibiotics.models import Antibiotic
        from .data_normalization import normalize_antibiotic_name
        
        if not name:
            return None
        
        normalized_name = normalize_antibiotic_name(name)
        
        # Check cache first
        if normalized_name in self._antibiotic_cache:
            return self._antibiotic_cache[normalized_name]
        
        # Search database (case-insensitive)
        antibiotic = Antibiotic.objects.filter(
            Q(name__iexact=normalized_name) | 
            Q(name__iexact=name)
        ).first()
        
        if antibiotic:
            self._antibiotic_cache[normalized_name] = antibiotic
        
        return antibiotic
    
    def get_all_bacteria_names(self) -> List[str]:
        """
        Get all unique bacteria names from the database.
        
        Returns:
            List of bacteria names
        """
        from bacteria.models import Bacteria
        
        return list(Bacteria.objects.values_list('name', flat=True).distinct())
    
    def get_all_antibiotic_names(self) -> List[str]:
        """
        Get all unique antibiotic names from the database.
        
        Returns:
            List of antibiotic names
        """
        from antibiotics.models import Antibiotic
        
        return list(Antibiotic.objects.values_list('name', flat=True).distinct())
    
    def identify_bacteria_duplicates(self) -> Dict[str, List[str]]:
        """
        Identify potential duplicate bacteria entries.
        
        Returns:
            Dictionary mapping normalized names to list of variations
        """
        from .data_normalization import identify_duplicates
        
        bacteria_names = self.get_all_bacteria_names()
        return identify_duplicates(bacteria_names)
    
    def identify_antibiotic_duplicates(self) -> Dict[str, List[str]]:
        """
        Identify potential duplicate antibiotic entries.
        
        Returns:
            Dictionary mapping normalized names to list of variations
        """
        from .data_normalization import identify_duplicates
        
        antibiotic_names = self.get_all_antibiotic_names()
        return identify_duplicates(antibiotic_names)
    
    @transaction.atomic
    def merge_bacteria_duplicates(self, keep_name: str, merge_names: List[str]) -> Tuple[int, int]:
        """
        Merge duplicate bacteria entries into a single canonical entry.
        
        Args:
            keep_name: Name of the bacteria to keep
            merge_names: List of bacteria names to merge into keep_name
            
        Returns:
            Tuple of (samples_updated, bacteria_deleted)
        """
        from bacteria.models import Bacteria
        from samples.models import Sample
        
        # Find the bacteria to keep
        keep_bacteria = self.find_bacteria_by_name(keep_name)
        if not keep_bacteria:
            raise ValueError(f"Bacteria '{keep_name}' not found")
        
        samples_updated = 0
        bacteria_deleted = 0
        
        for merge_name in merge_names:
            if merge_name == keep_name:
                continue
            
            # Find bacteria to merge
            merge_bacteria = self.find_bacteria_by_name(merge_name)
            if not merge_bacteria:
                logger.warning(f"Bacteria '{merge_name}' not found, skipping")
                continue
            
            # Update all samples referencing the duplicate bacteria
            updated = Sample.objects.filter(bacteria=merge_bacteria).update(bacteria=keep_bacteria)
            samples_updated += updated
            
            # Delete the duplicate bacteria
            merge_bacteria.delete()
            bacteria_deleted += 1
            
            logger.info(f"Merged bacteria '{merge_name}' into '{keep_name}': {updated} samples updated")
        
        # Clear cache
        self._bacteria_cache.clear()
        
        return samples_updated, bacteria_deleted
    
    @transaction.atomic
    def merge_antibiotic_duplicates(self, keep_name: str, merge_names: List[str]) -> Tuple[int, int]:
        """
        Merge duplicate antibiotic entries into a single canonical entry.
        
        Args:
            keep_name: Name of the antibiotic to keep
            merge_names: List of antibiotic names to merge into keep_name
            
        Returns:
            Tuple of (results_updated, antibiotics_deleted)
        """
        from antibiotics.models import Antibiotic
        from results.models import TestResult
        
        # Find the antibiotic to keep
        keep_antibiotic = self.find_antibiotic_by_name(keep_name)
        if not keep_antibiotic:
            raise ValueError(f"Antibiotic '{keep_name}' not found")
        
        results_updated = 0
        antibiotics_deleted = 0
        
        for merge_name in merge_names:
            if merge_name == keep_name:
                continue
            
            # Find antibiotic to merge
            merge_antibiotic = self.find_antibiotic_by_name(merge_name)
            if not merge_antibiotic:
                logger.warning(f"Antibiotic '{merge_name}' not found, skipping")
                continue
            
            # Update all test results referencing the duplicate antibiotic
            updated = TestResult.objects.filter(antibiotic=merge_antibiotic).update(antibiotic=keep_antibiotic)
            results_updated += updated
            
            # Delete the duplicate antibiotic
            merge_antibiotic.delete()
            antibiotics_deleted += 1
            
            logger.info(f"Merged antibiotic '{merge_name}' into '{keep_name}': {updated} results updated")
        
        # Clear cache
        self._antibiotic_cache.clear()
        
        return results_updated, antibiotics_deleted
    
    def clear_cache(self):
        """Clear the internal cache."""
        self._bacteria_cache.clear()
        self._antibiotic_cache.clear()
        logger.info("Master data cache cleared")


# Global instance
master_data_manager = MasterDataManager()
