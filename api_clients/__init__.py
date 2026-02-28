from typing import Dict, Any, Optional
from api_clients.binance_client import BinanceClient
from api_clients.finnhub_client import FinnhubClient
from api_clients.metals_api_client import MetalsAPIClient
from config.database import get_connection

class APIClientFactory:
    """API 客户端工厂，管理 API key 和客户端实例"""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_client(cls, api_name: str) -> Any:
        """获取或创建 API 客户端"""
        if api_name not in cls._instances:
            cls._instances[api_name] = cls._create_client(api_name)
        return cls._instances[api_name]
    
    @classmethod
    def _create_client(cls, api_name: str) -> Any:
        """根据配置创建对应的客户端"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT api_key FROM api_configs WHERE api_name = ? AND status = 1',
            (api_name,)
        )
        row = cursor.fetchone()
        conn.close()
        
        api_key = row[0] if row else None
        
        if api_name == 'binance':
            return BinanceClient(api_key)
        elif api_name == 'finnhub':
            if not api_key:
                raise ValueError("Finnhub API key is required")
            return FinnhubClient(api_key)
        elif api_name == 'metals-api':
            if not api_key:
                raise ValueError("Metals-API key is required")
            return MetalsAPIClient(api_key)
        else:
            raise ValueError(f"Unknown API: {api_name}")
    
    @classmethod
    def set_api_key(cls, api_name: str, api_key: str):
        """设置 API key"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE api_configs SET api_key = ?, updated_at = CURRENT_TIMESTAMP WHERE api_name = ?',
            (api_key, api_name)
        )
        conn.commit()
        conn.close()
        
        # 清除缓存，下次重新创建
        if api_name in cls._instances:
            del cls._instances[api_name]
