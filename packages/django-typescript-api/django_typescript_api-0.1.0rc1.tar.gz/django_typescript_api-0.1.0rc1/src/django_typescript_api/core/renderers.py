from pathlib import Path
from typing import List, Optional
from .ir import IntermediateRepresentation, ModelNode, FieldNode, FieldConstraint
from ..conf import config

class TypeScriptRenderer:
    """Renderer for generating TypeScript code from IR with JSDoc support."""
    
    def __init__(self, output_path: Optional[Path] = None):
        self.output_path = output_path or config.OUTPUT_PATH
    
    def render(self, ir: IntermediateRepresentation) -> str:
        """Render the complete IR to TypeScript code with enhanced documentation."""
        lines = config.CUSTOM_HEADERS.copy()
        
        # Render all models
        for model_node in ir.models:
            model_code = self._render_model(model_node)
            lines.extend(model_code)
            lines.append('')  # Add empty line between models
        
        return '\n'.join(lines)
    
    def _render_model(self, model_node: ModelNode) -> List[str]:
        """Render a single model to TypeScript interface with JSDoc."""
        lines = []
        
        # Add comprehensive JSDoc
        if config.INCLUDE_DOCS:
            lines.append('/**')
            if model_node.verbose_name:
                lines.append(f' * {model_node.verbose_name}')
                if model_node.verbose_name_plural:
                    lines.append(f' * Plural: {model_node.verbose_name_plural}')
                lines.append(' *')
            
            if model_node.docstring:
                for line in model_node.docstring.strip().split('\n'):
                    lines.append(f' * {line.strip()}')
                lines.append(' *')
            
            lines.append(f' * @interface {model_node.name}')
            lines.append(' */')
        
        lines.append(f'export interface {model_node.name} {{')
        
        for field in model_node.fields:
            field_lines = self._render_field(field)
            lines.extend(field_lines)
        
        lines.append('}')
        
        return lines
    
    def _render_field(self, field_node: FieldNode) -> List[str]:
        """Render a single field with JSDoc comments and validation hints."""
        lines = []
        indent = config.BASE_INDENTATION
        
        # Add field documentation
        if config.INCLUDE_DOCS and (field_node.help_text or field_node.constraints):
            lines.append(f'{indent}/**')
            
            if field_node.help_text:
                lines.append(f'{indent} * {field_node.help_text}')
                if field_node.constraints:
                    lines.append(f'{indent} *')
            
            if field_node.constraints:
                constraints = field_node.constraints
                if constraints.min_length is not None:
                    lines.append(f'{indent} * @minLength {constraints.min_length}')
                if constraints.max_length is not None:
                    lines.append(f'{indent} * @maxLength {constraints.max_length}')
                if constraints.min_value is not None:
                    lines.append(f'{indent} * @minimum {constraints.min_value}')
                if constraints.max_value is not None:
                    lines.append(f'{indent} * @maximum {constraints.max_value}')
                if constraints.pattern:
                    lines.append(f'{indent} * @pattern {constraints.pattern}')
                if constraints.choices:
                    choices_str = ', '.join([f"'{c[0]}'" for c in constraints.choices])
                    lines.append(f'{indent} * @enum {{{choices_str}}}')
            
            if field_node.unique:
                lines.append(f'{indent} * @unique')
            
            if field_node.default is not None:
                lines.append(f'{indent} * @default {field_node.default}')
            
            lines.append(f'{indent} */')
        
        # Render field definition
        nullable_indicator = '?' if field_node.nullable else ''
        field_line = f'{indent}{field_node.name}{nullable_indicator}: {field_node.ts_type};'
        
        # Add validation comments inline for simple cases
        if config.INCLUDE_VALIDATORS and field_node.constraints and not config.INCLUDE_DOCS:
            constraints = field_node.constraints
            comment_parts = []
            
            if constraints.min_length is not None:
                comment_parts.append(f'min: {constraints.min_length}')
            if constraints.max_length is not None:
                comment_parts.append(f'max: {constraints.max_length}')
            if constraints.min_value is not None:
                comment_parts.append(f'min: {constraints.min_value}')
            if constraints.max_value is not None:
                comment_parts.append(f'max: {constraints.max_value}')
            
            if comment_parts:
                field_line = field_line.replace(';', f'; // {", ".join(comment_parts)}')
        
        lines.append(field_line)
        
        return lines
    
    def write_to_file(self, ts_code: str):
        """Write TypeScript code to file with proper encoding."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(ts_code, encoding='utf-8')