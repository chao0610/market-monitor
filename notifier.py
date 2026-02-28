#!/usr/bin/env python3
"""
消息推送模块
支持飞书推送
"""

import sys
import json
import os
from datetime import datetime
from typing import List

sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from volatility_detector import AlertResult

class AlertNotifier:
    """预警通知器"""
    
    def __init__(self):
        self.enabled = True
        # 飞书 webhook URL（从环境变量或配置文件读取）
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK')
    
    def format_alert(self, alert: AlertResult) -> str:
        """格式化单个预警 - 横向排列"""
        emoji = "🔴" if alert.direction == 'up' else "🟢"
        
        return f"{emoji} {alert.symbol_code}: 5分钟{alert.change_5m:+.2%} | 30分钟{alert.change_30m:+.2%} | 2小时{alert.change_2h:+.2%}"
    
    def format_summary(self, alerts: List[AlertResult]) -> str:
        """格式化简报"""
        if not alerts:
            return ""
        
        header = f"📊 行情预警 {datetime.now().strftime('%m-%d %H:%M')}\n"
        
        alert_texts = [self.format_alert(alert) for alert in alerts]
        
        return header + "\n".join(alert_texts)
    
    def send(self, alerts: List[AlertResult]) -> bool:
        """发送预警"""
        if not alerts:
            return False
        
        message = self.format_summary(alerts)
        
        # 打印到控制台
        print("\n" + "=" * 60)
        print(message)
        print("=" * 60 + "\n")
        
        return True
    
    def get_message(self, alerts: List[AlertResult]) -> str:
        """获取格式化消息（供外部调用）"""
        if not alerts:
            return ""
        return self.format_summary(alerts)


def send_test_alert():
    """测试发送预警"""
    from volatility_detector import AlertResult
    
    notifier = AlertNotifier()
    
    # 创建测试数据
    test_alerts = [
        AlertResult(
            symbol_code="BTCUSDT",
            symbol_name="Bitcoin",
            threshold=0.02,
            change_5m=0.023,
            change_30m=0.051,
            change_2h=0.085,
            triggered_5m=True,
            triggered_30m=True,
            triggered_2h=True,
            direction="up"
        ),
        AlertResult(
            symbol_code="SPY",
            symbol_name="S&P 500 ETF",
            threshold=0.008,
            change_5m=0.005,
            change_30m=0.018,
            change_2h=0.025,
            triggered_5m=False,
            triggered_30m=True,
            triggered_2h=True,
            direction="up"
        ),
    ]
    
    notifier.send(test_alerts)


if __name__ == '__main__':
    send_test_alert()
