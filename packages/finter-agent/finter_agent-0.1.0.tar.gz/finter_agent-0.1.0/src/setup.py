"""Environment setup functionality."""

import json
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def run_command(
    cmd: list[str], cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)


def check_uv_installed() -> bool:
    """Check if uv is installed on the system."""
    try:
        run_command(["uv", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_uv():
    """Install uv if it's not already installed."""
    console.print("📦 Installing uv...")

    # Use the official uv installation script
    install_cmd = [sys.executable, "-m", "pip", "install", "uv"]

    try:
        run_command(install_cmd)
        console.print("✅ uv installed successfully")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install uv: {e.stderr}")


def copy_templates(project_path: Path, research_type: str = "signal"):
    """Copy template files to the new project based on research type."""
    console.print(f"📄 Copying {research_type} template files...")

    # Get the path to the templates directory
    templates_dir = Path(__file__).parent / "templates"

    try:
        # Copy type-specific CLAUDE.md
        claude_template = templates_dir / research_type / "CLAUDE.md"
        if claude_template.exists():
            shutil.copy2(claude_template, project_path / "CLAUDE.md")

        # Copy type-specific pyproject.toml
        pyproject_template = templates_dir / research_type / "pyproject.toml"
        if pyproject_template.exists():
            shutil.copy2(pyproject_template, project_path / "pyproject.toml")

        # Copy example files if they exist
        example_dir = templates_dir / research_type / "example"
        if example_dir.exists():
            project_example_dir = project_path / "example"
            shutil.copytree(example_dir, project_example_dir)

        # Copy .vscode settings if they exist
        vscode_settings = Path(__file__).parent / ".vscode" / "settings.json"
        if vscode_settings.exists():
            project_vscode_dir = project_path / ".vscode"
            project_vscode_dir.mkdir(exist_ok=True)
            shutil.copy2(vscode_settings, project_vscode_dir / "settings.json")

        # Create .claude/agents directory
        claude_agents_dir = project_path / ".claude" / "agents"
        claude_agents_dir.mkdir(parents=True, exist_ok=True)

        # Read agents list from JSON file
        agents_json_path = templates_dir / research_type / ".claude" / "agents.json"
        agents_to_copy = []

        if agents_json_path.exists():
            with open(agents_json_path, "r") as f:
                agents_to_copy = json.load(f)
        else:
            # Fallback to default signal agent if no JSON file exists
            agents_to_copy = ["signal-agent.md"]

        # Copy the agent templates
        agents_dir = Path(__file__).parent / ".claude" / "agents"
        for agent_file in agents_to_copy:
            agent_template = agents_dir / agent_file
            if agent_template.exists():
                shutil.copy2(agent_template, claude_agents_dir / agent_file)

        # Copy .mcp.json if it exists for the research type
        mcp_template = templates_dir / research_type / ".claude" / ".mcp.json"
        if mcp_template.exists():
            shutil.copy2(mcp_template, project_path / ".mcp.json")

        console.print(
            f"✅ {research_type.capitalize()} template files copied successfully"
        )

    except Exception as e:
        console.print(f"⚠️  Warning: Failed to copy templates: {e}")


def collect_api_key(project_path: Path):
    """Collect Finter API key from user and save to .env file."""
    console.print("\n🔑 Setting up Finter API access...")
    console.print("Opening browser to get your API key...")

    # Open browser to user info page
    webbrowser.open("https://finter.quantit.io/user/info")

    console.print("\n📋 Steps:")
    console.print("1. Log in with your Google account")
    console.print("2. Copy your API key from the page")
    console.print("3. Paste it below")

    # Get API key from user
    api_key = console.input("\n🔐 Enter your Finter API key: ").strip()

    if not api_key:
        console.print("⚠️  No API key provided. You can set it later in .env file")
        return

    # Create .env file
    env_file = project_path / ".env"
    try:
        with open(env_file, "w") as f:
            f.write(f"FINTER_API_KEY={api_key}\n")
        console.print("✅ API key saved to .env file")
    except Exception as e:
        console.print(f"⚠️  Failed to save API key: {e}")


def create_uv_project(project_name: str, project_path: Path):
    """Create a new uv project directory and sync dependencies."""
    console.print(f"🏗️  Creating uv project: {project_name}")

    try:
        # Create virtual environment
        run_command(["uv", "venv"], cwd=project_path)

        console.print("✅ uv project created successfully")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create uv project: {e.stderr}")


def sync_dependencies(project_path: Path):
    """Sync dependencies using uv sync."""
    console.print("📦 Installing dependencies...")

    try:
        # Sync dependencies from pyproject.toml
        run_command(["uv", "sync"], cwd=project_path)

        console.print("✅ Dependencies installed successfully")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to sync dependencies: {e.stderr}")


def setup_environment(project_name: str, research_type: str = "signal"):
    """Set up the complete development environment."""
    project_path = Path.cwd() / project_name

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Check uv installation
        task = progress.add_task("Checking uv installation...", total=None)
        if not check_uv_installed():
            progress.update(task, description="Installing uv...")
            install_uv()
        progress.update(task, description="✅ uv ready")
        progress.remove_task(task)

        # Create project directory
        task = progress.add_task("Creating project directory...", total=None)
        project_path.mkdir(exist_ok=True)
        progress.update(task, description="✅ Project directory created")
        progress.remove_task(task)

        # Copy template files first
        task = progress.add_task("Copying template files...", total=None)
        copy_templates(project_path, research_type)
        progress.update(task, description="✅ Templates copied")
        progress.remove_task(task)

        # Set up uv project
        task = progress.add_task("Setting up uv environment...", total=None)
        create_uv_project(project_name, project_path)
        progress.update(task, description="✅ uv environment ready")
        progress.remove_task(task)

        # Sync dependencies
        task = progress.add_task("Installing dependencies...", total=None)
        sync_dependencies(project_path)
        progress.update(task, description="✅ Dependencies installed")
        progress.remove_task(task)

    # Collect API key after environment setup
    collect_api_key(project_path)

    # Show final instructions
    console.print("\n🎉 Environment setup complete!")
    console.print(f"📁 Project created at: [bold]{project_path}[/bold]")
    console.print("\n📋 Next steps:")
    console.print(f"   cd {project_name}")
    console.print("   uv run python your_script.py")

    # Get agents list for display
    templates_dir = Path(__file__).parent / "templates"
    agents_json_path = templates_dir / research_type / ".claude" / "agents.json"
    agents = []

    if agents_json_path.exists():
        try:
            with open(agents_json_path, "r") as f:
                agents = json.load(f)
        except Exception:
            agents = ["signal-agent.md"]
    else:
        agents = ["signal-agent.md"]

    console.print("\n💡 Template files included:")
    console.print("   - CLAUDE.md: Claude Code configuration")
    console.print(
        f"   - pyproject.toml: {research_type.capitalize()} research dependencies"
    )
    console.print("   - .claude/agents/: Specialized research agents")
    for agent in agents:
        console.print(f"     • {agent}")
    console.print("   - example/: Sample code and notebooks to get started")
    console.print("     • example.py: Basic signal research script")
    console.print("     • example.ipynb: Interactive Jupyter notebook")
    console.print("\n📦 Dependencies installed and ready to use!")
