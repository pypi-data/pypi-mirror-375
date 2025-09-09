"""API client for Eastmoney trading operations."""

from typing import Any

import httpx
from loguru import logger

from emta.models.trading import OrderType

from ..models.exceptions import TradingError

# Base headers for API requests
BASE_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://jywg.18.cn",
    "Host": "jywg.18.cn",
}


class APIClient:
    """Handles API requests to Eastmoney trading services"""

    def __init__(self, session: httpx.Client, validate_key: str | None = None):
        """Initialize the API client.

        Args:
            session: HTTP client session
        """
        self.session = session
        self.logger = logger
        self.validate_key = validate_key

    def _check_response(self, resp: httpx.Response) -> None:
        """Check if response is successful.

        Args:
            resp: HTTP response to check

        Raises:
            TradingError: If response status is not 200
        """
        if resp.status_code != 200:
            self.logger.error(
                f"Request {resp.url} failed, code={resp.status_code}, response={resp.text}"
            )
            raise TradingError(f"API request failed with status {resp.status_code}")

    def query_something(
        self, url: str, req_data: dict[str, Any] | None = None
    ) -> httpx.Response:
        """通用查询函数

        :param url: 请求url
        :param req_data: 请求提交数据,可选
        :return: HTTP响应
        """
        full_url = f"{url}{self.validate_key}"
        if req_data is None:
            req_data = {
                "qqhs": 100,
                "dwc": "",
            }
        headers = BASE_HEADERS.copy()
        headers["X-Requested-With"] = "XMLHttpRequest"
        self.logger.debug(f"(url={full_url}), (data={req_data})")
        resp = self.session.post(full_url, headers=headers, data=req_data)
        self._check_response(resp)
        return resp

    def query_asset_and_position_v1(self) -> dict[str, Any]:
        """Get asset and position information.

        Args:
            validate_key: Validation key for the session

        Returns:
            Dictionary containing asset and position data
        """
        url = "https://jywg.18.cn/Com/queryAssetAndPositionV1?validatekey="
        resp = self.query_something(url)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]

    def submit_trade_v2(
        self,
        stock_code: str,
        trade_type: OrderType,
        market: str,
        price: float,
        amount: int,
    ) -> dict[str, Any]:
        """交易接口, 买入或卖出.

        :param str stock_code: 股票代码
        :param str trade_type: 交易方向,B for buy, S for sell
        :param str market: 股票市场,HA 上海, SA
        :param float price: 股票价格
        :param int amount: 买入/卖出数量
        """
        req_data = {
            "stockCode": stock_code,
            "tradeType": trade_type.value,
            "zqmc": "",
            "market": market,
            "price": price,
            "amount": amount,
        }
        self.logger.info(req_data)
        url = "https://jywg.18.cn/Trade/SubmitTradeV2?validatekey="
        resp = self.query_something(url, req_data=req_data)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]

    def revoke_orders(self, order_str: str) -> str | Any:
        """取消交易接口.

        :param str order_str: 订单字符串, 由成交日期+成交编号组成. 在create_order和query_order接口, Wtrq的值是成交日期, Wtbh的值是成交编号, 格式为: 20240520_130662
        """
        data = {"revokes": order_str.strip()}
        url = "https://jywg.18.cn/Trade/RevokeOrders?validatekey="
        resp = self.query_something(url, req_data=data)
        self._check_response(resp)
        return resp.text.strip()

    def get_orders_data(self) -> dict[str, Any]:
        """查询交易接口."""
        url = "https://jywg.18.cn/Search/GetOrdersData?validatekey="
        resp = self.query_something(url)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]

    def stock_bid_ask_em(self, symbol: str = "000001") -> dict[str, str | float]:
        """
        东方财富-行情报价
        https://quote.eastmoney.com/sz000001.html
        :param symbol: 股票代码
        :type symbol: str
        :return: 行情报价
        :rtype: pandas.DataFrame
        """
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        market_code = 1 if symbol.startswith("6") else 0
        params = {
            "fltt": "2",
            "invt": "2",
            "fields": "f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,"
            "f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,"
            "f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,"
            "f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,"
            "f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,"
            "f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,"
            "f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,"
            "f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295",
            "secid": f"{market_code}.{symbol}",
        }
        resp = self.session.get(url, params=params)
        data_json = resp.json()
        ret_dict = {
            "sell_5": data_json["data"]["f31"],
            "sell_5_vol": data_json["data"]["f32"] * 100,
            "sell_4": data_json["data"]["f33"],
            "sell_4_vol": data_json["data"]["f34"] * 100,
            "sell_3": data_json["data"]["f35"],
            "sell_3_vol": data_json["data"]["f36"] * 100,
            "sell_2": data_json["data"]["f37"],
            "sell_2_vol": data_json["data"]["f38"] * 100,
            "sell_1": data_json["data"]["f39"],
            "sell_1_vol": data_json["data"]["f40"] * 100,
            "buy_1": data_json["data"]["f19"],
            "buy_1_vol": data_json["data"]["f20"] * 100,
            "buy_2": data_json["data"]["f17"],
            "buy_2_vol": data_json["data"]["f18"] * 100,
            "buy_3": data_json["data"]["f15"],
            "buy_3_vol": data_json["data"]["f16"] * 100,
            "buy_4": data_json["data"]["f13"],
            "buy_4_vol": data_json["data"]["f14"] * 100,
            "buy_5": data_json["data"]["f11"],
            "buy_5_vol": data_json["data"]["f12"] * 100,
            "最新": data_json["data"]["f43"],
            "均价": data_json["data"]["f71"],
            "涨幅": data_json["data"]["f170"],
            "涨跌": data_json["data"]["f169"],
            "总手": data_json["data"]["f47"],
            "金额": data_json["data"]["f48"],
            "换手": data_json["data"]["f168"],
            "量比": data_json["data"]["f50"],
            "最高": data_json["data"]["f44"],
            "最低": data_json["data"]["f45"],
            "今开": data_json["data"]["f46"],
            "昨收": data_json["data"]["f60"],
            "涨停": data_json["data"]["f51"],
            "跌停": data_json["data"]["f52"],
            "外盘": data_json["data"]["f49"],
            "内盘": data_json["data"]["f161"],
        }
        return ret_dict
