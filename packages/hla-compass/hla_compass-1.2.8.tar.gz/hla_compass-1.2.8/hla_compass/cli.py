"""
HLA-Compass CLI for module development
"""

import os
import sys
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import click
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .testing import ModuleTester
from .auth import Auth
from .config import Config
from .signing import ModuleSigner

console = Console()


def load_sdk_config() -> dict | None:
    """Load SDK configuration from config file"""
    try:
        config_path = Config.get_config_path()
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception:
        pass
    return None


ALITHEA_BANNER = """
        [bold bright_magenta]█████╗[/bold bright_magenta] [bold bright_cyan]██╗[/bold bright_cyan]     [bold bright_green]██╗[/bold bright_green][bold bright_yellow]████████╗[/bold bright_yellow][bold bright_red]██╗  ██╗[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta] [bold bright_cyan]█████╗[/bold bright_cyan]
       [bold bright_magenta]██╔══██╗[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]╚══██╔══╝[/bold bright_yellow][bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]██╔════╝[/bold bright_magenta][bold bright_cyan]██╔══██╗[/bold bright_cyan]
       [bold bright_magenta]███████║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]███████║[/bold bright_red][bold bright_magenta]█████╗[/bold bright_magenta]  [bold bright_cyan]███████║[/bold bright_cyan]
       [bold bright_magenta]██╔══██║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██╔══██║[/bold bright_red][bold bright_magenta]██╔══╝[/bold bright_magenta]  [bold bright_cyan]██╔══██║[/bold bright_cyan]
       [bold bright_magenta]██║  ██║[/bold bright_magenta][bold bright_cyan]███████╗[/bold bright_cyan][bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta][bold bright_cyan]██║  ██║[/bold bright_cyan]
       [bold bright_magenta]╚═╝  ╚═╝[/bold bright_magenta][bold bright_cyan]╚══════╝[/bold bright_cyan][bold bright_green]╚═╝[/bold bright_green][bold bright_yellow]   ╚═╝[/bold bright_yellow]   [bold bright_red]╚═╝  ╚═╝[/bold bright_red][bold bright_magenta]╚══════╝[/bold bright_magenta][bold bright_cyan]╚═╝  ╚═╝[/bold bright_cyan]

                  [bold bright_white]🧬  B I O I N F O R M A T I C S  🧬[/bold bright_white]
"""


