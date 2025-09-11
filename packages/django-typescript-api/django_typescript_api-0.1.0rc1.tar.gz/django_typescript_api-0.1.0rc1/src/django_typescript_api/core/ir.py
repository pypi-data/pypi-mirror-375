from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

@dataclass
class FieldConstraint:
    """Represents validation constraints for a field."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None  # Regex pattern
    choices: Optional[List[tuple]] = None

@dataclass
class FieldNode:
    """Represents a field in a Django model."""
    name: str
    django_type: str
    ts_type: str
    nullable: bool = False
    is_relation: bool = False
    related_model: Optional[str] = None
    help_text: Optional[str] = None
    constraints: Optional[FieldConstraint] = None
    default: Optional[Any] = None
    unique: bool = False
    blank: bool = False

@dataclass
class ModelNode:
    """Represents a Django model for TypeScript generation."""
    name: str
    app_label: str
    fields: List[FieldNode] = field(default_factory=list)
    docstring: Optional[str] = None
    verbose_name: Optional[str] = None
    verbose_name_plural: Optional[str] = None

@dataclass
class IntermediateRepresentation:
    """Container for all generated nodes."""
    models: List[ModelNode] = field(default_factory=list)
    
    def add_model(self, model_node: ModelNode):
        """Add a model node to the IR."""
        self.models.append(model_node)
    
    def get_model(self, name: str) -> Optional[ModelNode]:
        """Get a model by name."""
        for model in self.models:
            if model.name == name:
                return model
        return None
    
    def get_models_by_app(self, app_label: str) -> List[ModelNode]:
        """Get all models for a specific app."""
        return [model for model in self.models if model.app_label == app_label]