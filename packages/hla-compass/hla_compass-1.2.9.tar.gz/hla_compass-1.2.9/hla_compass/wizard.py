"""
Interactive wizard for HLA-Compass module creation

Guides users through module setup with intelligent questions and code generation.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .generators import CodeGenerator

console = Console()

# Custom style for the wizard
WIZARD_STYLE = Style([
    ('qmark', 'fg:#667eea bold'),       # Purple question mark
    ('question', 'bold'),                # Bold questions
    ('answer', 'fg:#10b981 bold'),      # Green answers
    ('pointer', 'fg:#667eea bold'),     # Purple pointer
    ('highlighted', 'fg:#667eea bold'), # Purple highlights
    ('selected', 'fg:#10b981'),         # Green selected
    ('separator', 'fg:#6b7280'),        # Gray separator
    ('instruction', 'fg:#6b7280'),      # Gray instructions
    ('text', ''),
    ('disabled', 'fg:#6b7280 italic'),
])


class ModuleWizard:
    """Interactive wizard for module creation"""
    
    def __init__(self):
        self.generator = CodeGenerator()
        self.config = {}
        
    def run(self) -> Dict[str, Any]:
        """Run the interactive wizard and return configuration"""
        
        # Welcome message
        self._show_welcome()
        
        # Step 1: Basic information
        self.config.update(self._ask_basic_info())
        
        # Step 2: Module type
        self.config.update(self._ask_module_type())
        
        # Step 3: Input parameters
        self.config['inputs'] = self._ask_inputs()
        
        # Step 4: Processing type
        self.config.update(self._ask_processing())
        
        # Step 5: Output format
        self.config['outputs'] = self._ask_outputs()
        
        # Step 6: Dependencies
        self.config['dependencies'] = self._ask_dependencies()
        
        # Step 7: Confirm and generate
        if self._confirm_configuration():
            return self.config
        else:
            # Allow editing
            return self._edit_configuration()
    
    def _show_welcome(self):
        """Display welcome message"""
        console.print(Panel.fit(
            "[bold bright_magenta]🧬 HLA-Compass Module Creation Wizard[/bold bright_magenta]\n\n"
            "I'll guide you through creating your module step by step.\n"
            "This wizard will:\n"
            "• Ask about your module's purpose\n"
            "• Define input and output schemas\n"
            "• Generate working code\n"
            "• Create test data\n\n"
            "[dim]Press Ctrl+C at any time to cancel[/dim]",
            title="Welcome",
            border_style="bright_magenta"
        ))
        console.print()
    
    def _ask_basic_info(self) -> Dict[str, Any]:
        """Ask for basic module information"""
        console.print("[bold cyan]📝 Basic Information[/bold cyan]\n")
        
        name = questionary.text(
            "Module name:",
            default="my-module",
            style=WIZARD_STYLE,
            validate=lambda x: len(x) > 0
        ).ask()
        
        description = questionary.text(
            "Brief description:",
            default="HLA-Compass analysis module",
            style=WIZARD_STYLE
        ).ask()
        
        author = questionary.text(
            "Your name:",
            default="Developer",
            style=WIZARD_STYLE
        ).ask()
        
        email = questionary.text(
            "Your email:",
            default=f"{author.lower().replace(' ', '.')}@example.com",
            style=WIZARD_STYLE
        ).ask()
        
        return {
            'name': name,
            'description': description,
            'author': {'name': author, 'email': email}
        }
    
    def _ask_module_type(self) -> Dict[str, Any]:
        """Ask about module type"""
        console.print("\n[bold cyan]🎨 Module Type[/bold cyan]\n")
        
        has_ui = questionary.confirm(
            "Does your module need a user interface?",
            default=False,
            style=WIZARD_STYLE
        ).ask()
        
        result = {'has_ui': has_ui}
        
        if has_ui:
            ui_type = questionary.select(
                "What kind of UI do you need?",
                choices=[
                    "Data table with filters",
                    "Interactive charts and graphs",
                    "Form-based input wizard",
                    "Custom dashboard",
                    "Simple results display"
                ],
                style=WIZARD_STYLE
            ).ask()
            result['ui_type'] = ui_type
        
        return result
    
    def _ask_inputs(self) -> Dict[str, Any]:
        """Ask about input parameters"""
        console.print("\n[bold cyan]📥 Input Parameters[/bold cyan]\n")
        console.print("[dim]Define what data your module will accept[/dim]\n")
        
        inputs = {}
        
        # Common peptide-related inputs
        use_peptides = questionary.confirm(
            "Will you work with peptide sequences?",
            default=True,
            style=WIZARD_STYLE
        ).ask()
        
        if use_peptides:
            peptide_input = questionary.select(
                "How will peptides be provided?",
                choices=[
                    "List of sequences",
                    "FASTA file",
                    "Database query",
                    "CSV/Excel file"
                ],
                style=WIZARD_STYLE
            ).ask()
            
            if peptide_input == "List of sequences":
                inputs['peptide_sequences'] = {
                    'type': 'array',
                    'description': 'List of peptide sequences',
                    'required': True,
                    'items': {'type': 'string'}
                }
            elif peptide_input == "FASTA file":
                inputs['fasta_file'] = {
                    'type': 'string',
                    'description': 'Path or content of FASTA file',
                    'required': True
                }
            elif peptide_input == "Database query":
                inputs['query'] = {
                    'type': 'object',
                    'description': 'Database query parameters',
                    'required': True
                }
            else:  # CSV/Excel
                inputs['data_file'] = {
                    'type': 'string',
                    'description': 'Path to CSV/Excel file',
                    'required': True
                }
        
        # Ask for additional custom inputs
        while questionary.confirm(
            "Add another input parameter?",
            default=False,
            style=WIZARD_STYLE
        ).ask():
            param_name = questionary.text(
                "Parameter name:",
                style=WIZARD_STYLE
            ).ask()
            
            param_type = questionary.select(
                "Parameter type:",
                choices=['string', 'number', 'boolean', 'array', 'object'],
                style=WIZARD_STYLE
            ).ask()
            
            param_desc = questionary.text(
                "Description:",
                style=WIZARD_STYLE
            ).ask()
            
            param_required = questionary.confirm(
                "Is this required?",
                default=True,
                style=WIZARD_STYLE
            ).ask()
            
            inputs[param_name] = {
                'type': param_type,
                'description': param_desc,
                'required': param_required
            }
            
            if not param_required:
                default_val = questionary.text(
                    f"Default value for {param_name}:",
                    style=WIZARD_STYLE
                ).ask()
                
                # Parse default value based on type
                if param_type == 'number':
                    inputs[param_name]['default'] = float(default_val) if default_val else 0
                elif param_type == 'boolean':
                    inputs[param_name]['default'] = default_val.lower() in ['true', 'yes', '1']
                elif param_type == 'array':
                    inputs[param_name]['default'] = []
                elif param_type == 'object':
                    inputs[param_name]['default'] = {}
                else:
                    inputs[param_name]['default'] = default_val
        
        return inputs
    
    def _ask_processing(self) -> Dict[str, Any]:
        """Ask about processing type"""
        console.print("\n[bold cyan]⚙️ Processing Type[/bold cyan]\n")
        
        processing_type = questionary.select(
            "What kind of processing will your module perform?",
            choices=[
                "Sequence analysis (alignment, motifs, properties)",
                "Statistical analysis (correlation, clustering)",
                "Machine learning (prediction, classification)",
                "Data transformation (filtering, formatting)",
                "Database operations (search, annotation)",
                "Visualization (plots, reports)",
                "Integration (external APIs, tools)",
                "Custom algorithm"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        # Ask for specific features based on type
        features = []
        
        if "Sequence analysis" in processing_type:
            features = questionary.checkbox(
                "Select sequence analysis features:",
                choices=[
                    "Physicochemical properties",
                    "Motif discovery",
                    "Sequence alignment",
                    "Structure prediction",
                    "Immunogenicity scoring"
                ],
                style=WIZARD_STYLE
            ).ask()
        elif "Machine learning" in processing_type:
            features = questionary.checkbox(
                "Select ML features:",
                choices=[
                    "Binary classification",
                    "Multi-class classification",
                    "Regression",
                    "Clustering",
                    "Feature importance"
                ],
                style=WIZARD_STYLE
            ).ask()
        
        return {
            'processing_type': processing_type,
            'features': features
        }
    
    def _ask_outputs(self) -> Dict[str, Any]:
        """Ask about output format"""
        console.print("\n[bold cyan]📤 Output Format[/bold cyan]\n")
        
        output_format = questionary.select(
            "Primary output format:",
            choices=[
                "Structured data (JSON/dict)",
                "Table (CSV/Excel compatible)",
                "Report (formatted text/HTML)",
                "Visualization (charts/plots)",
                "Files (generated files)"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        outputs = {}
        
        if "Structured data" in output_format:
            outputs['results'] = {
                'type': 'array',
                'description': 'Processing results'
            }
            outputs['summary'] = {
                'type': 'object',
                'description': 'Summary statistics'
            }
        elif "Table" in output_format:
            outputs['table'] = {
                'type': 'array',
                'description': 'Tabular results'
            }
            outputs['columns'] = {
                'type': 'array',
                'description': 'Column definitions'
            }
        elif "Report" in output_format:
            outputs['report'] = {
                'type': 'string',
                'description': 'Formatted report'
            }
        elif "Visualization" in output_format:
            outputs['plots'] = {
                'type': 'array',
                'description': 'Generated plots'
            }
        else:  # Files
            outputs['files'] = {
                'type': 'array',
                'description': 'Generated file paths'
            }
        
        # Always include status and metadata
        outputs['status'] = {
            'type': 'string',
            'description': 'Execution status'
        }
        outputs['metadata'] = {
            'type': 'object',
            'description': 'Execution metadata'
        }
        
        return outputs
    
    def _ask_dependencies(self) -> List[str]:
        """Ask about required dependencies"""
        console.print("\n[bold cyan]📦 Dependencies[/bold cyan]\n")
        
        # Common scientific Python packages
        deps = questionary.checkbox(
            "Select required packages:",
            choices=[
                "numpy - Numerical computing",
                "pandas - Data manipulation",
                "scikit-learn - Machine learning",
                "biopython - Bioinformatics tools",
                "matplotlib - Plotting",
                "seaborn - Statistical visualization",
                "scipy - Scientific computing",
                "torch - Deep learning",
                "requests - HTTP requests",
                "xlsxwriter - Excel export"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        # Clean up dependency names
        clean_deps = [dep.split(' - ')[0] for dep in deps]
        
        # Ask for additional custom dependencies
        custom = questionary.text(
            "Additional packages (comma-separated, optional):",
            default="",
            style=WIZARD_STYLE
        ).ask()
        
        if custom:
            clean_deps.extend([d.strip() for d in custom.split(',')])
        
        return clean_deps
    
    def _confirm_configuration(self) -> bool:
        """Show configuration summary and confirm"""
        console.print("\n[bold cyan]📋 Configuration Summary[/bold cyan]\n")
        
        # Create summary table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Setting", style="bright_white")
        table.add_column("Value", style="bright_green")
        
        table.add_row("Module Name", self.config['name'])
        table.add_row("Description", self.config['description'])
        table.add_row("Type", "UI Module" if self.config.get('has_ui') else "Backend Module")
        table.add_row("Author", f"{self.config['author']['name']} <{self.config['author']['email']}>")
        table.add_row("Inputs", f"{len(self.config.get('inputs', {}))} parameters")
        table.add_row("Outputs", f"{len(self.config.get('outputs', {}))} fields")
        table.add_row("Dependencies", f"{len(self.config.get('dependencies', []))} packages")
        
        console.print(table)
        console.print()
        
        return questionary.confirm(
            "Generate module with this configuration?",
            default=True,
            style=WIZARD_STYLE
        ).ask()
    
    def _edit_configuration(self) -> Dict[str, Any]:
        """Allow editing configuration"""
        while True:
            action = questionary.select(
                "What would you like to change?",
                choices=[
                    "Basic information",
                    "Module type",
                    "Input parameters",
                    "Processing type",
                    "Output format",
                    "Dependencies",
                    "✓ Continue with current configuration",
                    "✗ Cancel"
                ],
                style=WIZARD_STYLE
            ).ask()
            
            if action == "✓ Continue with current configuration":
                return self.config
            elif action == "✗ Cancel":
                return None
            elif action == "Basic information":
                self.config.update(self._ask_basic_info())
            elif action == "Module type":
                self.config.update(self._ask_module_type())
            elif action == "Input parameters":
                self.config['inputs'] = self._ask_inputs()
            elif action == "Processing type":
                self.config.update(self._ask_processing())
            elif action == "Output format":
                self.config['outputs'] = self._ask_outputs()
            elif action == "Dependencies":
                self.config['dependencies'] = self._ask_dependencies()
            
            # Show updated configuration
            self._confirm_configuration()


def run_wizard() -> Optional[Dict[str, Any]]:
    """Run the module creation wizard"""
    try:
        wizard = ModuleWizard()
        config = wizard.run()
        
        if config:
            console.print("\n[green]✓ Configuration complete![/green]")
            console.print("[dim]Generating module files...[/dim]\n")
            return config
        else:
            console.print("\n[yellow]Module creation cancelled[/yellow]")
            return None
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Wizard interrupted[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Wizard error: {e}[/red]")
        return None