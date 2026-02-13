"""
Data Normalization Utilities
Provides functions to normalize text data for consistent storage and querying.
"""

import re
from typing import Optional, List
from django.db.models import Q


def normalize_text(text: str) -> str:
    """
    Normalize text by converting to lowercase, removing extra spaces, and trimming.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    normalized = text.lower()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Trim leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def normalize_bacteria_name(name: str) -> str:
    """
    Normalize bacteria name with special handling for common patterns.
    
    Args:
        name: Bacteria name to normalize
        
    Returns:
        Normalized bacteria name
    """
    if not name:
        return ""
    
    # Basic normalization
    normalized = normalize_text(name)
    
    # Remove common prefixes/suffixes that might vary
    # e.g., "bacteria:", "organism:", etc.
    patterns_to_remove = [
        r'^bacteria:\s*',
        r'^organism:\s*',
        r'^pathogen:\s*',
    ]
    
    for pattern in patterns_to_remove:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Trim again after pattern removal
    normalized = normalized.strip()
    
    return normalized


def normalize_antibiotic_name(name: str) -> str:
    """
    Normalize antibiotic name with special handling for common patterns.
    
    Args:
        name: Antibiotic name to normalize
        
    Returns:
        Normalized antibiotic name
    """
    if not name:
        return ""
    
    # Basic normalization
    normalized = normalize_text(name)
    
    # Remove common suffixes that might vary
    # e.g., dosage information, formulation details
    patterns_to_remove = [
        r'\s*\(\d+\s*mg\)',  # (500 mg)
        r'\s*\d+\s*mg',      # 500 mg
        r'\s*tablet.*$',     # tablet, tablets
        r'\s*capsule.*$',    # capsule, capsules
    ]
    
    for pattern in patterns_to_remove:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Trim again after pattern removal
    normalized = normalized.strip()
    
    return normalized


def normalize_department_name(name: str) -> str:
    """
    Normalize department name.
    
    Args:
        name: Department name to normalize
        
    Returns:
        Normalized department name
    """
    if not name:
        return ""
    
    # Basic normalization
    normalized = normalize_text(name)
    
    # Standardize common abbreviations
    abbreviations = {
        'icu': 'intensive care unit',
        'er': 'emergency room',
        'ed': 'emergency department',
        'or': 'operating room',
        'ob/gyn': 'obstetrics and gynecology',
        'obgyn': 'obstetrics and gynecology',
    }
    
    if normalized in abbreviations:
        normalized = abbreviations[normalized]
    
    return normalized


def create_case_insensitive_query(field_name: str, value: str) -> Q:
    """
    Create a case-insensitive query for a field.
    
    Args:
        field_name: Name of the field to query
        value: Value to search for
        
    Returns:
        Django Q object for case-insensitive query
    """
    if not value:
        return Q()
    
    normalized_value = normalize_text(value)
    return Q(**{f"{field_name}__iexact": normalized_value})


def find_similar_names(name: str, existing_names: List[str], threshold: float = 0.8) -> List[str]:
    """
    Find similar names in a list using fuzzy matching.
    Useful for identifying potential duplicates.
    
    Args:
        name: Name to search for
        existing_names: List of existing names to compare against
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        List of similar names
    """
    from difflib import SequenceMatcher
    
    normalized_name = normalize_text(name)
    similar_names = []
    
    for existing_name in existing_names:
        normalized_existing = normalize_text(existing_name)
        
        # Calculate similarity ratio
        ratio = SequenceMatcher(None, normalized_name, normalized_existing).ratio()
        
        if ratio >= threshold:
            similar_names.append(existing_name)
    
    return similar_names


def get_canonical_name(name: str, name_type: str = 'bacteria') -> str:
    """
    Get the canonical (standardized) name for a bacteria or antibiotic.
    This function will be enhanced to use master reference tables.
    
    Args:
        name: Name to canonicalize
        name_type: Type of name ('bacteria' or 'antibiotic')
        
    Returns:
        Canonical name
    """
    if name_type == 'bacteria':
        return normalize_bacteria_name(name)
    elif name_type == 'antibiotic':
        return normalize_antibiotic_name(name)
    else:
        return normalize_text(name)


def extract_bacteria_from_text(text: str) -> Optional[str]:
    """
    Extract bacteria name from free text (useful for OCR processing).
    
    Args:
        text: Text containing bacteria name
        
    Returns:
        Extracted bacteria name or None
    """
    if not text:
        return None
    
    # Common patterns for bacteria names
    patterns = [
        r'bacteria:\s*([^\n\r]+)',
        r'organism:\s*([^\n\r]+)',
        r'bacterium:\s*([^\n\r]+)',
        r'pathogen:\s*([^\n\r]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bacteria_name = match.group(1).strip()
            return normalize_bacteria_name(bacteria_name)
    
    return None


def validate_sensitivity_value(value: str) -> str:
    """
    Validate and normalize sensitivity values.
    
    Args:
        value: Sensitivity value to validate
        
    Returns:
        Normalized sensitivity value ('sensitive', 'intermediate', or 'resistant')
    """
    if not value:
        return 'unknown'
    
    normalized = normalize_text(value)
    
    # Map common variations to standard values
    sensitivity_map = {
        's': 'sensitive',
        'sensitive': 'sensitive',
        'susceptible': 'sensitive',
        'i': 'intermediate',
        'intermediate': 'intermediate',
        'r': 'resistant',
        'resistant': 'resistant',
        'resistance': 'resistant',
    }
    
    return sensitivity_map.get(normalized, 'unknown')


def batch_normalize_names(names: List[str], name_type: str = 'bacteria') -> dict:
    """
    Normalize a batch of names and return mapping of original to normalized.
    
    Args:
        names: List of names to normalize
        name_type: Type of names ('bacteria' or 'antibiotic')
        
    Returns:
        Dictionary mapping original names to normalized names
    """
    mapping = {}
    
    for name in names:
        if name:
            normalized = get_canonical_name(name, name_type)
            mapping[name] = normalized
    
    return mapping


def identify_duplicates(names: List[str]) -> dict:
    """
    Identify duplicate names (case-insensitive).
    
    Args:
        names: List of names to check
        
    Returns:
        Dictionary mapping normalized names to list of original variations
    """
    duplicates = {}
    
    for name in names:
        if not name:
            continue
            
        normalized = normalize_text(name)
        
        if normalized not in duplicates:
            duplicates[normalized] = []
        
        if name not in duplicates[normalized]:
            duplicates[normalized].append(name)
    
    # Filter to only return actual duplicates (more than one variation)
    return {k: v for k, v in duplicates.items() if len(v) > 1}
