"""
Broker Service Layer
Handles all broker interactions with proper error handling and fallbacks
Based on OpenAlgo service patterns
"""

import logging
from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BrokerService:
    """Service layer for broker operations"""
    
    def __init__(self):
        self.mt5_client = None
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """Initialize MT5 client"""
        try:
            from .mt5_client import mt5_client
            self.mt5_client = mt5_client
            logger.info("MT5 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MT5 client: {e}")
            self.mt5_client = None
    
    def get_account_info(self) -> Tuple[bool, Dict[str, Any], int]:
        """
        Get account information from MT5
        
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        if not self.mt5_client:
            return False, {
                'status': 'error',
                'message': 'MT5 client not initialized. Install MetaTrader5: pip install MetaTrader5'
            }, 503
        
        try:
            account = self.mt5_client.get_account_info()
            
            if account:
                return True, {
                    'status': 'success',
                    'data': {
                        'balance': round(account.balance, 2),
                        'equity': round(account.equity, 2),
                        'margin': round(account.margin, 2),
                        'margin_free': round(account.margin_free, 2),
                        'margin_level': round(account.margin_level, 2),
                        'profit': round(account.profit, 2),
                        'currency': account.currency,
                        'leverage': account.leverage,
                        'server': account.server,
                        'login': account.login,
                        'name': account.name,
                        'company': account.company
                    }
                }, 200
            else:
                return False, {
                    'status': 'error',
                    'message': 'Failed to get account info from MT5. Make sure MT5 terminal is running and logged in.'
                }, 500
                
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return False, {
                'status': 'error',
                'message': f'MT5 error: {str(e)}'
            }, 500
    
    def get_positions(self) -> Tuple[bool, Dict[str, Any], int]:
        """
        Get open positions
        
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        try:
            if not self.mt5_client:
                return True, {
                    'status': 'success',
                    'data': []
                }, 200
            
            positions = self.mt5_client.get_positions()
            
            formatted_positions = []
            for pos in positions:
                formatted_positions.append({
                    'position_id': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type,
                    'volume': round(pos.volume, 2),
                    'price_open': round(pos.price_open, 5),
                    'price_current': round(pos.price_current, 5),
                    'profit': round(pos.profit, 2),
                    'swap': round(pos.swap, 2),
                    'commission': round(pos.commission, 2),
                    'sl': round(pos.sl, 5) if pos.sl else 0.0,
                    'tp': round(pos.tp, 5) if pos.tp else 0.0,
                    'time_open': pos.time_open.isoformat(),
                    'comment': pos.comment
                })
            
            return True, {
                'status': 'success',
                'data': formatted_positions
            }, 200
                
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return True, {
                'status': 'success',
                'data': []
            }, 200
    
    def get_orders(self) -> Tuple[bool, Dict[str, Any], int]:
        """
        Get pending orders
        
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        try:
            if not self.mt5_client:
                return True, {
                    'status': 'success',
                    'data': []
                }, 200
            
            orders = self.mt5_client.get_orders()
            
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    'order_id': order.ticket,
                    'symbol': order.symbol,
                    'type': order.type,
                    'volume': round(order.volume, 2),
                    'price_open': round(order.price_open, 5),
                    'sl': round(order.sl, 5) if order.sl else 0.0,
                    'tp': round(order.tp, 5) if order.tp else 0.0,
                    'time_setup': order.time_setup.isoformat(),
                    'comment': order.comment
                })
            
            return True, {
                'status': 'success',
                'data': formatted_orders
            }, 200
                
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return True, {
                'status': 'success',
                'data': []
            }, 200
    
    def get_trade_history(self, days: int = 30) -> Tuple[bool, Dict[str, Any], int]:
        """
        Get trade history
        
        Args:
            days: Number of days to look back
            
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        try:
            if not self.mt5_client:
                return True, {
                    'status': 'success',
                    'data': []
                }, 200
            
            deals = self.mt5_client.get_history_deals(days)
            
            formatted_deals = []
            for deal in deals:
                formatted_deals.append({
                    'deal_id': deal['deal_id'],
                    'order_id': deal['order_id'],
                    'position_id': deal['position_id'],
                    'symbol': deal['symbol'],
                    'type': deal['type'],
                    'volume': round(deal['volume'], 2),
                    'price': round(deal['price'], 5),
                    'profit': round(deal['profit'], 2),
                    'swap': round(deal['swap'], 2),
                    'commission': round(deal['commission'], 2),
                    'time': deal['time'].isoformat(),
                    'comment': deal['comment']
                })
            
            return True, {
                'status': 'success',
                'data': formatted_deals
            }, 200
                
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return True, {
                'status': 'success',
                'data': []
            }, 200
    
    def place_order(self, symbol: str, order_type: str, volume: float,
                   price: float = 0.0, sl: float = 0.0, tp: float = 0.0,
                   comment: str = '') -> Tuple[bool, Dict[str, Any], int]:
        """
        Place a trading order
        
        Args:
            symbol: Trading symbol
            order_type: Order type (BUY, SELL, etc.)
            volume: Order volume
            price: Order price (0 for market orders)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
            
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        try:
            if not self.mt5_client:
                return False, {
                    'status': 'error',
                    'message': 'MT5 client not available'
                }, 503
            
            result = self.mt5_client.place_order(
                symbol=symbol,
                order_type=order_type,
                volume=volume,
                price=price,
                sl=sl,
                tp=tp,
                comment=comment
            )
            
            if result:
                return True, {
                    'status': 'success',
                    'data': result
                }, 200
            else:
                return False, {
                    'status': 'error',
                    'message': 'Failed to place order'
                }, 500
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False, {
                'status': 'error',
                'message': str(e)
            }, 500
    
    def close_position(self, position_id: str) -> Tuple[bool, Dict[str, Any], int]:
        """
        Close a position
        
        Args:
            position_id: Position ticket ID
            
        Returns:
            Tuple containing:
            - Success status (bool)
            - Response data (dict)
            - HTTP status code (int)
        """
        try:
            if not self.mt5_client:
                return False, {
                    'status': 'error',
                    'message': 'MT5 client not available'
                }, 503
            
            success = self.mt5_client.close_position(position_id)
            
            if success:
                return True, {
                    'status': 'success',
                    'message': f'Position {position_id} closed successfully'
                }, 200
            else:
                return False, {
                    'status': 'error',
                    'message': f'Failed to close position {position_id}'
                }, 500
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False, {
                'status': 'error',
                'message': str(e)
            }, 500
    


# Global service instance
broker_service = BrokerService()