def show_banner():
    """Display the Alithea banner with helpful context"""
    console.print(ALITHEA_BANNER)
    env = Config.get_environment()
    api = Config.get_api_endpoint()

    # Color-coded environment indicator
    env_color = {"dev": "green", "staging": "yellow", "prod": "red"}.get(env, "cyan")

    info = (
        f"[bold bright_white]HLA-Compass Platform SDK[/bold bright_white]\n"
        f"[dim white]Version[/dim white] [bold bright_cyan]{__version__}[/bold bright_cyan]   "
        f"[dim white]Environment[/dim white] [bold {env_color}]{env.upper()}[/bold {env_color}]\n"
        f"[dim white]API Endpoint[/dim white] [bright_blue]{api}[/bright_blue]\n"
        f"[bright_magenta]✨[/bright_magenta] [italic]Immuno-Peptidomics • Module Development • AI-Powered Analysis[/italic] [bright_magenta]✨[/bright_magenta]"
    )
    console.print(
        Panel.fit(
            info,
            title="[bold bright_cyan]🔬 Alithea Bio[/bold bright_cyan]",
            subtitle="[bright_blue]https://alithea.bio[/bright_blue]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )


@click.group()
@click.version_option(version=__version__)
def cli():
    """HLA-Compass SDK - Module development tools"""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Overwrite existing configuration and keys")
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Default environment",
)
@click.option(
    "--api-endpoint", help="Custom API endpoint (overrides environment default)"
)
@click.option("--organization", help="Your organization name")
@click.option("--author-name", help="Your name for module authorship")
@click.option("--author-email", help="Your email for module authorship")
def configure(
    force: bool,
    env: str,
    api_endpoint: str | None,
    organization: str | None,
    author_name: str | None,
    author_email: str | None,
):
    """Set up initial SDK configuration and generate RSA keypair for signing"""
    console.print("[bold blue]HLA-Compass SDK Configuration[/bold blue]\n")

    # Get configuration directory
    config_path = Config.get_config_path()

    # Check if configuration already exists
    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_path}[/yellow]")
        if not Confirm.ask("Do you want to update the existing configuration?"):
            console.print("Configuration cancelled.")
            return
        force = True

    try:
        # Initialize module signer
        signer = ModuleSigner()

        # Check for existing keys
        keys_exist = (
            signer.private_key_path.exists() and signer.public_key_path.exists()
        )

        if keys_exist and not force:
            console.print(
                f"[yellow]RSA keypair already exists at {signer.keys_dir}[/yellow]"
            )
            regenerate_keys = Confirm.ask("Do you want to regenerate the RSA keypair?")
        else:
            regenerate_keys = True

        # Generate or regenerate keys if needed
        if regenerate_keys:
            console.print("🔐 Generating RSA keypair for module signing...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Generating 4096-bit RSA keypair...", total=None
                )

                try:
                    private_path, public_path = signer.generate_keys(force=force)
                    progress.update(task, description="Keys generated successfully!")
                    console.print(f"  ✓ Private key: {private_path}")
                    console.print(f"  ✓ Public key: {public_path}")
                    console.print(
                        f"  ✓ Key fingerprint: {signer.get_key_fingerprint()}"
                    )
                except Exception as e:
                    console.print(f"[red]Error generating keys: {e}[/red]")
                    sys.exit(1)
        else:
            console.print(f"✓ Using existing RSA keypair at {signer.keys_dir}")
            console.print(f"  Key fingerprint: {signer.get_key_fingerprint()}")

        # Collect configuration parameters
        console.print("\n[bold]Configuration Setup[/bold]")

        # Use provided values or prompt for input
        if not api_endpoint:
            api_endpoint = Config.API_ENDPOINTS.get(env)

        if not organization:
            organization = Prompt.ask(
                "Organization name",
                default=os.environ.get("HLA_AUTHOR_ORG", "Independent"),
            )

        if not author_name:
            author_name = Prompt.ask(
                "Your name (for module authorship)",
                default=os.environ.get(
                    "HLA_AUTHOR_NAME", os.environ.get("USER", "Developer")
                ),
            )

        if not author_email:
            author_email = Prompt.ask(
                "Your email (for module authorship)",
                default=os.environ.get(
                    "HLA_AUTHOR_EMAIL",
                    f"{author_name.lower().replace(' ', '.')}@example.com",
                ),
            )

        # Create configuration
        config_data = {
            "version": "1.0",
            "environment": env,
            "api_endpoint": api_endpoint,
            "organization": organization,
            "author": {"name": author_name, "email": author_email},
            "signing": {
                "algorithm": signer.ALGORITHM,
                "hash_algorithm": signer.HASH_ALGORITHM,
                "key_fingerprint": signer.get_key_fingerprint(),
                "private_key_path": str(signer.private_key_path),
                "public_key_path": str(signer.public_key_path),
            },
            "created_at": json.dumps(
                {"timestamp": "auto"}
            ),  # Will be replaced with actual timestamp
        }

        # Add timestamp
        import datetime

        config_data["created_at"] = datetime.datetime.now().isoformat()

        # Save configuration
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        console.print(f"\n[green]✓ Configuration saved to {config_path}[/green]\n")

        # Display configuration summary
        config_table = Table(title="SDK Configuration Summary")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")

        config_table.add_row("Environment", env)
        config_table.add_row("API Endpoint", api_endpoint)
        config_table.add_row("Organization", organization)
        config_table.add_row("Author", f"{author_name} <{author_email}>")
        config_table.add_row("Keys Directory", str(signer.keys_dir))
        config_table.add_row(
            "Signing Algorithm", f"{signer.ALGORITHM} with {signer.HASH_ALGORITHM}"
        )

        console.print(config_table)

        console.print("\n[bold]Next Steps:[/bold]")
        console.print("• Create a module: [cyan]hla-compass init my-module[/cyan]")
        console.print("• Build and sign: [cyan]hla-compass build[/cyan]")
        console.print("• Publish to platform: [cyan]hla-compass publish[/cyan]")

    except Exception as e:
        console.print(f"[red]Configuration failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("name", required=False)
@click.option(
    "--template",
    type=click.Choice(["ui", "no-ui"]),
    default="no-ui",
    help="Module template: 'ui' for modules with user interface, 'no-ui' for backend-only (default: no-ui)"
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Use interactive wizard to create module with custom configuration"
)
@click.option(
    "--compute",
    type=click.Choice(["lambda", "fargate", "sagemaker"]),
    default="lambda",
    help="Compute type",
)
@click.option("--no-banner", is_flag=True, help="Skip the Alithea banner display")
@click.option(
    "--yes", is_flag=True, help="Assume yes for all prompts (non-interactive mode)"
)
def init(
    name: str | None,
    template: str,
    interactive: bool,
    compute: str,
    no_banner: bool,
    yes: bool,
):
    """Create a new HLA-Compass module

    Examples:
        hla-compass init my-module                    # Backend-only module (no UI)
        hla-compass init my-module --template ui      # Module with user interface
        hla-compass init --interactive                # Interactive wizard (recommended)
        hla-compass init my-module -i                 # Interactive wizard with name
    """
    # Show the beautiful Alithea banner only during module creation
    if not no_banner:
        show_banner()
    
    # Use interactive wizard if requested
    if interactive:
        from .wizard import run_wizard
        from .generators import CodeGenerator
        
        console.print("[bold cyan]🎯 Starting Interactive Module Wizard[/bold cyan]\n")
        
        # Run the wizard
        config = run_wizard()
        if not config:
            console.print("[yellow]Module creation cancelled[/yellow]")
            return
        
        # Use provided name if given, otherwise use wizard name
        if name:
            config['name'] = name
        module_name = config['name']
        
        # Create module directory
        module_dir = Path(module_name)
        if module_dir.exists() and not yes:
            if not Confirm.ask(f"Directory '{module_name}' already exists. Continue?"):
                return
        
        # Generate module from wizard configuration
        generator = CodeGenerator()
        success = generator.generate_module(config, module_dir)
        
        if success:
            console.print(Panel.fit(
                f"[green]✓ Module '{module_name}' created successfully![/green]\n\n"
                f"[bold]Generated from wizard configuration:[/bold]\n"
                f"• Type: {'UI Module' if config.get('has_ui') else 'Backend Module'}\n"
                f"• Inputs: {len(config.get('inputs', {}))} parameters\n"
                f"• Outputs: {len(config.get('outputs', {}))} fields\n"
                f"• Dependencies: {len(config.get('dependencies', []))} packages\n\n"
                f"[bold]Next steps:[/bold]\n"
                f"1. cd {module_name}\n"
                f"2. pip install -r backend/requirements.txt\n"
                f"3. hla-compass dev  # Start hot-reload server\n\n"
                f"[dim]The wizard has generated working code based on your specifications.\n"
                f"Edit backend/main.py to customize the processing logic.[/dim]",
                title="Module Created with Wizard",
                border_style="green",
                width=100
            ))
        else:
            console.print("[red]Failed to generate module from wizard configuration[/red]")
        return
    
    # Standard template-based creation (non-interactive)
    if not name:
        console.print("[red]Module name is required when not using --interactive[/red]")
        console.print("Usage: hla-compass init MODULE_NAME")
        console.print("   Or: hla-compass init --interactive")
        return

    # Determine module type from template
    module_type = "with-ui" if template == "ui" else "no-ui"
    
    # Map template names to actual template directories
    template_dir_name = f"{template}-template"

    console.print(
        f"[bold green]🧬 Creating HLA-Compass Module: [white]{name}[/white] 🧬[/bold green]"
    )
    console.print(
        f"[dim]Template: {template} • Type: {module_type} • Compute: {compute}[/dim]\n"
    )

    # Check if directory already exists
    module_dir = Path(name)
    if module_dir.exists():
        if not yes and not Confirm.ask(f"Directory '{name}' already exists. Continue?"):
            return

    # Find template directory
    pkg_templates_dir = Path(__file__).parent / "templates" / template_dir_name
    
    if not pkg_templates_dir.exists():
        console.print(f"[red]Template '{template}' not found[/red]")
        console.print("[yellow]Available templates:[/yellow]")
        console.print("  • no-ui - Backend-only module without user interface")
        console.print("  • ui    - Module with React/TypeScript user interface")
        return
    
    template_dir = pkg_templates_dir

    # Copy template
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Copying template files...", total=None)

        shutil.copytree(template_dir, module_dir, dirs_exist_ok=True)

        progress.update(task, description="Updating manifest...")

        # Update manifest.json
        manifest_path = module_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        manifest["name"] = name
        manifest["type"] = module_type
        manifest["computeType"] = compute

        # Load author information from SDK config, then environment, then defaults
        sdk_config = load_sdk_config()
        author_info = sdk_config.get("author", {}) if sdk_config else {}

        manifest["author"]["name"] = (
            author_info.get("name") or
            os.environ.get("HLA_AUTHOR_NAME") or
            os.environ.get("USER", "Unknown")
        )
        manifest["author"]["email"] = author_info.get("email") or os.environ.get(
            "HLA_AUTHOR_EMAIL", "developer@example.com"
        )
        manifest["author"]["organization"] = (
            sdk_config.get("organization") if sdk_config else None
        ) or os.environ.get("HLA_AUTHOR_ORG", "Independent")
        manifest["description"] = os.environ.get(
            "HLA_MODULE_DESC", f"HLA-Compass module: {name}"
        )

        # Show what was set
        console.print(f"  Author: {manifest['author']['name']}")
        console.print(f"  Email: {manifest['author']['email']}")
        console.print(f"  Organization: {manifest['author']['organization']}")

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Remove frontend directory if no-ui
        if module_type == "no-ui":
            frontend_dir = module_dir / "frontend"
            if frontend_dir.exists():
                shutil.rmtree(frontend_dir)

        # Create virtual environment only if not already in one
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            progress.update(
                task, description="Skipping venv (already in virtual environment)..."
            )
        else:
            progress.update(task, description="Creating virtual environment...")
            subprocess.run(
                [sys.executable, "-m", "venv", str(module_dir / "venv")],
                capture_output=True,
            )

        progress.update(task, description="Module created!", completed=True)

    # Display comprehensive success message with full workflow
    ui_specific = ""
    if module_type == "with-ui":
        ui_specific = (
            f"• Edit frontend/index.tsx for UI components\n"
            f"• Install frontend deps: cd frontend && npm install\n"
        )
    
    console.print(
        Panel.fit(
            f"[green]✓ Module '{name}' created successfully![/green]\n\n"
            f"[bold]Template Type:[/bold] {template.upper()} ({'With UI' if module_type == 'with-ui' else 'Backend-only'})\n\n"
            f"[bold]Quick Start:[/bold]\n"
            f"1. cd {name}\n"
            f"2. pip install -r backend/requirements.txt  # Install Python dependencies\n"
            f"3. hla-compass test                         # Test locally\n\n"
            f"[bold]Development:[/bold]\n"
            f"• Edit backend/main.py to implement your logic\n"
            f"{ui_specific}"
            f"• Add test data to examples/sample_input.json\n"
            f"• Test: hla-compass test --input examples/sample_input.json\n\n"
            f"[bold]Deployment:[/bold]\n"
            f"• Configure: hla-compass configure\n"
            f"• Build: hla-compass build\n"
            f"• Publish: hla-compass publish --env dev\n\n"
            f"[bold]Documentation:[/bold]\n"
            f"• Templates guide: sdk/python/hla_compass/templates/README.md\n"
            f"• SDK docs: https://docs.hla-compass.com",
            title=f"Module Created - {'UI' if module_type == 'with-ui' else 'No-UI'} Template",
            width=100,
        )
    )


@cli.command()
@click.option("--manifest", default="manifest.json", help="Path to manifest.json")
@click.option(
    "--json", "output_json", is_flag=True, help="Output as JSON for automation"
)
def validate(manifest: str, output_json: bool):
    """Validate module structure and manifest"""
    if not output_json:
        console.print("[bold]Validating module...[/bold]")

    errors = []
    warnings = []

    # Check manifest exists
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        if output_json:
            result = {
                "valid": False,
                "errors": ["manifest.json not found"],
                "warnings": [],
            }
            print(json.dumps(result))
        else:
            console.print("[red]✗ manifest.json not found[/red]")
        sys.exit(1)

    # Load and validate manifest
    try:
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        if output_json:
            result = {
                "valid": False,
                "errors": [f"Invalid JSON in manifest.json: {e}"],
                "warnings": [],
            }
            print(json.dumps(result))
        else:
            console.print(f"[red]✗ Invalid JSON in manifest.json: {e}[/red]")
        sys.exit(1)

    # Required fields
    required_fields = [
        "name",
        "version",
        "type",
        "computeType",
        "author",
        "inputs",
        "outputs",
    ]
    for field in required_fields:
        if field not in manifest_data:
            errors.append(f"Missing required field: {field}")

    # Check backend structure
    module_dir = manifest_path.parent
    backend_dir = module_dir / "backend"

    if not backend_dir.exists():
        errors.append("backend/ directory not found")
    else:
        if not (backend_dir / "main.py").exists():
            errors.append("backend/main.py not found")
        if not (backend_dir / "requirements.txt").exists():
            warnings.append("backend/requirements.txt not found")

    # Check frontend for with-ui modules
    if manifest_data.get("type") == "with-ui":
        frontend_dir = module_dir / "frontend"
        if not frontend_dir.exists():
            errors.append("frontend/ directory required for with-ui modules")
        elif not (frontend_dir / "index.tsx").exists():
            errors.append("frontend/index.tsx not found")

    # Display results
    if output_json:
        result = {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)
    else:
        if errors:
            console.print("[red]✗ Validation failed with errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print(
                "\n[yellow]Fix the errors above, then run 'hla-compass validate' again[/yellow]"
            )
            sys.exit(1)
        else:
            console.print("[green]✓ Module structure valid[/green]")
            if warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")
            console.print("\n[bold]Ready for next steps:[/bold]")
            console.print("  • Test: hla-compass test")
            console.print("  • Sign: hla-compass sign dist/*.zip (coming soon)")
            console.print(
                "  • Deploy: hla-compass deploy dist/*.zip --env dev (coming soon)"
            )
            sys.exit(0)


@cli.command()
@click.option("--port", default=8080, help="Port for dev server (default: 8080)")
@click.option("--no-frontend", is_flag=True, help="Skip frontend dev server for UI modules")
@click.option("--verbose", is_flag=True, help="Show detailed logs")
def dev(port: int, no_frontend: bool, verbose: bool):
    """Start hot-reload development server for module testing
    
    Features:
    - Automatic reload on file changes
    - Interactive web UI for testing
    - Real-time error display
    - Mock API for local development
    
    Example:
        hla-compass dev               # Start on default port 8080
        hla-compass dev --port 3000   # Use custom port
    """
    from .dev_server import run_dev_server
    
    console.print("[bold blue]Starting Development Server[/bold blue]\n")
    
    # Check if we're in a module directory
    if not Path("manifest.json").exists():
        console.print("[red]Error: manifest.json not found[/red]")
        console.print("Run this command from your module directory")
        sys.exit(1)
    
    # Check backend directory
    if not Path("backend/main.py").exists():
        console.print("[red]Error: backend/main.py not found[/red]")
        console.print("Module structure appears incomplete")
        sys.exit(1)
    
    try:
        # Configure logging if verbose
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        # Start the dev server
        run_dev_server(".", port)
        
    except Exception as e:
        console.print(f"[red]Failed to start dev server: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option("--input", "input_file", help="Input JSON file")
@click.option("--local", is_flag=True, default=False, help="Test locally without API")
@click.option("--remote", is_flag=True, default=False, help="Test against real API")
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.option(
    "--json", "output_json", is_flag=True, help="Output as JSON for automation"
)
def test(
    input_file: str | None, local: bool, remote: bool, verbose: bool, output_json: bool
):
    """Test module locally or against real API"""

    # Determine test mode
    if remote and local:
        console.print("[red]Cannot use both --local and --remote flags[/red]")
        return

    # Default to remote if authenticated, otherwise local
    auth = Auth()
    if not remote and not local:
        remote = auth.is_authenticated()
        local = not remote

    if remote:
        if not output_json:
            console.print(
                "[bold]Testing module with API authentication context...[/bold]"
            )
        if not auth.is_authenticated():
            if output_json:
                result = {
                    "ok": False,
                    "status": "error",
                    "error": {"type": "auth_error", "message": "Not authenticated"},
                }
                print(json.dumps(result))
            else:
                console.print(
                    "[yellow]⚠️  Not authenticated. Please login first.[/yellow]"
                )
                console.print("Run: hla-compass auth login")
            sys.exit(1)  # noqa: F823
        if not output_json:
            console.print(
                "[blue]ℹ️  Note: Module executes locally with API access. Remote execution coming soon.[/blue]"
            )
    else:
        if not output_json:
            console.print("[bold]Testing module locally (no API access)...[/bold]")

    # Load test input
    if input_file:
        with open(input_file, "r") as f:
            test_input = json.load(f)
    else:
        # Try to load example input
        example_path = Path("examples/sample_input.json")
        if example_path.exists():
            with open(example_path, "r") as f:
                test_input = json.load(f)
        else:
            test_input = {}
            if not output_json:
                console.print(
                    "[yellow]No input file provided, using empty input[/yellow]"
                )

    try:
        if remote:
            # Test using real API

            # Load manifest to get module name
            manifest_path = Path("manifest.json")
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    module_name = manifest.get("name", "test-module")
            else:
                module_name = "test-module"

            console.print(f"\n[blue]Executing module '{module_name}' via API...[/blue]")

            # For now, test by directly importing and running the module with API client
            # In future, this would execute via API Gateway
            import sys

            sys.path.insert(0, "backend")
            from main import lambda_handler

            # Create event for Lambda handler
            event = {
                "parameters": test_input,
                "job_id": "test-" + str(Path.cwd().name),
                "user_id": "test-user",
                "organization_id": "test-org",
            }

            # Mock context
            class Context:
                request_id = "test-request"

            result = lambda_handler(event, Context())

        else:
            # Test locally
            tester = ModuleTester()
            if not output_json:
                console.print("\n[blue]Running local test...[/blue]")

            # Create mock context
            context = {
                "job_id": "local-test",
                "user_id": "local-user",
                "organization_id": "local-org",
            }

            result = tester.test_local("backend/main.py", test_input, context)

        # Get module info for metadata
        module_name = "unknown"
        module_version = "1.0.0"
        manifest_path = Path("manifest.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                module_name = manifest.get("name", "unknown")
                module_version = manifest.get("version", "1.0.0")

        # Display results
        if output_json:
            # JSON output for automation
            from datetime import datetime

            if result.get("status") == "success":
                json_result = {
                    "ok": True,
                    "status": "success",
                    "summary": result.get("summary", {}),
                    "metadata": {
                        "module": module_name,
                        "version": module_version,
                        "execution_time": datetime.now().isoformat(),
                    },
                }
            else:
                error_info = result.get("error", {})
                json_result = {
                    "ok": False,
                    "status": "error",
                    "error": {
                        "type": error_info.get("type", "execution_error"),
                        "message": error_info.get("message", "Module execution failed"),
                    },
                    "metadata": {"module": module_name, "version": module_version},
                }

            print(json.dumps(json_result, indent=2))
            sys.exit(0 if json_result["ok"] else 1)
        else:
            # Human-readable output
            if result.get("status") == "success":
                console.print("[green]✓ Test passed[/green]")
                if verbose:
                    console.print("\nTest Result:")
                    console.print(
                        Syntax(json.dumps(result, indent=2), "json", theme="monokai")
                    )
                else:
                    # Show summary if available
                    if "summary" in result:
                        console.print("\n[bold]Summary:[/bold]")
                        for key, value in result["summary"].items():
                            console.print(f"  {key}: {value}")
                sys.exit(0)
            else:
                console.print("[red]✗ Test failed[/red]")
                if "error" in result:
                    console.print(
                        f"Error: {result['error'].get('message', 'Unknown error')}"
                    )
                sys.exit(1)

    except Exception as e:
        if output_json:
            json_result = {
                "ok": False,
                "status": "error",
                "error": {"type": "exception", "message": str(e)},
                "metadata": {
                    "module": module_name if "module_name" in locals() else "unknown",
                    "version": (
                        module_version if "module_version" in locals() else "1.0.0"
                    ),
                },
            }
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]Test failed with error: {e}[/red]")
            if verbose:
                import traceback

                console.print(traceback.format_exc())
        sys.exit(1)


@cli.group()
def auth():
    """Authentication commands"""
    pass


@auth.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Environment to login to",
)
def login(env: str):
    """Login to HLA-Compass platform"""
    console.print(f"[bold]Logging in to {env} environment...[/bold]")

    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)

    auth = Auth()

    try:
        success = auth.login(email, password, env)
        if success:
            console.print("[green]✓ Login successful![/green]")
            console.print(f"Environment: {env}")
            console.print("You can now test modules with: hla-compass test")
        else:
            console.print("[red]✗ Login failed[/red]")
            console.print("Please check your credentials and try again")
    except Exception as e:
        console.print(f"[red]Login error: {e}[/red]")


