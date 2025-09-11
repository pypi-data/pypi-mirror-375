# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a quantitative research project set up using finter-signal. The project includes tools and frameworks for financial data analysis, strategy development, and backtesting.

## Development Commands

### Environment Management
```bash
uv sync                    # Install/update dependencies
uv add package-name        # Add new dependency
uv remove package-name     # Remove dependency
uv run python script.py    # Run Python script in virtual environment
```

### Common Tasks
```bash
uv run jupyter lab         # Start Jupyter Lab for analysis
uv run python -m pytest   # Run tests
uv run python main.py      # Run main analysis script
```

### Code Quality
```bash
ruff check .               # Lint code
ruff format .              # Format code
ruff check --fix .         # Auto-fix linting issues
```

## Project Structure

```
.
├── data/                  # Raw and processed data files
├── notebooks/             # Jupyter notebooks for analysis
├── src/                   # Source code modules
│   ├── strategies/        # Trading strategies
│   ├── data/             # Data processing utilities
│   ├── analysis/         # Analysis tools
│   └── backtest/         # Backtesting framework
├── tests/                # Unit tests
├── .claude/              # Claude Code agents and configurations
│   └── agents/           # Specialized agents for quant tasks
└── config/               # Configuration files
```

## Key Dependencies

### Core Libraries
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib/plotly**: Data visualization
- **finter**: Quantitative finance library

### Development Tools
- **ruff**: Linting and formatting
- **pytest**: Testing framework
- **jupyter**: Interactive development

## Best Practices

### Data Management
- Store raw data in `data/raw/`
- Keep processed data in `data/processed/`
- Use consistent naming conventions for data files
- Document data sources and transformations

### Code Organization
- Keep strategies in separate modules under `src/strategies/`
- Implement data utilities in `src/data/`
- Use type hints throughout the codebase
- Write tests for all critical functions

### Analysis Workflow
1. Explore data in Jupyter notebooks
2. Develop reusable functions in src modules
3. Create comprehensive backtests
4. Document findings and methodology

## Agent Usage

This project includes specialized Claude Code agents in `.claude/agents/`:
- Use quantitative analysis agents for data processing tasks
- Leverage strategy development agents for trading logic
- Employ backtesting agents for performance evaluation

Example usage:
```
@sample-agent analyze the performance of a momentum strategy on tech stocks
```