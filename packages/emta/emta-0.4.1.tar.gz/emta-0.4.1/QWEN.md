# Qwen Code Context for EastmoneyTradingLibrary

## Project Overview

This is a Python package named `emta` (EasyMoney Trading Agent). It's an unofficial library for interacting with Eastmoney trading services. The project provides functionality to automate trading operations such as login, placing orders, checking account status, and retrieving market data.

### Key Technologies
- **Language**: Python 3.11
- **Dependency Management**: UV (package management and virtual environment)
- **Build System**: Hatchling
- **Testing**: Pytest
- **Code Quality**:
  - Mypy (static type checking)
  - Ruff (linting and formatting)
  - Pre-commit (git hooks)
- **License**: MIT

### Project Structure
```
EastmoneyTradingLibrary/
├── src/emta/           # Main source code package
│   ├── __init__.py     # Package initializer, exports main classes
│   ├── py.typed        # PEP 561 marker for type hints
│   ├── core/           # Core trading agent implementation
│   │   └── agent.py    # Main trading agent class
│   ├── models/         # Data models and exceptions
│   │   ├── trading.py  # Trading data models
│   │   └── exceptions.py  # Exception classes
│   ├── auth/           # Authentication module
│   │   └── client.py   # Authentication client
│   ├── api/            # API client for trading operations
│   │   └── client.py   # API client implementation
│   └── utils/          # Utility functions
│       ├── encryption.py  # Password encryption utilities
│       ├── captcha.py  # Captcha recognition utilities
│       └── stocks.py   # Stock market code utilities
├── tests/              # Test directory
│   └── test_trading.py # Main test file
├── examples/           # Example usage scripts
│   └── trading_example.py  # Complete example of library usage
├── dist/               # Distribution files (built packages)
├── .python-version     # Specifies Python version (3.11)
├── LICENSE             # MIT license file
├── README.md           # Project documentation
├── pyproject.toml      # Project configuration (metadata, dependencies, tools)
└── uv.lock             # UV lock file for dependencies
```

## Building and Running

### Prerequisites
- Python 3.11 (as specified in `.python-version`)
- UV package manager

### Installation
```bash
pip install emta
```

### Development Setup
1. Clone the repository
2. Install dependencies using UV:
   ```bash
   uv sync
   ```

### Running Tests
Tests are written with pytest. Execute them using:
```bash
uv run pytest
```

### Type Checking
Run mypy for static type checking:
```bash
uv run mypy src/
```

### Linting
Check code style with ruff:
```bash
uv run ruff check src/
```

## Development Conventions

### Code Style
- Follow PEP 8 style guide
- Use type hints for all function signatures and variables where possible
- Ruff is configured with specific rules (E, W, F, I, B, C4, UP, ARG001) and ignores (E501, B008, W191, B904)

### Testing
- Use pytest for writing tests
- Place test files in the `tests/` directory
- Aim for comprehensive test coverage
- Tests use environment variables for credentials (EM_USERNAME, EM_PASSWORD)

### Dependency Management
- Runtime dependencies are defined in `pyproject.toml` under `[project.dependencies]`
- Development dependencies are defined in `pyproject.toml` under `[tool.uv.dev-dependencies]`
- Use `uv.lock` to lock dependency versions for reproducible builds

### Versioning
- Follow semantic versioning (currently at 0.4.0)
- Version is specified in `pyproject.toml`

### Commit Hooks
- Pre-commit is configured for git hooks to ensure code quality before commits

## Core Functionality

### Trading Agent
The main interface is the `TradingAgent` class which provides methods for:
- Login to Eastmoney account
- Logout from Eastmoney account
- Get account information (balance, portfolio)
- Place buy/sell orders
- Query existing orders
- Cancel orders
- Get market data for stocks

### Authentication
The authentication module handles:
- Captcha recognition using ddddocr
- Password encryption using RSA public key
- Session management with validate keys

### API Client
The API client handles:
- Asset and position queries
- Order submission
- Order cancellation
- Market data retrieval from Eastmoney

### Data Models
The models module provides:
- Data classes for account information, positions, and portfolios
- Enums for order types and statuses
- TypedDicts for structured data
- Custom exceptions for error handling

## Usage Example

```python
from emta import TradingAgent, OrderType

# Create a trading agent
agent = TradingAgent("your_username", "your_password")

# Login to Eastmoney
if agent.login():
    # Place a buy order
    order_id = agent.place_order("600000", OrderType.BUY, 100, 12.5)

    # Get market data
    market_data = agent.get_market_data("600000")

    # Logout
    agent.logout()
```

## Current Status
The project is in active development with the following features implemented:
- [x] Login to Eastmoney
- [x] Modular code structure
- [x] Error handling
- [x] Trading agent with order placement and management
- [x] Market data retrieval

The library provides a complete interface for automated trading with Eastmoney, handling all the complexities of authentication, encryption, and API interactions.
