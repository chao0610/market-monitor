import requests
from datetime import datetime
from typing import Dict, Any, Optional
from .base_client import BaseAPIClient

class MetalsAPIClient(BaseAPIClient):
    """Metals-API 客户端 - 用于贵金属价格"""
    
    def __init__(self, api_key: str):
        super().__init__('metals-api', 'https://metals-api.com/api', api_key)
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新贵金属价格
        symbol: XAU(黄金), XAG(白银), XPT(铂金), XPD(钯金)
        返回价格单位为 美元/盎司
        """
        self._rate_limit(1.0)  # 免费版限制
        
        url = f"{self.base_url}/latest"
        params = {
            'access_key': self.api_key,
            'base': 'USD',
            'symbols': symbol
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error', 'Unknown')}")
        
        # Metals-API 返回的是 1/USD 格式，需要转换
        # 例如黄金 0.0005 表示 1/0.0005 = 2000 USD/oz
        rate = data['rates'].get(symbol)
        if rate:
            price = 1 / float(rate)
        else:
            price = 0
        
        return {
            'symbol': symbol,
            'price': price,
            'volume': None,  # Metals-API 不提供成交量
            'market_time': datetime.fromtimestamp(data['timestamp']),
            'source_api': 'metals-api'
        }
    
    def get_historical(self, symbol: str, date: str) -> Dict[str, Any]:
        """
        获取历史价格
        date: YYYY-MM-DD 格式
        """
        self._rate_limit(1.0)
        
        url = f"{self.base_url}/{date}"
        params = {
            'access_key': self.api_key,
            'base': 'USD',
            'symbols': symbol
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
