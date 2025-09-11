from typing import Dict, List, Optional, Any
from .ir import FieldNode, FieldConstraint
from ..conf import config

class TypeMapper:
    """Maps Django field types to TypeScript types with validation support."""
    
    # Default type mappings
    DEFAULT_MAPPINGS = {
        'AutoField': 'number',
        'BigAutoField': 'number',
        'BigIntegerField': 'number',
        'BinaryField': 'string',
        'BooleanField': 'boolean',
        'CharField': 'string',
        'DateField': 'string',  # ISO string format
        'DateTimeField': 'string',  # ISO string format
        'DecimalField': 'number',
        'DurationField': 'string',
        'EmailField': 'string',
        'FileField': 'string',
        'FilePathField': 'string',
        'FloatField': 'number',
        'IntegerField': 'number',
        'GenericIPAddressField': 'string',
        'JSONField': 'any',
        'PositiveBigIntegerField': 'number',
        'PositiveIntegerField': 'number',
        'PositiveSmallIntegerField': 'number',
        'SlugField': 'string',
        'SmallIntegerField': 'number',
        'TextField': 'string',
        'TimeField': 'string',
        'URLField': 'string',
        'UUIDField': 'string',
    }
    
    def __init__(self):
        self.mappings = {**self.DEFAULT_MAPPINGS, **config.TYPE_MAPPINGS}
    
    def get_ts_type(self, django_field) -> str:
        """Get TypeScript type for a Django field."""
        field_type = django_field.get_internal_type()
        
        # Handle foreign keys and relations
        if field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']:
            related_model = django_field.related_model
            if related_model:
                return f"{related_model.__name__} | number"
            return 'number'
        
        # Handle choices fields - create union type
        if hasattr(django_field, 'choices') and django_field.choices:
            choices = [f"'{choice[0]}'" for choice in django_field.choices]
            return ' | '.join(choices)
        
        # Handle ArrayField if present (Django 3.1+)
        if field_type == 'ArrayField':
            base_field = getattr(django_field, 'base_field', None)
            if base_field:
                base_type = self.get_ts_type(base_field)
                return f"{base_type}[]"
            return 'any[]'
        
        # Return mapped type or fallback to any
        return self.mappings.get(field_type, 'any')
    
    def is_field_nullable(self, django_field) -> bool:
        """Check if a field is nullable."""
        return django_field.null or (hasattr(django_field, 'blank') and django_field.blank)
    
    def get_field_constraints(self, django_field) -> Optional[FieldConstraint]:
        """Extract validation constraints from Django field."""
        if not config.INCLUDE_VALIDATORS:
            return None
        
        constraints = FieldConstraint()
        
        # String length constraints
        if hasattr(django_field, 'max_length'):
            constraints.max_length = django_field.max_length
        if hasattr(django_field, 'min_length'):
            constraints.min_length = django_field.min_length
        
        # Numeric constraints
        if hasattr(django_field, 'min_value'):
            constraints.min_value = django_field.min_value
        if hasattr(django_field, 'max_value'):
            constraints.max_value = django_field.max_value
        
        # Choices
        if hasattr(django_field, 'choices') and django_field.choices:
            constraints.choices = django_field.choices
        
        # Regex pattern (for RegexField, EmailField, etc.)
        if hasattr(django_field, 'regex') and django_field.regex:
            constraints.pattern = django_field.regex.pattern
        
        # Check if any constraints were found
        has_constraints = any(
            getattr(constraints, attr) is not None 
            for attr in ['min_length', 'max_length', 'min_value', 'max_value', 'pattern', 'choices']
        )
        
        return constraints if has_constraints else None

class NamingStrategy:
    """Strategy for naming conventions."""
    
    @staticmethod
    def get_model_type_name(model_name: str) -> str:
        """Get the TypeScript interface name for a model."""
        return model_name
    
    @staticmethod
    def get_create_type_name(model_name: str) -> str:
        """Get the TypeScript type name for create operations."""
        return f"{model_name}Create"
    
    @staticmethod
    def get_update_type_name(model_name: str) -> str:
        """Get the TypeScript type name for update operations."""
        return f"{model_name}Update"
    
    @staticmethod
    def get_dto_type_name(model_name: str, operation: str) -> str:
        """Get DTO type name for specific operations."""
        return f"{model_name}{operation.capitalize()}DTO"