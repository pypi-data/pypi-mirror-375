from django.apps import apps
from typing import List, Optional
from .ir import ModelNode, FieldNode, FieldConstraint, IntermediateRepresentation
from .strategies import TypeMapper

class ModelInspector:
    """Inspector for Django models with enhanced field information."""
    
    def __init__(self, type_mapper: Optional[TypeMapper] = None):
        self.type_mapper = type_mapper or TypeMapper()
    
    def inspect_models(self, app_labels: Optional[List[str]] = None) -> IntermediateRepresentation:
        """Inspect all models in the specified apps."""
        ir = IntermediateRepresentation()
        
        if app_labels is None:
            app_labels = [app.label for app in apps.get_app_configs()]
        
        for app_label in app_labels:
            try:
                app_config = apps.get_app_config(app_label)
                for model in app_config.get_models():
                    model_node = self._inspect_model(model)
                    ir.add_model(model_node)
            except LookupError:
                # Skip apps that don't exist or can't be loaded
                continue
        
        return ir
    
    def _inspect_model(self, model) -> ModelNode:
        """Inspect a single Django model with enhanced metadata."""
        model_node = ModelNode(
            name=model.__name__,
            app_label=model._meta.app_label,
            docstring=model.__doc__,
            verbose_name=getattr(model._meta, 'verbose_name', None),
            verbose_name_plural=getattr(model._meta, 'verbose_name_plural', None)
        )
        
        for field in model._meta.get_fields():
            # Skip reverse relations and auto-created fields
            if field.auto_created or field.is_relation and field.many_to_many:
                continue
            
            field_node = self._inspect_field(field)
            model_node.fields.append(field_node)
        
        return model_node
    
    def _inspect_field(self, field) -> FieldNode:
        """Inspect a single Django field with enhanced metadata."""
        ts_type = self.type_mapper.get_ts_type(field)
        nullable = self.type_mapper.is_field_nullable(field)
        constraints = self.type_mapper.get_field_constraints(field)
        
        # Get help text
        help_text = getattr(field, 'help_text', None)
        if help_text:
            help_text = str(help_text).strip()
        
        # Get default value if it's a simple value
        default_value = None
        if hasattr(field, 'default') and field.default not in [None, ...]:
            if not callable(field.default):
                default_value = field.default
        
        # Check if it's a relation field
        is_relation = field.is_relation
        related_model = None
        if is_relation and field.related_model:
            related_model = field.related_model.__name__
        
        return FieldNode(
            name=field.name,
            django_type=field.get_internal_type(),
            ts_type=ts_type,
            nullable=nullable,
            is_relation=is_relation,
            related_model=related_model,
            help_text=help_text,
            constraints=constraints,
            default=default_value,
            unique=getattr(field, 'unique', False),
            blank=getattr(field, 'blank', False)
        )