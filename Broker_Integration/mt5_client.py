"""
MT5 Client for Exness Integration
Complete implementation based on OpenAlgo patterns
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MT5Account:
    """MT5 account information"""
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    profit: float
    currency: str
    leverage: int
    server: str
    login: str
    name: str = ""
    company: str = "Exness"


@dataclass
class MT5Position:
    """MT5 position information"""
    ticket: str
    symbol: str
    type: str  # 'LONG' or 'SHORT'
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    commission: float
    sl: float
    tp: float
    time_open: datetime
    comment: str = ""


@dataclass
class MT5Order:
    """MT5 order information"""
    ticket: str
    symbol: str
    type: str
    volume: float
    price_open: float
    sl: float
    tp: float
    time_setup: datetime
    comment: str = ""


class MT5Client:
    """MT5 client for direct broker integration"""
    
    def __init__(self):
        self.mt5 = None
        self.account = None
        self.password = None
        self.server = None
        self.connected = False
        self._load_credentials()
    
    def _load_credentials(self):
        """Load MT5 credentials from environment or hardcoded"""
        # Try environment first
        self.account = int(os.getenv('MT5_ACCOUNT', 0))
        self.password = os.getenv('MT5_PASSWORD', '')
        self.server = os.getenv('MT5_SERVER', '')
        
        # Hardcode if not in environment
        if not self.account:
            self.account = 297025057
            self.password = "Test@2025"
            self.server = "Exness-MT5Trial9"
            logger.info("Using hardcoded MT5 credentials")
        
        logger.info(f"MT5 credentials: Account={self.account}, Server={self.server}")
    
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            
            # Initialize MT5
            if not self.mt5.initialize():
                error = self.mt5.last_error()
                logger.error(f"❌ MT5 initialize() failed: {error}")
                logger.error(f"   Make sure MT5 terminal is running!")
                return False
            
            # Login to account
            if self.account and self.password and self.server:
                authorized = self.mt5.login(
                    self.account, 
                    password=self.password, 
                    server=self.server
                )
                if authorized:
                    logger.info(f"✅ Connected to MT5 Account: {self.account}")
                    self.connected = True
                    return True
                else:
                    error = self.mt5.last_error()
                    logger.error(f"❌ MT5 login failed: {error}")
                    logger.error(f"   Account: {self.account}")
                    logger.error(f"   Server: {self.server}")
                    logger.error(f"   Make sure MT5 terminal is logged in!")
                    return False
            else:
                logger.error("❌ Missing MT5 credentials in .env file")
                return False
                
        except ImportError:
            logger.error("❌ MetaTrader5 module not installed!")
            logger.error("   Install it with: pip install MetaTrader5")
            logger.error("   System CANNOT work without MT5 package!")
            return False
        except Exception as e:
            logger.error(f"❌ MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.mt5 and self.connected:
            self.mt5.shutdown()
            self.connected = False
            logger.info("MT5 disconnected")
    
    def get_account_info(self) -> Optional[MT5Account]:
        """Get account information"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            account_info = self.mt5.account_info()
            if account_info:
                return MT5Account(
                    balance=float(account_info.balance),
                    equity=float(account_info.equity),
                    margin=float(account_info.margin),
                    margin_free=float(account_info.margin_free),
                    margin_level=float(account_info.margin_level) if account_info.margin_level else 0.0,
                    profit=float(account_info.profit),
                    currency=account_info.currency,
                    leverage=int(account_info.leverage),
                    server=account_info.server,
                    login=str(account_info.login),
                    name=account_info.name,
                    company=account_info.company
                )
            return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_positions(self) -> List[MT5Position]:
        """Get open positions"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            positions = self.mt5.positions_get()
            if positions:
                result = []
                for pos in positions:
                    result.append(MT5Position(
                        ticket=str(pos.ticket),
                        symbol=pos.symbol,
                        type='LONG' if pos.type == 0 else 'SHORT',
                        volume=float(pos.volume),
                        price_open=float(pos.price_open),
                        price_current=float(pos.price_current),
                        profit=float(pos.profit),
                        swap=float(pos.swap),
                        commission=float(pos.commission),
                        sl=float(pos.sl) if pos.sl else 0.0,
                        tp=float(pos.tp) if pos.tp else 0.0,
                        time_open=datetime.fromtimestamp(pos.time),
                        comment=pos.comment or ''
                    ))
                return result
            return []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_orders(self) -> List[MT5Order]:
        """Get pending orders"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            orders = self.mt5.orders_get()
            if orders:
                result = []
                for order in orders:
                    result.append(MT5Order(
                        ticket=str(order.ticket),
                        symbol=order.symbol,
                        type=self._get_order_type_string(order.type),
                        volume=float(order.volume_initial),
                        price_open=float(order.price_open),
                        sl=float(order.sl) if order.sl else 0.0,
                        tp=float(order.tp) if order.tp else 0.0,
                        time_setup=datetime.fromtimestamp(order.time_setup),
                        comment=order.comment or ''
                    ))
                return result
            return []
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def get_history_deals(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get trade history"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            deals = self.mt5.history_deals_get(from_date, to_date)
            if deals:
                result = []
                for deal in deals:
                    if deal.entry == 1:  # Entry deals only
                        result.append({
                            'deal_id': str(deal.ticket),
                            'order_id': str(deal.order),
                            'position_id': str(deal.position_id),
                            'symbol': deal.symbol,
                            'type': 'BUY' if deal.type == 0 else 'SELL',
                            'volume': float(deal.volume),
                            'price': float(deal.price),
                            'profit': float(deal.profit),
                            'swap': float(deal.swap),
                            'commission': float(deal.commission),
                            'time': datetime.fromtimestamp(deal.time),
                            'comment': deal.comment or ''
                        })
                return result
            return []
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def _get_order_type_string(self, order_type: int) -> str:
        """Convert MT5 order type to string"""
        type_map = {
            0: 'BUY',
            1: 'SELL',
            2: 'BUY_LIMIT',
            3: 'SELL_LIMIT',
            4: 'BUY_STOP',
            5: 'SELL_STOP',
            6: 'BUY_STOP_LIMIT',
            7: 'SELL_STOP_LIMIT'
        }
        return type_map.get(order_type, 'UNKNOWN')
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: float = 0.0, sl: float = 0.0, tp: float = 0.0, 
                   comment: str = '') -> Optional[Dict[str, Any]]:
        """Place a trading order"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            mt5_type_map = {
                'BUY': self.mt5.ORDER_TYPE_BUY,
                'SELL': self.mt5.ORDER_TYPE_SELL,
                'BUY_LIMIT': self.mt5.ORDER_TYPE_BUY_LIMIT,
                'SELL_LIMIT': self.mt5.ORDER_TYPE_SELL_LIMIT,
                'BUY_STOP': self.mt5.ORDER_TYPE_BUY_STOP,
                'SELL_STOP': self.mt5.ORDER_TYPE_SELL_STOP
            }
            
            mt5_type = mt5_type_map.get(order_type.upper())
            if mt5_type is None:
                logger.error(f"Invalid order type: {order_type}")
                return None
            
            request = {
                'action': self.mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'type': mt5_type,
                'price': price,
                'sl': sl,
                'tp': tp,
                'comment': comment,
                'type_time': self.mt5.ORDER_TIME_GTC,
                'type_filling': self.mt5.ORDER_FILLING_IOC,
            }
            
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                return {
                    'order_id': str(result.order),
                    'deal_id': str(result.deal),
                    'volume': float(result.volume),
                    'price': float(result.price),
                    'comment': result.comment or ''
                }
            else:
                logger.error(f"Order failed: {result.retcode if result else 'No result'}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def close_position(self, position_id: str) -> bool:
        """Close a position"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            positions = self.mt5.positions_get(ticket=int(position_id))
            if not positions:
                logger.error(f"Position {position_id} not found")
                return False
            
            position = positions[0]
            close_type = self.mt5.ORDER_TYPE_SELL if position.type == 0 else self.mt5.ORDER_TYPE_BUY
            
            request = {
                'action': self.mt5.TRADE_ACTION_DEAL,
                'symbol': position.symbol,
                'volume': position.volume,
                'type': close_type,
                'position': int(position_id),
                'comment': 'Close position',
                'type_time': self.mt5.ORDER_TIME_GTC,
                'type_filling': self.mt5.ORDER_FILLING_IOC,
            }
            
            result = self.mt5.order_send(request)
            if result and result.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position {position_id} closed successfully")
                return True
            else:
                logger.error(f"Failed to close position: {result.retcode if result else 'No result'}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False


# Global instance
mt5_client = MT5Client()
