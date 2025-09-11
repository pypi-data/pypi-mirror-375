# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a quantitative research platform CLI tool called "finter-agent" that helps researchers quickly set up specialized development environments for various research types (signal, data, ML, backtesting). The tool creates new quantitative research environments with proper Python tooling, dependencies, and specialized Claude Code agents.

## Development Commands

### Environment Setup
```bash
uv sync                    # Install dependencies and sync environment
source .venv/bin/activate  # Activate virtual environment (Linux/macOS)
.venv\Scripts\activate     # Activate virtual environment (Windows)
uv pip install -e .       # Install package in development mode
```

### Running the CLI
```bash
finter-agent init                            # Initialize signal research environment (default)
finter-agent init --signal                   # Initialize for signal research
finter-agent init --name myproject --signal  # Custom name with specific type
python -m src.cli init                       # Alternative way to run during development
```

### Code Quality
```bash
ruff check .               # Lint code
ruff format .              # Format code
ruff check --fix .         # Auto-fix linting issues
```

### Testing
```bash
pytest                     # Run tests (if test files exist)
```

## Architecture

### Core Components
- **src/cli.py**: Main CLI interface using Click framework with Rich console output, supports multiple research types
- **src/setup.py**: Environment setup logic that handles uv installation, project creation, template copying, and virtual environment setup
- **src/__init__.py**: Package initialization
- **src/templates/**: Template files for different research types including CLAUDE.md and specialized agents

### Key Dependencies
- **finter**: Core quantitative platform library (>=0.4.71)
- **click**: CLI framework for command-line interface
- **rich**: Enhanced terminal output with colors and formatting
- **matplotlib, plotly**: Visualization libraries for quantitative analysis
- **numba**: High-performance numerical computing
- **tqdm**: Progress bars

### Code Style
- Uses Ruff for linting and formatting
- Line length limit: 88 characters
- 4-space indentation
- Type hints required (Python 3.13+)
- Automatic import sorting and code formatting on save

### Entry Points
- Main CLI entry point: `finter-agent` command maps to `src.cli:main`
- The CLI provides an `init` command with research type options:
  - `--signal`: Trading strategy development

### Template Structure
Each research type includes:
- Customized CLAUDE.md configuration
- Specialized Claude Code agent in `.claude/agents/`
- Research-specific best practices and tools