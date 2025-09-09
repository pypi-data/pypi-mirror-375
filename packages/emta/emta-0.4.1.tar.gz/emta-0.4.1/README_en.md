# Eastmoney Trading Agent (emta)

[![PyPI version](https://img.shields.io/pypi/v/emta)](https://pypi.org/project/emta/)
[![Python Version](https://img.shields.io/pypi/pyversions/emta)](https://pypi.org/project/emta/)
[![License](https://img.shields.io/pypi/l/emta)](https://github.com/your-username/emta/blob/main/LICENSE)

Unofficial Python library for automated trading with Eastmoney (东方财富).

## Overview

The Eastmoney Trading Agent (`emta`) is an unofficial Python library that provides programmatic access to Eastmoney's trading platform. It enables automated trading operations such as placing orders, checking account balances, and retrieving market data.

## Key Features

* **Authentication**: Secure login with captcha recognition and password encryption
* **Order Management**: Place, query, and cancel buy/sell orders
* **Account Information**: Retrieve account balances and portfolio positions
* **Market Data**: Access real-time market data for stocks
* **Modular Design**: Clean, well-structured codebase with clear separation of concerns
* **Type Safety**: Full type hinting for better code reliability
* **Error Handling**: Comprehensive exception handling for robust applications

## Installation

Ensure you are using Python 3.11 or later (but less than 4.0).

```bash
pip install emta
```

## Quick Start

```python
from emta import TradingAgent, OrderType

# Create a trading agent
agent = TradingAgent("your_username", "your_password")

# Login to Eastmoney
if agent.login():
    # Get account information
    account_info = agent.get_account_info()
    print(f"Account balance: {account_info.get('account_balance', 0)}")

    # Place a buy order
    order_id = agent.place_order("600000", OrderType.BUY, 100, 12.5)
    if order_id:
        print(f"Order placed successfully with ID: {order_id}")

    # Get market data
    market_data = agent.get_market_data("600000")
    print(f"Current price: {market_data}")

    # Logout
    agent.logout()
```

For a complete example, see [examples/trading_example.py](examples/trading_example.py).

## API Reference

### TradingAgent

The main interface for interacting with Eastmoney's trading services.

#### Constructor
```python
TradingAgent(username: str | None = None, password: str | None = None)
```

#### Methods

| Method | Description |
|--------|-------------|
| `login(username=None, password=None, duration=30)` | Authenticate with Eastmoney |
| `logout()` | End the current session |
| `get_account_info()` | Retrieve account balance and portfolio |
| `place_order(stock_code, trade_type, amount, price)` | Place a buy or sell order |
| `query_orders()` | Retrieve a list of recent orders |
| `cancel_order(order_id)` | Cancel an existing order |
| `get_market_data(stock_code)` | Get current market data for a stock |

## Technology Stack

* **Python**: 3.11+
* **Dependency Management**: [UV](https://github.com/astral-sh/uv) for fast dependency resolution
* **HTTP Client**: [HTTPX](https://www.python-httpx.org/) for async/sync HTTP requests
* **Testing**: [Pytest](https://docs.pytest.org/) for comprehensive test coverage
* **Type Checking**: [Mypy](http://mypy-lang.org/) for static type analysis
* **Code Quality**: [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
* **Captcha Recognition**: [ddddocr](https://github.com/sml2h3/ddddocr) for automatic captcha solving

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/emta.git
   cd emta
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Type checking:
   ```bash
   uv run mypy src/
   ```

5. Linting:
   ```bash
   uv run ruff check src/
   ```

## Project Structure

```
src/emta/
├── __init__.py            # Package initialization
├── py.typed               # Type hints marker
├── core/                  # Core trading agent implementation
│   └── agent.py           # Main trading agent class
├── models/                # Data models and exceptions
│   ├── trading.py         # Trading data models
│   └── exceptions.py      # Exception classes
├── auth/                  # Authentication module
│   └── client.py          # Authentication client
├── api/                   # API client for trading operations
│   └── client.py          # API client implementation
└── utils/                 # Utility functions
    ├── encryption.py      # Password encryption utilities
    ├── captcha.py         # Captcha recognition utilities
    └── stocks.py          # Stock market code utilities
```

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or additional features:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Submit a pull request

Please follow the existing code style and add appropriate documentation for any new features.

## Testing

Tests are written with pytest. To run the tests:

```bash
uv run pytest
```

To run tests with coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

## License

This project is open-source software released under the [MIT License](./LICENSE).