@auth.command()
def logout():
    """Logout from HLA-Compass platform"""
    console.print("[bold]Logging out...[/bold]")

    auth = Auth()
    auth.logout()

    console.print("[green]✓ Logged out successfully[/green]")


@auth.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Environment to register for",
)
def register(env: str):
    """Register as a developer (temporary credentials will be provided)"""
    console.print(f"[bold]Developer Registration for {env} environment[/bold]")
    console.print(
        "[blue]ℹ️  Note: This creates a developer account with temporary credentials.[/blue]"
    )

    email = Prompt.ask("Email")
    name = Prompt.ask("Full Name")
    organization = Prompt.ask("Organization", default="Independent")

    auth = Auth()

    try:
        # Note: auth.register ignores password and uses developer_register internally
        success = auth.register(email, None, name, organization, env)
        if success:
            console.print("[green]✓ Registration successful![/green]")
            console.print("Temporary credentials have been sent to your email.")
            console.print("You can login with: hla-compass auth login")
            sys.exit(0)
        else:
            console.print("[red]✗ Registration failed[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Registration error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--output", "-o", help="Output file path (default: dist/{name}-{version}.zip)"
)
@click.option("--no-sign", is_flag=True, help="Skip module signing")
def build(output: str | None = None, no_sign: bool = False):
    """Build and optionally sign module package for deployment"""

    console.print("[bold blue]Building Module Package[/bold blue]\n")

    # Check manifest exists
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]Error: manifest.json not found[/red]")
        console.print("Run this command from your module directory")
        sys.exit(1)

    # Load manifest for module info
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        module_name = manifest.get("name", "unknown")
        module_version = manifest.get("version", "1.0.0")
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid manifest.json - {e}[/red]")
        sys.exit(1)

    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = dist_dir / f"{module_name}-{module_version}.zip"

    # Sign the manifest before packaging (unless --no-sign)
    if not no_sign:
        try:
            console.print("🔐 Signing module manifest...")

            # Initialize signer
            signer = ModuleSigner()

            # Check if keys exist
            if not (
                signer.private_key_path.exists() and signer.public_key_path.exists()
            ):
                console.print("[red]Error: RSA keys not found[/red]")
                console.print("Run 'hla-compass configure' to generate signing keys")
                sys.exit(1)

            # Sign manifest in place
            signature = signer.sign_manifest(manifest)

            # Update manifest with signature information
            manifest["signature"] = signature
            manifest["publicKey"] = signer.get_public_key_string()
            manifest["signatureAlgorithm"] = signer.ALGORITHM
            manifest["hashAlgorithm"] = signer.HASH_ALGORITHM
            manifest["keyFingerprint"] = signer.get_key_fingerprint()

            # Save updated manifest
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            console.print(
                f"  ✓ Manifest signed with fingerprint: {manifest['keyFingerprint'][:16]}..."
            )

        except Exception as e:
            console.print(f"[red]Error signing manifest: {e}[/red]")
            console.print(
                "Use --no-sign to build without signing, or run 'hla-compass configure'"
            )
            sys.exit(1)
    else:
        console.print("⚠️  Skipping module signing (--no-sign flag)")

    # Files and directories to include
    include_items = [
        "manifest.json",
        "backend/",
        "frontend/",
        "docs/",
        "examples/",
        "README.md",
    ]

    # Create zip package
    console.print(f"📦 Creating package: {output_path}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:

        # Count total files first
        total_files = 0
        for item in include_items:
            item_path = Path(item)
            if item_path.exists():
                if item_path.is_file():
                    total_files += 1
                elif item_path.is_dir():
                    for file_path in item_path.rglob("*"):
                        if file_path.is_file() and not any(
                            skip in str(file_path)
                            for skip in [
                                "__pycache__",
                                ".pyc",
                                ".pyo",
                                "node_modules",
                                ".git",
                                ".DS_Store",
                            ]
                        ):
                            total_files += 1

        task = progress.add_task("Packaging files...", total=total_files)
        files_processed = 0

        with zipfile.ZipFile(
            output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
        ) as zipf:
            for item in include_items:
                item_path = Path(item)
                if item_path.exists():
                    if item_path.is_file():
                        zipf.write(item_path, item_path)
                        files_processed += 1
                        progress.update(task, advance=1, description=f"Added {item}")
                    elif item_path.is_dir():
                        for file_path in item_path.rglob("*"):
                            if file_path.is_file():
                                # Skip common unnecessary files
                                if any(
                                    skip in str(file_path)
                                    for skip in [
                                        "__pycache__",
                                        ".pyc",
                                        ".pyo",
                                        "node_modules",
                                        ".git",
                                        ".DS_Store",
                                    ]
                                ):
                                    continue
                                try:
                                    arcname = file_path.relative_to(Path.cwd())
                                except ValueError:
                                    # If file is not relative to cwd, use the full path structure
                                    arcname = str(file_path)
                                zipf.write(file_path, arcname)
                                files_processed += 1
                                progress.update(
                                    task, advance=1, description=f"Adding {arcname}"
                                )

    # Get package size and file count
    package_size = output_path.stat().st_size / 1024  # KB

    console.print("\n[green]✓ Module package built successfully![/green]")

    # Create summary table
    summary_table = Table(title="Build Summary")
    summary_table.add_column("Property", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Module Name", module_name)
    summary_table.add_row("Version", module_version)
    summary_table.add_row("Package", str(output_path))
    summary_table.add_row("Size", f"{package_size:.1f} KB")
    summary_table.add_row("Files", str(files_processed))
    summary_table.add_row("Signed", "✓ Yes" if not no_sign else "✗ No")

    if not no_sign and "keyFingerprint" in manifest:
        summary_table.add_row(
            "Key Fingerprint", manifest["keyFingerprint"][:32] + "..."
        )

    console.print(summary_table)

    console.print("\n[bold]Next Steps:[/bold]")
    console.print(
        f"• Publish to platform: [cyan]hla-compass publish {output_path}[/cyan]"
    )
    console.print(f"• Deploy manually: [cyan]hla-compass deploy {output_path}[/cyan]")


@cli.command()
@click.argument("package_file")
def sign(package_file: str):
    """Sign a module package"""
    console.print("[bold blue]Module Signing[/bold blue]\n")

    package_path = Path(package_file)
    if not package_path.exists():
        console.print(f"[red]Error: Package file not found: {package_file}[/red]")
        sys.exit(1)

    try:
        # Check if it's a zip file (built package) or directory (module source)
        if package_path.is_file() and package_path.suffix == ".zip":
            console.print("[red]Error: Cannot sign built package directly[/red]")
            console.print("Signing must be done during the build process.")
            console.print(
                "Use 'hla-compass build' to build and sign, or use --no-sign to skip signing"
            )
            sys.exit(1)
        elif package_path.is_dir():
            # Sign module directory manifest
            from .signing import sign_module_package

            console.print(f"📦 Signing module at: {package_path}")

            signer = ModuleSigner()

            # Check if keys exist
            if not (
                signer.private_key_path.exists() and signer.public_key_path.exists()
            ):
                console.print("[red]Error: RSA keys not found[/red]")
                console.print("Run 'hla-compass configure' to generate signing keys")
                sys.exit(1)

            # Sign the module package
            updated_manifest = sign_module_package(package_path, signer)

            console.print("[green]✓ Module manifest signed successfully![/green]")
            console.print(
                f"  Algorithm: {updated_manifest.get('signatureAlgorithm', 'RSA-PSS')}"
            )
            console.print(f"  Hash: {updated_manifest.get('hashAlgorithm', 'SHA-256')}")
            console.print(
                f"  Key Fingerprint: {updated_manifest.get('keyFingerprint', 'N/A')[:32]}..."
            )

            console.print("\n[cyan]Next Steps:[/cyan]")
            console.print("• Build signed package: [cyan]hla-compass build[/cyan]")
            console.print("• Publish to platform: [cyan]hla-compass publish[/cyan]")

        else:
            console.print(f"[red]Error: Invalid package file: {package_file}[/red]")
            console.print(
                "Provide either a module directory or use 'hla-compass build' to build and sign"
            )
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Signing failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--package", "-p", help="Path to built package (if not provided, will build first)"
)
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Target environment",
)
@click.option(
    "--no-build", is_flag=True, help="Skip building if package already exists"
)
@click.option("--no-sign", is_flag=True, help="Skip signing during build")
@click.option("--force", is_flag=True, help="Force republish even if module exists")
def publish(package: str | None, env: str, no_build: bool, no_sign: bool, force: bool):
    """Build, sign, and publish module to HLA-Compass platform"""

    console.print(f"[bold blue]Publishing Module to {env.upper()}[/bold blue]\n")

    # Check if we're in a module directory
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]Error: manifest.json not found[/red]")
        console.print("Run this command from your module directory")
        sys.exit(1)

    # Load manifest for module info
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        module_name = manifest.get("name", "unknown")
        module_version = manifest.get("version", "1.0.0")
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid manifest.json - {e}[/red]")
        sys.exit(1)

    try:
        # Step 1: Determine or build the package
        if package:
            package_path = Path(package)
            if not package_path.exists():
                console.print(
                    f"[red]Error: Specified package not found: {package}[/red]"
                )
                sys.exit(1)
        else:
            # Determine expected package path
            dist_dir = Path("dist")
            package_path = dist_dir / f"{module_name}-{module_version}.zip"

            # Check if package exists and if we should build
            if package_path.exists() and no_build:
                console.print(f"📦 Using existing package: {package_path}")
            else:
                console.print("📦 Building module package...")

                # Build the package using our build command logic
                # We need to import the build functionality or call it directly
                dist_dir.mkdir(exist_ok=True)

                # Sign the manifest before packaging (unless --no-sign)
                if not no_sign:
                    try:
                        console.print("🔐 Signing module manifest...")

                        # Initialize signer
                        signer = ModuleSigner()

                        # Check if keys exist
                        if not (
                            signer.private_key_path.exists() and
                            signer.public_key_path.exists()
                        ):
                            console.print("[red]Error: RSA keys not found[/red]")
                            console.print(
                                "Run 'hla-compass configure' to generate signing keys"
                            )
                            sys.exit(1)

                        # Sign manifest in place
                        signature = signer.sign_manifest(manifest)

                        # Update manifest with signature information
                        manifest["signature"] = signature
                        manifest["publicKey"] = signer.get_public_key_string()
                        manifest["signatureAlgorithm"] = signer.ALGORITHM
                        manifest["hashAlgorithm"] = signer.HASH_ALGORITHM
                        manifest["keyFingerprint"] = signer.get_key_fingerprint()

                        # Save updated manifest
                        with open(manifest_path, "w") as f:
                            json.dump(manifest, f, indent=2)

                        console.print("  ✓ Manifest signed")

                    except Exception as e:
                        console.print(f"[red]Error signing manifest: {e}[/red]")
                        if not force:
                            console.print(
                                "Use --no-sign to skip signing, or run 'hla-compass configure'"
                            )
                            sys.exit(1)

                # Package the module
                include_items = [
                    "manifest.json",
                    "backend/",
                    "frontend/",
                    "docs/",
                    "examples/",
                    "README.md",
                ]

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Creating package...", total=None)

                    with zipfile.ZipFile(
                        package_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
                    ) as zipf:
                        for item in include_items:
                            item_path = Path(item)
                            if item_path.exists():
                                if item_path.is_file():
                                    zipf.write(item_path, item_path)
                                elif item_path.is_dir():
                                    for file_path in item_path.rglob("*"):
                                        if file_path.is_file():
                                            # Skip unnecessary files
                                            if any(
                                                skip in str(file_path)
                                                for skip in [
                                                    "__pycache__",
                                                    ".pyc",
                                                    ".pyo",
                                                    "node_modules",
                                                    ".git",
                                                    ".DS_Store",
                                                ]
                                            ):
                                                continue
                                            try:
                                                arcname = file_path.relative_to(
                                                    Path.cwd()
                                                )
                                            except ValueError:
                                                # If file is not relative to cwd, use the full path structure
                                                arcname = str(file_path)
                                            zipf.write(file_path, arcname)

                    progress.update(task, description="Package created!")

                console.print(f"  ✓ Package built: {package_path}")

        # Step 2: Check authentication
        auth = Auth()
        if not auth.is_authenticated():
            console.print("[red]Error: Not authenticated[/red]")
            console.print("Run 'hla-compass auth login' first")
            sys.exit(1)

        console.print("🔑 Authentication verified")

        # Step 3: Initialize API client and upload
        from .client import APIClient

        client = APIClient()

        package_size = package_path.stat().st_size / 1024  # KB
        console.print(f"📤 Uploading package ({package_size:.1f} KB)...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            upload_task = progress.add_task("Uploading to platform...", total=100)

            try:
                # Simulate upload progress (replace with actual upload logic)
                upload_response = client.upload_module(
                    str(package_path), module_name, module_version
                )
                progress.update(upload_task, completed=100)

            except Exception as e:
                progress.update(
                    upload_task, description=f"Upload failed: {str(e)[:50]}..."
                )
                raise e

        module_id = upload_response.get("module_id")
        if not module_id:
            console.print(
                "[red]Error: Upload succeeded but no module_id returned[/red]"
            )
            sys.exit(1)

        console.print(f"  ✓ Package uploaded (ID: {module_id})")

        # Step 4: Register module
        console.print("📝 Registering module...")

        # Prepare metadata
        metadata = {
            "name": module_name,
            "version": module_version,
            "environment": env,
            "description": manifest.get("description", ""),
            "author": manifest.get("author", ""),
            "compute_type": manifest.get("computeType", "lambda"),
            "inputs": manifest.get("inputs", {}),
            "outputs": manifest.get("outputs", {}),
        }

        # Add signing information if available
        if "signature" in manifest:
            metadata["signature_info"] = {
                "algorithm": manifest.get("signatureAlgorithm"),
                "hash_algorithm": manifest.get("hashAlgorithm"),
                "key_fingerprint": manifest.get("keyFingerprint"),
                "signed": True,
            }

        client.register_module(module_id, metadata)
        console.print("  ✓ Module registered")

        # Step 5: Success summary
        console.print("\n[green]🎉 Module published successfully![/green]\n")

        # Create results table
        results_table = Table(title="Publication Summary")
        results_table.add_column("Property", style="cyan")
        results_table.add_column("Value", style="white")

        results_table.add_row("Module Name", module_name)
        results_table.add_row("Version", module_version)
        results_table.add_row("Module ID", module_id)
        results_table.add_row("Environment", env.upper())
        results_table.add_row("Package Size", f"{package_size:.1f} KB")
        results_table.add_row("Signed", "✓ Yes" if "signature" in manifest else "✗ No")

        if "keyFingerprint" in manifest:
            results_table.add_row(
                "Key Fingerprint", manifest["keyFingerprint"][:32] + "..."
            )

        console.print(results_table)

        console.print("\n[bold]Next Steps:[/bold]")
        console.print(
            f"• Test execution: [cyan]hla-compass execute {module_id} --input examples/input.json[/cyan]"
        )
        console.print(f"• List modules: [cyan]hla-compass list --env {env}[/cyan]")
        console.print(
            f"• View in platform: [cyan]https://hla-compass.com/modules/{module_id}[/cyan]"
        )

    except Exception as e:
        console.print(f"[red]Publication failed: {e}[/red]")

        # Provide helpful error context
        if "authentication" in str(e).lower():
            console.print("Try: [cyan]hla-compass auth login[/cyan]")
        elif "signing" in str(e).lower():
            console.print("Try: [cyan]hla-compass configure[/cyan]")
        elif "manifest" in str(e).lower():
            console.print("Check your manifest.json file for errors")

        sys.exit(1)


@cli.command()
@click.argument("package_file")
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Target environment",
)
def deploy(package_file: str, env: str):
    """Deploy module to HLA-Compass platform"""
    from pathlib import Path
    from .auth import Auth
    from .client import APIClient

    console.print(f"[bold blue]Deploying Module to {env}[/bold blue]\n")

    # Check package exists
    package_path = Path(package_file)
    if not package_path.exists():
        console.print(f"[red]Error: Package file not found: {package_file}[/red]")
        sys.exit(1)

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Extract module info from package name or manifest
    try:
        import zipfile

        with zipfile.ZipFile(package_path, "r") as zipf:
            # Try to read manifest from zip
            if "manifest.json" in zipf.namelist():
                with zipf.open("manifest.json") as f:
                    manifest = json.loads(f.read())
                    module_name = manifest.get("name", "unknown")
                    module_version = manifest.get("version", "1.0.0")
            else:
                # Fall back to filename parsing
                filename = package_path.stem  # Remove .zip
                parts = filename.rsplit("-", 1)
                if len(parts) == 2:
                    module_name, module_version = parts
                else:
                    module_name = filename
                    module_version = "1.0.0"
    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not read manifest from package: {e}[/yellow]"
        )
        # Use filename as fallback
        filename = package_path.stem
        parts = filename.rsplit("-", 1)
        if len(parts) == 2:
            module_name, module_version = parts
        else:
            module_name = filename
            module_version = "1.0.0"

    console.print(f"📦 Module: {module_name}")
    console.print(f"📌 Version: {module_version}")
    console.print(
        f"📁 Package: {package_path.name} ({package_path.stat().st_size / 1024:.1f} KB)\n"
    )

    # Initialize API client
    client = APIClient()

    try:
        # Step 1: Upload module
        console.print("⬆️  Uploading module package...")
        upload_response = client.upload_module(
            str(package_path), module_name, module_version
        )

        module_id = upload_response.get("module_id")
        if not module_id:
            console.print(
                "[red]Error: Upload succeeded but no module_id returned[/red]"
            )
            sys.exit(1)

        console.print(f"  ✓ Upload complete (module_id: {module_id})")

        # Step 2: Register module
        console.print("📝 Registering module...")

        # Prepare metadata
        metadata = {"name": module_name, "version": module_version, "environment": env}

        # Add manifest data if available
        if "manifest" in locals():
            metadata.update(
                {
                    "description": manifest.get("description", ""),
                    "author": manifest.get("author", ""),
                    "compute_type": manifest.get("compute", {}).get("type", "lambda"),
                    "inputs": manifest.get("inputs", {}),
                    "outputs": manifest.get("outputs", {}),
                }
            )

        client.register_module(module_id, metadata)
        console.print("  ✓ Module registered successfully")

        # Success summary
        console.print("\n[green]✓ Module deployed successfully![/green]")
        console.print(f"  Module ID: {module_id}")
        console.print(f"  Name: {module_name}")
        console.print(f"  Version: {module_version}")
        console.print(f"  Environment: {env}")

        console.print("\n[cyan]Execute with:[/cyan]")
        console.print(f"  hla-compass execute {module_id} --input examples/input.json")

    except Exception as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Environment to list from",
)
def list(env: str):
    """List deployed modules"""
    from .auth import Auth
    from .client import APIClient

    console.print(f"[bold blue]Available Modules ({env})[/bold blue]\n")

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Initialize API client
    client = APIClient()

    try:
        modules = client.list_modules()

        if not modules:
            console.print("[yellow]No modules found[/yellow]")
            console.print("Deploy a module with: hla-compass deploy <package>")
            return

        # Display modules in a table
        from rich.table import Table

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Module ID", style="dim")
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Type")
        table.add_column("Status")

        for module in modules:
            table.add_row(
                module.get("id", "N/A"),
                module.get("name", "N/A"),
                module.get("version", "N/A"),
                module.get("compute_type", "lambda"),
                module.get("status", "active"),
            )

        console.print(table)
        console.print(f"\nTotal: {len(modules)} module(s)")

    except Exception as e:
        console.print(f"[red]Error listing modules: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("module_id")
@click.option("--input", "-i", "input_file", required=True, help="Input JSON file")
@click.option("--output", "-o", help="Output file to save results")
@click.option("--wait/--no-wait", default=True, help="Wait for execution to complete")
def execute(module_id: str, input_file: str, output: str | None, wait: bool):
    """Execute a module with input data"""
    from pathlib import Path
    from .auth import Auth
    from .client import APIClient
    import time

    console.print("[bold blue]Module Execution[/bold blue]\n")

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Load input data
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[red]Error: Input file not found: {input_file}[/red]")
        sys.exit(1)

    try:
        with open(input_path) as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in input file: {e}[/red]")
        sys.exit(1)

    # Initialize API client
    client = APIClient()

    console.print(f"📦 Module: {module_id}")
    console.print(f"📄 Input: {input_file}")
    console.print("")

    try:
        # Execute module
        console.print("🚀 Starting execution...")
        response = client.execute_module(module_id, input_data)

        job_id = response.get("job_id")
        if not job_id:
            console.print("[red]Error: No job_id returned[/red]")
            sys.exit(1)

        console.print(f"  ✓ Job submitted (ID: {job_id})")

        if not wait:
            console.print("\n[cyan]Check status with:[/cyan]")
            console.print(f"  hla-compass status {job_id}")
            return

        # Wait for completion
        console.print("\n⏳ Waiting for completion...")
        max_wait = 300  # 5 minutes
        poll_interval = 2  # seconds
        elapsed = 0

        while elapsed < max_wait:
            status_response = client.get_job_status(job_id)
            status = status_response.get("status", "unknown")

            if status == "completed":
                console.print("  ✓ Execution completed")

                # Get results
                result_response = client.get_job_result(job_id)

                # Save or display results
                if output:
                    with open(output, "w") as f:
                        json.dump(result_response, f, indent=2)
                    console.print(f"\n[green]✓ Results saved to: {output}[/green]")
                else:
                    console.print("\n[bold]Results:[/bold]")
                    console.print(json.dumps(result_response, indent=2))

                return

            elif status == "failed":
                console.print("  ✗ Execution failed")
                error_msg = status_response.get("error", "Unknown error")
                console.print(f"[red]Error: {error_msg}[/red]")
                sys.exit(1)

            time.sleep(poll_interval)
            elapsed += poll_interval

        console.print("[yellow]Timeout: Execution taking longer than expected[/yellow]")
        console.print(f"Check status with: hla-compass status {job_id}")

    except Exception as e:
        console.print(f"[red]Execution failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("job_id")
def status(job_id: str):
    """Check job execution status"""
    from .auth import Auth
    from .client import APIClient

    console.print("[bold blue]Job Status[/bold blue]\n")

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Initialize API client
    client = APIClient()

    try:
        response = client.get_job_status(job_id)

        status = response.get("status", "unknown")
        created_at = response.get("created_at", "N/A")
        updated_at = response.get("updated_at", "N/A")

        # Status emoji mapping
        status_icons = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "unknown": "❓",
        }

        console.print(f"Job ID: {job_id}")
        console.print(f"Status: {status_icons.get(status, '')} {status}")
        console.print(f"Created: {created_at}")
        console.print(f"Updated: {updated_at}")

        if status == "completed":
            console.print("\n[green]Job completed successfully![/green]")
            console.print(
                f"Get results with: [cyan]hla-compass results {job_id}[/cyan]"
            )
        elif status == "failed":
            error_msg = response.get("error", "Unknown error")
            console.print(f"\n[red]Job failed: {error_msg}[/red]")
        elif status in ["pending", "running"]:
            console.print(f"\n[yellow]Job is still {status}...[/yellow]")
            console.print(f"Check again with: [cyan]hla-compass status {job_id}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("job_id")
@click.option("--output", "-o", help="Output file to save results")
@click.option(
    "--format",
    type=click.Choice(["json", "summary"]),
    default="json",
    help="Output format",
)
def results(job_id: str, output: str | None, format: str):
    """Get job execution results"""
    from .auth import Auth
    from .client import APIClient

    console.print("[bold blue]Job Results[/bold blue]\n")

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Initialize API client
    client = APIClient()

    try:
        # Check job status first
        status_response = client.get_job_status(job_id)
        status = status_response.get("status", "unknown")

        if status != "completed":
            console.print(f"[yellow]Job status: {status}[/yellow]")
            if status == "failed":
                error_msg = status_response.get("error", "Unknown error")
                console.print(f"[red]Job failed: {error_msg}[/red]")
            else:
                console.print("Results are only available for completed jobs")
            sys.exit(1)

        # Get results
        result_response = client.get_job_result(job_id)

        # Format output
        if format == "summary":
            # Extract summary info
            console.print(f"Job ID: {job_id}")
            console.print(f"Status: ✅ {result_response.get('status', 'completed')}")

            if "summary" in result_response:
                console.print("\n[bold]Summary:[/bold]")
                for key, value in result_response["summary"].items():
                    console.print(f"  {key}: {value}")

            if "results" in result_response:
                console.print(f"\nResult count: {len(result_response['results'])}")
        else:
            # Full JSON output
            output_data = json.dumps(result_response, indent=2)

            if output:
                with open(output, "w") as f:
                    f.write(output_data)
                console.print(f"[green]✓ Results saved to: {output}[/green]")
            else:
                console.print(output_data)

    except Exception as e:
        console.print(f"[red]Error getting results: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
