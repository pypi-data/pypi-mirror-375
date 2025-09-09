# 东方财富交易代理 (emta)

[![PyPI version](https://img.shields.io/pypi/v/emta)](https://pypi.org/project/emta/)
[![Python Version](https://img.shields.io/pypi/pyversions/emta)](https://pypi.org/project/emta/)
[![License](https://img.shields.io/pypi/l/emta)](https://github.com/your-username/emta/blob/main/LICENSE)

东方财富非官方Python交易库

## 概述

东方财富交易代理（`emta`）是一个非官方的Python库，提供对东方财富交易平台的编程访问。它支持自动化的交易操作，包括下单、查询账户余额和获取市场数据等功能。

## 主要特性

* **身份验证**：支持验证码识别和密码加密的安全登录
* **订单管理**：支持下单、查询和撤单操作
* **账户信息**：获取账户余额和持仓信息
* **市场数据**：访问股票实时市场数据
* **模块化设计**：代码结构清晰，关注点分离明确
* **类型安全**：完整的类型提示，提高代码可靠性
* **错误处理**：全面的异常处理机制，确保应用稳定性

## 安装

请确保使用Python 3.11或更高版本（但低于4.0）。

```bash
pip install emta
```

## 快速开始

```python
from emta import TradingAgent, OrderType

# 创建交易代理
agent = TradingAgent("your_username", "your_password")

# 登录东方财富
if agent.login():
    # 获取账户信息
    account_info = agent.get_account_info()
    print(f"账户余额: {account_info.get('account_balance', 0)}")

    # 下买单
    order_id = agent.place_order("600000", OrderType.BUY, 100, 12.5)
    if order_id:
        print(f"订单提交成功，订单号: {order_id}")

    # 获取市场数据
    market_data = agent.get_market_data("600000")
    print(f"当前价格: {market_data}")

    # 登出
    agent.logout()
```

完整示例请参见 [examples/trading_example.py](examples/trading_example.py)。

## API 参考

### TradingAgent

与东方财富交易服务交互的主要接口。

#### 构造函数
```python
TradingAgent(username: str | None = None, password: str | None = None)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `login(username=None, password=None, duration=30)` | 东方财富身份验证 |
| `logout()` | 结束当前会话 |
| `get_account_info()` | 获取账户余额和持仓信息 |
| `place_order(stock_code, trade_type, amount, price)` | 下达买入或卖出订单 |
| `query_orders()` | 获取最近的订单列表 |
| `cancel_order(order_id)` | 撤销现有订单 |
| `get_market_data(stock_code)` | 获取股票的当前市场数据 |

## 技术栈

* **Python**: 3.11+
* **依赖管理**: [UV](https://github.com/astral-sh/uv) 用于快速依赖解析
* **HTTP客户端**: [HTTPX](https://www.python-httpx.org/) 用于异步/同步HTTP请求
* **测试**: [Pytest](https://docs.pytest.org/) 用于全面的测试覆盖
* **类型检查**: [Mypy](http://mypy-lang.org/) 用于静态类型分析
* **代码质量**: [Ruff](https://docs.astral.sh/ruff/) 用于代码检查和格式化
* **验证码识别**: [ddddocr](https://github.com/sml2h3/ddddocr) 用于自动验证码识别

## 开发环境搭建

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-username/emta.git
   cd emta
   ```

2. 使用UV安装依赖：
   ```bash
   uv sync
   ```

3. 运行测试：
   ```bash
   uv run pytest
   ```

4. 类型检查：
   ```bash
   uv run mypy src/
   ```

5. 代码检查：
   ```bash
   uv run ruff check src/
   ```

## 项目结构

```
src/emta/
├── __init__.py            # 包初始化文件
├── py.typed               # 类型提示标记
├── core/                  # 核心交易代理实现
│   └── agent.py           # 主要交易代理类
├── models/                # 数据模型和异常
│   ├── trading.py         # 交易数据模型
│   └── exceptions.py      # 异常类
├── auth/                  # 认证模块
│   └── client.py          # 认证客户端
├── api/                   # API客户端交易操作
│   └── client.py          # API客户端实现
└── utils/                 # 工具函数
    ├── encryption.py      # 密码加密工具
    ├── captcha.py         # 验证码识别工具
    └── stocks.py          # 股票市场代码工具
```

## 贡献

欢迎贡献！如果您有改进建议、错误修复或新增功能：

1. Fork 仓库
2. 创建功能分支
3. 进行修改
4. 如适用，请添加测试
5. 确保所有测试通过
6. 提交 pull request

请遵循现有的代码风格，并为新功能添加适当的文档。

## 测试

测试使用 pytest 编写。运行测试：

```bash
uv run pytest
```

运行带覆盖率的测试：

```bash
uv run coverage run -m pytest
uv run coverage report
```

## 许可证

本项目是根据 [MIT 许可证](./LICENSE) 发布的开源软件。
