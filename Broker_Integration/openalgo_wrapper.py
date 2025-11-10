"""
OpenAlgo Wrapper for KeenAI-Quant
Provides simplified interface to OpenAlgo services
"""

import sys
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

# Add openalgo to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'openalgo'))

from backend.models.trading_models import Order, Position, Account, OrderDirection, OrderType, OrderStatus


class OpenAlgoWrapper:
    """
    Wrapper for OpenAlgo services
    Provides simplified interface for broker operations
    """
    
    def __init__(self, broker: str = "mt5", api_key: Optional[str] = None):
        """
        Initialize OpenAlgo wrapper
        
        Args:
            broker: Broker name (default: mt5)
            api_key: API key for authentication
        """
        self.broker = broker
        self.api_key = api_key
        self.auth_token: Optional[str] = None
        
        # Supported trading pairs for KeenAI
        self.supported_pairs = [
            "EUR/USD",
            "XAU/USD", 
            "BTC/USD",
            "ETH/USD"
        ]
        
        print(f"🔌 OpenAlgoWrapper initialized")
        print(f"   Broker: {self.broker}")
        print(f"   Supported pairs: {', '.join(self.supported_pairs)}")
    
    def connect(self) -> bool:
        """
        Establish connection to broker via OpenAlgo
        
        Returns:
            True if connection successful
        """
        try:
            # Import OpenAlgo auth database
            from database.auth_db import get_auth_token_broker
            
            # Get authentication token
            result = get_auth_token_broker()
            
            if result:
                self.auth_token, broker_name = result
                self.broker = broker_name
                print(f"✅ Connected to {broker_name}")
                return True
            else:
                print(f"❌ Failed to get auth token")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def verify_pairs(self) -> Dict[str, bool]:
        """
        Verify that all required trading pairs are available
        
        Returns:
            Dictionary mapping pair to availability status
        """
        availability = {}
        
        for pair in self.supported_pairs:
            # For now, assume all pairs are available
            # In production, would query broker for symbol availability
            availability[pair] = True
        
        print(f"📊 Pair availability:")
        for pair, available in availability.items():
            status = "✅" if available else "❌"
            print(f"   {status} {pair}")
        
        return availability
    
    def get_symbol_info(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get symbol information from broker
        
        Args:
            pair: Trading pair (e.g., "EUR/USD")
            
        Returns:
            Symbol information dictionary or None
        """
        if pair not in self.supported_pairs:
            print(f"⚠️ Unsupported pair: {pair}")
            return None
        
        # Symbol info structure
        # In production, would query actual broker
        symbol_info = {
            'symbol': pair,
            'exchange': 'FOREX' if '/' in pair else 'CRYPTO',
            'lot_size': 1.0,
            'tick_size': 0.00001,
            'min_quantity': 0.01,
            'max_quantity': 100.0
        }
        
        return symbol_info
    
    def _ensure_connected(self) -> bool:
        """
        Ensure connection is established
        
        Returns:
            True if connected
        """
        if not self.auth_token:
            print(f"⚠️ Not connected. Attempting to connect...")
            return self.connect()
        return True
    
    def place_order(
        self,
        symbol: str,
        action: str,
        quantity: float,
        price_type: str = "MARKET",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Place an order via OpenAlgo
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            quantity: Order quantity
            price_type: MARKET or LIMIT
            price: Limit price (for LIMIT orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Tuple of (success, response_data)
        """
        if not self._ensure_connected():
            return False, {'error': 'Not connected to broker'}
        
        try:
            from services.place_order_service import place_order_with_auth
            
            # Prepare order data
            order_data = {
                'apikey': self.api_key,
                'strategy': 'KeenAI-Quant',
                'symbol': symbol,
                'action': action.upper(),
                'exchange': 'NSE',  # Will be mapped by OpenAlgo
                'pricetype': price_type.upper(),
                'product': 'MIS',
                'quantity': str(quantity),
                'position_size': str(quantity)
            }
            
            if price:
                order_data['price'] = str(price)
            
            if stop_loss:
                order_data['trigger_price'] = str(stop_loss)
            
            # Place order
            success, response, status_code = place_order_with_auth(
                self.auth_token,
                self.broker,
                order_data
            )
            
            return success, response
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return False, {'error': str(e)}
    
    def get_orderbook(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Get order book from broker
        
        Returns:
            Tuple of (success, orders_list)
        """
        if not self._ensure_connected():
            return False, []
        
        try:
            from services.orderbook_service import get_orderbook_with_auth
            
            success, response, status_code = get_orderbook_with_auth(
                self.auth_token,
                self.broker
            )
            
            if success and 'data' in response:
                return True, response['data']
            
            return False, []
            
        except Exception as e:
            print(f"❌ Error getting orderbook: {e}")
            return False, []
    
    def get_positionbook(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Get position book from broker
        
        Returns:
            Tuple of (success, positions_list)
        """
        if not self._ensure_connected():
            return False, []
        
        try:
            from services.positionbook_service import get_positionbook_with_auth
            
            success, response, status_code = get_positionbook_with_auth(
                self.auth_token,
                self.broker
            )
            
            if success and 'data' in response:
                return True, response['data']
            
            return False, []
            
        except Exception as e:
            print(f"❌ Error getting positionbook: {e}")
            return False, []
    
    def get_funds(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Get account funds and margin information
        
        Returns:
            Tuple of (success, funds_data)
        """
        if not self._ensure_connected():
            return False, {}
        
        try:
            from services.funds_service import get_funds_with_auth
            
            success, response, status_code = get_funds_with_auth(
                self.auth_token,
                self.broker
            )
            
            if success and 'data' in response:
                return True, response['data']
            
            return False, {}
            
        except Exception as e:
            print(f"❌ Error getting funds: {e}")
            return False, {}
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity
            price: New price
            
        Returns:
            Tuple of (success, response_data)
        """
        if not self._ensure_connected():
            return False, {'error': 'Not connected to broker'}
        
        try:
            from services.modify_order_service import modify_order_with_auth
            
            modify_data = {
                'apikey': self.api_key,
                'strategy': 'KeenAI-Quant',
                'orderid': order_id
            }
            
            if quantity:
                modify_data['quantity'] = str(quantity)
            
            if price:
                modify_data['price'] = str(price)
            
            success, response, status_code = modify_order_with_auth(
                self.auth_token,
                self.broker,
                modify_data
            )
            
            return success, response
            
        except Exception as e:
            print(f"❌ Error modifying order: {e}")
            return False, {'error': str(e)}
    
    def cancel_order(self, order_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Tuple of (success, response_data)
        """
        if not self._ensure_connected():
            return False, {'error': 'Not connected to broker'}
        
        try:
            from services.cancel_order_service import cancel_order_with_auth
            
            cancel_data = {
                'apikey': self.api_key,
                'strategy': 'KeenAI-Quant',
                'orderid': order_id
            }
            
            success, response, status_code = cancel_order_with_auth(
                self.auth_token,
                self.broker,
                cancel_data
            )
            
            return success, response
            
        except Exception as e:
            print(f"❌ Error cancelling order: {e}")
            return False, {'error': str(e)}
    
    def close_position(self, symbol: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Close a position
        
        Args:
            symbol: Symbol to close position for
            
        Returns:
            Tuple of (success, response_data)
        """
        if not self._ensure_connected():
            return False, {'error': 'Not connected to broker'}
        
        try:
            from services.close_position_service import close_position_with_auth
            
            close_data = {
                'apikey': self.api_key,
                'strategy': 'KeenAI-Quant',
                'symbol': symbol,
                'exchange': 'NSE'
            }
            
            success, response, status_code = close_position_with_auth(
                self.auth_token,
                self.broker,
                close_data
            )
            
            return success, response
            
        except Exception as e:
            print(f"❌ Error closing position: {e}")
            return False, {'error': str(e)}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get connection status information
        
        Returns:
            Dictionary with connection status
        """
        return {
            'connected': self.auth_token is not None,
            'broker': self.broker,
            'auth_token_present': bool(self.auth_token),
            'supported_pairs': self.supported_pairs
        }


# Global instance
openalgo_wrapper = OpenAlgoWrapper()
