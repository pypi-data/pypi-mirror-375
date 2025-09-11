# in agentforge_sdk/cli.py

import click
import os
import json
import zipfile
from pathlib import Path
import importlib.resources as pkg_resources
from .validator import ManifestValidator
from . import templates

MANIFEST_FILE = "agentforge.json"


@click.group()
def main():
    """AgentForge SDK Command Line Interface."""
    pass


@main.command()
@click.argument("project_name")
def init(project_name):
    """Initializes a new AgentForge plugin project."""
    project_path = Path.cwd() / project_name
    tools_path = project_path / "tools"

    if project_path.exists():
        click.echo(f"Error: Directory '{project_name}' already exists.")
        return

    click.echo(f"Initializing plugin in {project_path}...")

    project_path.mkdir()
    tools_path.mkdir()
    (tools_path / "__init__.py").touch()

    manifest_template_content = pkg_resources.read_text(templates, 'agentforge.template.json')
    manifest_data = json.loads(manifest_template_content)

    manifest_data["name"] = project_name.replace("-", " ").title()
    manifest_data["pluginId"] = f"com.yourname.{project_name}" # Placeholder
    manifest_data["roleName"] = project_name.replace("-", " ").title()

    with open(project_path / MANIFEST_FILE, "w") as f:
        json.dump(manifest_data, f, indent=2)

    tool_filename = "sample_tool.py"
    tool_class_name = "SampleTool"
    with open(tools_path / tool_filename, "w") as f:
        f.write(
f"""from agentforge_sdk.base import BaseTool, ToolContext

class {tool_class_name}(BaseTool):
    def __init__(self, context: ToolContext):
        super().__init__(context)
        # Example: Get an API key from the agent's configuration
        # self.api_key = self.context.get_config("MY_API_KEY")

    def run(self, **kwargs) -> str:
        # Your tool's logic goes here.
        # The arguments in **kwargs are sent by the LLM.
        location = kwargs.get("location", "world")
        return f"Hello, {{location}}! This is a sample tool."
""")
    click.echo(f"✅ Project '{project_name}' created successfully!")
    click.echo(f"   - Manifest: {project_path / MANIFEST_FILE}")
    click.echo(f"   - Sample tool: {tools_path / tool_filename}")


@main.command()
def validate():
    """Validates the plugin manifest (agentforge.json)."""
    project_root = Path.cwd()
    click.echo(f"🔍 Validating manifest in {project_root}...")

    validator = ManifestValidator(project_root)
    is_valid = validator.run()

    if is_valid:
        click.secho("✅ Manifest is valid!", fg="green")
    else:
        click.secho("❌ Manifest has errors:", fg="red", bold=True)
        for error in validator.errors:
            click.echo(f"   - {error}")


@main.command()
@click.option('--output', '-o', default='.', help='Output directory for the packaged file.')
def package(output):
    """Validates and packages the plugin into a .afp file."""
    project_root = Path.cwd()
    
    # --- VALIDATION STEP ---
    click.echo("Running pre-package validation...")
    validator = ManifestValidator(project_root)
    if not validator.run():
        click.secho("❌ Validation failed. Please fix the following errors before packaging:", fg="red", bold=True)
        for error in validator.errors:
            click.echo(f"   - {error}")
        # Stop the packaging process if validation fails
        return
    click.secho("✅ Validation successful.", fg="green")
    # --- END VALIDATION STEP ---
    
    # Manifest is now loaded in the validator, so we can reuse it
    manifest_data = validator.manifest_data
    plugin_name = manifest_data.get('name', 'plugin').replace(' ', '_')
    version = manifest_data.get('version', '1.0.0')

    output_filename = f"{plugin_name}-v{version}.afp"
    output_path = Path(output) / output_filename

    click.echo(f"📦 Packaging plugin into {output_path}...")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_root):
            if 'venv' in root or '.git' in root or '__pycache__' in root:
                continue
            for file in files:
                if file == output_filename:
                    continue
                file_path = Path(root) / file
                archive_path = file_path.relative_to(project_root)
                zipf.write(file_path, archive_path)

    click.echo(f"🚀 Plugin packaged successfully!")

if __name__ == '__main__':
    main()