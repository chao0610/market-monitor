import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from config.database import get_connection
from models.symbol import Symbol, MarketData

class MarketDataRepository:
    """行情数据仓库"""
    
    @staticmethod
    def get_active_symbols() -> List[Symbol]:
        """获取所有启用的标的"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol_id, symbol_code, symbol_name, symbol_type, 
                   data_source, update_interval, latency_notes, is_active, alert_threshold
            FROM symbols WHERE is_active = 1
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Symbol(
                symbol_id=row[0],
                symbol_code=row[1],
                symbol_name=row[2],
                symbol_type=row[3],
                data_source=row[4],
                update_interval=row[5],
                latency_notes=row[6],
                is_active=bool(row[7]),
                alert_threshold=row[8] if row[8] is not None else 1.0
            )
            for row in rows
        ]
    
    @staticmethod
    def get_symbol_by_code(symbol_code: str) -> Optional[Symbol]:
        """根据代码获取标的"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol_id, symbol_code, symbol_name, symbol_type, 
                   data_source, update_interval, latency_notes, is_active, alert_threshold
            FROM symbols WHERE symbol_code = ?
        ''', (symbol_code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Symbol(
                symbol_id=row[0],
                symbol_code=row[1],
                symbol_name=row[2],
                symbol_type=row[3],
                data_source=row[4],
                update_interval=row[5],
                latency_notes=row[6],
                is_active=bool(row[7]),
                alert_threshold=row[8] if row[8] is not None else 1.0
            )
        return None
    
    @staticmethod
    def save_market_data(symbol_id: int, market_time: datetime, 
                         price: float, volume: Optional[float], 
                         source_api: str) -> int:
        """保存行情数据"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_data (symbol_id, market_time, local_time, price, volume, source_api)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol_id, market_time, datetime.now(), price, volume, source_api))
        data_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return data_id
    
    @staticmethod
    def get_latest_price(symbol_id: int) -> Optional[Dict[str, Any]]:
        """获取最新价格"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, market_time, local_time, source_api
            FROM market_data
            WHERE symbol_id = ?
            ORDER BY market_time DESC
            LIMIT 1
        ''', (symbol_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'price': row[0],
                'market_time': row[1],
                'local_time': row[2],
                'source_api': row[3]
            }
        return None
    
    @staticmethod
    def get_price_history(symbol_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """获取历史价格"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, market_time, local_time, source_api
            FROM market_data
            WHERE symbol_id = ?
            ORDER BY market_time DESC
            LIMIT ?
        ''', (symbol_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'price': row[0],
                'market_time': row[1],
                'local_time': row[2],
                'source_api': row[3]
            }
            for row in rows
        ]
