import json
import os
from typing import Optional

import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from loguru import logger


class Hyperliquid:
    def __init__(
        self,
        config: dict = None,
        network: Optional[str] = "mainnet" or "testnet" or "local",  # 网络环境
        account_address: Optional[str] = None,  # 账户地址
        agent_secret_key: Optional[str] = None,  # 代理密钥
        skip_ws: Optional[bool] = True,  # 是否跳过 ws 连接
        perp_dexs: Optional[list] = None,  # 永续合约
        **kwargs,
    ):
        self.config = config or {}
        if not self.config:
            self.config = self.load_config()

        # 是否跳过 ws 连接
        self.skip_ws = skip_ws
        # 永续合约
        self.perp_dexs = perp_dexs

        # 账户地址
        self.account_address = account_address or ""
        # 代理密钥
        self.agent_secret_key: str = agent_secret_key or ""

        # 网络环境
        match network.lower():
            case "mainnet" | "main" | "prod":
                self.base_url = constants.MAINNET_API_URL  # 正式环境
            case "testnet" | "test" | "dev":
                self.base_url = constants.TESTNET_API_URL  # 测试环境
            case "local":
                self.base_url = constants.LOCAL_API_URL  # 本地环境
            case _:
                self.base_url = constants.MAINNET_API_URL  # 默认正式环境

        logger.debug(f"✅ base url: {self.base_url}")
        logger.debug(f"✅ account address: {self.account_address}")
        # 代理密钥 截断
        logger.debug(f"✅ api agent secret key: {self.agent_secret_key[:10]}...")

        ##################################################################

        # 初始化账户 client
        self.info = self._info()
        # 初始化交易所 client
        self.exchange = self._exchange()

    # 初始化账户信息
    def _info(self):
        return Info(self.base_url, skip_ws=self.skip_ws)

    # 初始化交易所 client
    def _exchange(self):
        account: LocalAccount = eth_account.Account.from_key(self.agent_secret_key)
        logger.debug(f"✅ api agent address: {account.address}")

        ex = Exchange(
            account,
            self.base_url,
            account_address=self.account_address,  # 账户地址
            perp_dexs=self.perp_dexs,  # 永续合约
        )
        return ex

    # 查看账户信息
    def user_state(self, address: str):
        ret = self.info.user_state(address)
        logger.debug(f"✅ user state: {json.dumps(ret, indent=2)}")
        return ret

    def spot_user_state(self, address: str):
        # 查看账户信息
        ret = self.info.spot_user_state(address)
        logger.debug(f"✅ spot user state: {json.dumps(ret, indent=2)}")
        return ret

    def market_open(
        self,
        coin: str,  # 币种
        is_buy: bool,  # 方向
        sz: float,  # 下单数量
        px: Optional[float] = None,  # 下单价格
        slippage: float = 0.01,  # 滑点
    ):
        # 下单
        order = self.exchange.market_open(
            coin,
            is_buy,
            sz,
            px,
            slippage,
        )
        logger.debug(f"✅ market open order: {json.dumps(order, indent=2)}")

        match order["status"]:
            case "ok":
                logger.success("🔥 下单成功")
                for status in order["response"]["data"]["statuses"]:
                    try:
                        filled = status["filled"]
                        logger.debug(
                            f"✅ Order #{filled['oid']} filled {filled['totalSz']} @{filled['avgPx']}"
                        )
                    except KeyError:
                        logger.error(f"❌ Error: {status['error']}")
            case _:
                logger.warning(f"❌ 下单异常: {order}")

        return order

    def market_close(self, coin: str):
        ret = self.exchange.market_close(coin)
        logger.debug(f"✅ market close order: {json.dumps(ret, indent=2)}")
        return ret

    def load_config(self, config_path: str = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        if not os.path.exists(config_path):
            logger.error(f"config file not found: {config_path}")
            return {}

        with open(config_path) as f:
            config = json.load(f)
        return config
