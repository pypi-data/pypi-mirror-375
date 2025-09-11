"""
Utility functions for idtap
"""
import humps
from typing import Dict, Any, List, Union


def selective_decamelize(obj: Dict[str, Any], preserve_keys: List[str] = None) -> Dict[str, Any]:
    """
    Decamelize dictionary keys selectively, preserving certain nested structures.
    
    Args:
        obj: Dictionary to decamelize
        preserve_keys: List of top-level keys whose nested content should not be decamelized
        
    Returns:
        Dictionary with camelCase keys converted to snake_case, except for preserved nested structures
    """
    if preserve_keys is None:
        preserve_keys = [
            'categorization_grid', 
            'categorizationGrid',
            'section_categorization',
            'sectionCategorization', 
            'ad_hoc_categorization',
            'adHocCategorization',
            'rule_set',
            'ruleSet',
            'tuning'
        ]
    
    # First convert top-level keys to snake_case
    result = {}
    for key, value in obj.items():
        snake_key = humps.decamelize(key)
        
        # Check if this key should preserve its nested structure
        if key in preserve_keys or snake_key in preserve_keys:
            result[snake_key] = value
        else:
            # For other keys, recursively decamelize if it's a dict
            if isinstance(value, dict):
                result[snake_key] = humps.decamelize(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                result[snake_key] = [humps.decamelize(item) if isinstance(item, dict) else item for item in value]
            else:
                result[snake_key] = value
    
    return result


def to_camel_case(obj: Union[Dict[str, Any], List, Any]) -> Union[Dict[str, Any], List, Any]:
    """
    Convert dictionary keys from snake_case to camelCase.
    
    Args:
        obj: Object to convert (dict, list, or other)
        
    Returns:
        Object with camelCase keys
    """
    return humps.camelize(obj)


def to_snake_case(obj: Union[Dict[str, Any], List, Any]) -> Union[Dict[str, Any], List, Any]:
    """
    Convert dictionary keys from camelCase to snake_case.
    
    Args:
        obj: Object to convert (dict, list, or other)
        
    Returns:
        Object with snake_case keys
    """
    return humps.decamelize(obj)
