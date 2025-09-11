from django.core.management.base import BaseCommand
from django.apps import apps
from pathlib import Path
from typing import Any, Optional
import time

from django_typescript_api.core.inspectors import ModelInspector
from django_typescript_api.core.renderers import TypeScriptRenderer
from django_typescript_api.conf import config, reload_config

class Command(BaseCommand):
    help = 'Generate TypeScript interfaces from Django models with validation and documentation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            type=Path,
            help='Output path for generated TypeScript file',
        )
        parser.add_argument(
            '--apps', '-a',
            nargs='+',
            help='Specific apps to include (default: all installed apps)',
        )
        parser.add_argument(
            '--no-docs',
            action='store_true',
            help='Skip JSDoc documentation generation',
        )
        parser.add_argument(
            '--no-validators',
            action='store_true',
            help='Skip validation constraints',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output with detailed information',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without writing to file',
        )
    
    def handle(self, *args: Any, **options: Any):
        start_time = time.time()
        
        # Reload config in case settings changed
        reload_config()
        
        # Override config from command line options
        output_path = options.get('output') or config.OUTPUT_PATH
        apps_to_include = options.get('apps') or config.APPS_TO_INCLUDE
        
        if options.get('no_docs'):
            config.INCLUDE_DOCS = False
        if options.get('no_validators'):
            config.INCLUDE_VALIDATORS = False
        
        self.stdout.write('Starting enhanced TypeScript generation...')
        
        if options.get('verbose'):
            self.stdout.write(f'Output: {output_path}')
            self.stdout.write(f'Apps: {apps_to_include or "All installed apps"}')
            self.stdout.write(f'Include docs: {config.INCLUDE_DOCS}')
            self.stdout.write(f'Include validators: {config.INCLUDE_VALIDATORS}')
            self.stdout.write(f'Dry run: {options.get("dry_run", False)}')
        
        try:
            # Step 1: Inspect models
            inspector = ModelInspector()
            ir = inspector.inspect_models(apps_to_include)
            
            model_count = len(ir.models)
            app_count = len(set(m.app_label for m in ir.models))
            field_count = sum(len(model.fields) for model in ir.models)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Inspected {model_count} models with {field_count} fields '
                    f'from {app_count} apps'
                )
            )
            
            if options.get('verbose'):
                for model in ir.models:
                    self.stdout.write(f'  - {model.app_label}.{model.name} ({len(model.fields)} fields)')
            
            # Step 2: Render TypeScript
            renderer = TypeScriptRenderer(output_path)
            ts_code = renderer.render(ir)
            
            # Step 3: Write to file or show preview
            if options.get('dry_run'):
                self.stdout.write(
                    self.style.WARNING('\n=== DRY RUN - Generated code preview (first 500 chars) ===')
                )
                self.stdout.write(ts_code[:500] + '...' if len(ts_code) > 500 else ts_code)
                self.stdout.write('=== END DRY RUN ===')
            else:
                renderer.write_to_file(ts_code)
                elapsed_time = time.time() - start_time
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully generated TypeScript interfaces to {output_path} '
                        f'({elapsed_time:.2f}s)'
                    )
                )
            
            if options.get('verbose'):
                self.stdout.write(f'Generated code size: {len(ts_code)} characters')
                self.stdout.write(f'Lines of code: {ts_code.count(chr(10)) + 1}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during generation: {e}')
            )
            if options.get('verbose'):
                import traceback
                self.stdout.write(traceback.format_exc())
            raise