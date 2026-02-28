#!/usr/bin/env python3
"""
波动检测和预警模块
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from models.symbol import Symbol
from models.market_data import MarketDataRepository
from models.alert_state import AlertState, AlertRepository

@dataclass
class AlertResult:
    """预警结果"""
    symbol_code: str
    symbol_name: str
    threshold: float
    change_5m: float
    change_30m: float
    change_2h: float
    triggered_5m: bool
    triggered_30m: bool
    triggered_2h: bool
    direction: str  # 'up' or 'down'

class VolatilityDetector:
    """波动检测器"""
    
    def __init__(self):
        self.repo = MarketDataRepository()
        AlertRepository.init_table()
    
    def get_price_at(self, symbol_id: int, minutes_ago: int) -> Optional[float]:
        """获取N分钟前的价格"""
        from datetime import datetime, timedelta
        import sqlite3
        from config.database import get_connection
        
        target_time = datetime.now() - timedelta(minutes=minutes_ago)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price FROM market_data 
            WHERE symbol_id = ? AND market_time <= ?
            ORDER BY market_time DESC
            LIMIT 1
        ''', (symbol_id, target_time))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def calculate_change(self, current_price: float, past_price: Optional[float]) -> float:
        """计算涨跌幅"""
        if past_price is None or past_price == 0:
            return 0.0
        return (current_price - past_price) / past_price
    
    def check_symbol(self, symbol: Symbol, current_price: float) -> Optional[AlertResult]:
        """检测单个标的的波动"""
        
        # 获取历史价格
        price_5m = self.get_price_at(symbol.symbol_id, 5)
        price_30m = self.get_price_at(symbol.symbol_id, 30)
        price_2h = self.get_price_at(symbol.symbol_id, 120)
        
        # 计算涨跌幅
        change_5m = self.calculate_change(current_price, price_5m)
        change_30m = self.calculate_change(current_price, price_30m)
        change_2h = self.calculate_change(current_price, price_2h)
        
        threshold = symbol.alert_threshold
        if threshold is None:
            threshold = 1.0
        
        # 获取预警状态
        state = AlertRepository.get_or_create(symbol.symbol_id)
        now = datetime.now()
        
        # 检查30分钟计数器是否过期
        if state.last_trigger_time_30m:
            if now - state.last_trigger_time_30m > timedelta(minutes=30):
                state.n1 = 0
                state.n2 = 0
        
        # 检查2小时计数器是否过期
        if state.last_trigger_time_2h:
            if now - state.last_trigger_time_2h > timedelta(hours=2):
                state.m1 = 0
                state.m2 = 0
        
        # 检测5分钟波动（固定阈值）
        triggered_5m = abs(change_5m) >= threshold
        
        # 检测30分钟波动（动态阈值）
        threshold_30m_up = (1 + state.n1) * threshold
        threshold_30m_down = (1 + state.n2) * threshold
        triggered_30m_up = change_30m >= threshold_30m_up
        triggered_30m_down = abs(change_30m) >= threshold_30m_down and change_30m < 0
        triggered_30m = triggered_30m_up or triggered_30m_down
        
        # 检测2小时波动（动态阈值）
        threshold_2h_up = (1 + state.m1) * threshold
        threshold_2h_down = (1 + state.m2) * threshold
        triggered_2h_up = change_2h >= threshold_2h_up
        triggered_2h_down = abs(change_2h) >= threshold_2h_down and change_2h < 0
        triggered_2h = triggered_2h_up or triggered_2h_down
        
        # 确定方向
        direction = 'up' if change_5m >= 0 else 'down'
        
        # 更新计数器
        if triggered_30m_up:
            state.n1 += 1
            state.n2 = 0
            state.last_trigger_time_30m = now
            state.last_trigger_direction_30m = 'up'
        elif triggered_30m_down:
            state.n1 = 0
            state.n2 += 1
            state.last_trigger_time_30m = now
            state.last_trigger_direction_30m = 'down'
        
        if triggered_2h_up:
            state.m1 += 1
            state.m2 = 0
            state.last_trigger_time_2h = now
            state.last_trigger_direction_2h = 'up'
        elif triggered_2h_down:
            state.m1 = 0
            state.m2 += 1
            state.last_trigger_time_2h = now
            state.last_trigger_direction_2h = 'down'
        
        # 保存状态
        AlertRepository.save(state)
        
        # 判断是否触发预警
        if triggered_5m or triggered_30m or triggered_2h:
            return AlertResult(
                symbol_code=symbol.symbol_code,
                symbol_name=symbol.symbol_name,
                threshold=threshold,
                change_5m=change_5m,
                change_30m=change_30m,
                change_2h=change_2h,
                triggered_5m=triggered_5m,
                triggered_30m=triggered_30m,
                triggered_2h=triggered_2h,
                direction=direction
            )
        
        return None
    
    def check_all(self) -> List[AlertResult]:
        """检测所有标的"""
        symbols = self.repo.get_active_symbols()
        alerts = []
        
        for symbol in symbols:
            # 获取最新价格
            latest = self.repo.get_latest_price(symbol.symbol_id)
            if latest:
                alert = self.check_symbol(symbol, latest['price'])
                if alert:
                    alerts.append(alert)
        
        return alerts
