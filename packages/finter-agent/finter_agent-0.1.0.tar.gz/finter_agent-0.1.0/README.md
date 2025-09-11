# Finter Agent

Quantitative research platform CLI with specialized agents for various research types including signal research, data analysis, machine learning, and backtesting.

## Installation

Install via uv (recommended):

```bash
uv tool install finter-agent
```

Or via pip:

```bash
pip install finter-agent
```

## Usage

Initialize a new quantitative research environment with specialized agents:

### Signal Research (Trading Strategies)
```bash
finter-agent init --signal
```

### Data Research (Analysis & Processing)
```bash
finter-agent init --data
```

### Machine Learning Research
```bash
finter-agent init --ml
```

### Backtesting Research
```bash
finter-agent init --backtest
```

### With Custom Project Name
```bash
finter-agent init --name my-quant-project --signal
```

Default type is `signal` if no research type is specified:
```bash
finter-agent init  # Creates a signal research environment
```

## What it does

The `init` command will:

- ✅ Check and install `uv` if needed
- 🏗️ Create a new project directory
- 🐍 Set up Python virtual environment with uv
- 📦 Install necessary dependencies
- 🤖 Add specialized Claude Code agents for your research type
- 📝 Include CLAUDE.md configuration for optimal development
- 🚀 Configure development environment for quantitative research

## Research Types

- **Signal**: Trading strategy development and signal generation
- **Data**: Data analysis, cleaning, and feature engineering
- **ML**: Machine learning model development and evaluation
- **Backtest**: Strategy backtesting and performance analysis

## Requirements

- Python 3.12+
- Internet connection for package installation

## Development

To contribute to this project:

```bash
git clone https://github.com/quantit/finter-agent.git
cd finter-agent
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## License

MIT License