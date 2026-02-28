import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from config.database import get_connection

@dataclass
class AlertState:
    """标的的预警状态"""
    symbol_id: int
    n1: int = 0  # 30分钟上涨计数器
    n2: int = 0  # 30分钟下跌计数器
    m1: int = 0  # 2小时上涨计数器
    m2: int = 0  # 2小时下跌计数器
    last_trigger_time_30m: Optional[datetime] = None
    last_trigger_time_2h: Optional[datetime] = None
    last_trigger_direction_30m: Optional[str] = None  # 'up' or 'down'
    last_trigger_direction_2h: Optional[str] = None

class AlertRepository:
    """预警状态数据访问"""
    
    @staticmethod
    def init_table():
        """初始化预警状态表"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_states (
                symbol_id INTEGER PRIMARY KEY,
                n1 INTEGER DEFAULT 0,
                n2 INTEGER DEFAULT 0,
                m1 INTEGER DEFAULT 0,
                m2 INTEGER DEFAULT 0,
                last_trigger_time_30m TIMESTAMP,
                last_trigger_time_2h TIMESTAMP,
                last_trigger_direction_30m TEXT,
                last_trigger_direction_2h TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
            )
        ''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_or_create(symbol_id: int) -> AlertState:
        """获取或创建预警状态"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol_id, n1, n2, m1, m2, 
                   last_trigger_time_30m, last_trigger_time_2h,
                   last_trigger_direction_30m, last_trigger_direction_2h
            FROM alert_states WHERE symbol_id = ?
        ''', (symbol_id,))
        row = cursor.fetchone()
        
        if row:
            state = AlertState(
                symbol_id=row[0],
                n1=row[1],
                n2=row[2],
                m1=row[3],
                m2=row[4],
                last_trigger_time_30m=row[5],
                last_trigger_time_2h=row[6],
                last_trigger_direction_30m=row[7],
                last_trigger_direction_2h=row[8]
            )
        else:
            state = AlertState(symbol_id=symbol_id)
            cursor.execute('''
                INSERT INTO alert_states (symbol_id) VALUES (?)
            ''', (symbol_id,))
            conn.commit()
        
        conn.close()
        return state
    
    @staticmethod
    def save(state: AlertState):
        """保存预警状态"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE alert_states SET
                n1 = ?, n2 = ?, m1 = ?, m2 = ?,
                last_trigger_time_30m = ?, last_trigger_time_2h = ?,
                last_trigger_direction_30m = ?, last_trigger_direction_2h = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE symbol_id = ?
        ''', (
            state.n1, state.n2, state.m1, state.m2,
            state.last_trigger_time_30m, state.last_trigger_time_2h,
            state.last_trigger_direction_30m, state.last_trigger_direction_2h,
            state.symbol_id
        ))
        conn.commit()
        conn.close()
