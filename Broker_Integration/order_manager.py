"""
Order Manager
Manages order lifecycle and tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict

from backend.models.trading_models import (
    Order, TradingSignal, OrderDirection, OrderType, OrderStatus
)
from .openalgo_wrapper import OpenAlgoWrapper


class OrderManager:
    """
    Manages order submission, tracking, and lifecycle
    """
    
    def __init__(self, wrapper: Optional[OpenAlgoWrapper] = None):
        """
        Initialize order manager
        
        Args:
            wrapper: OpenAlgo wrapper instance
        """
        self.wrapper = wrapper or OpenAlgoWrapper()
        self.active_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []
        self.order_counter = 0
        
        print(f"📋 OrderManager initialized")
    
    def submit_order(self, signal: TradingSignal) -> Optional[Order]:
        """
        Submit an order based on trading signal
        
        Args:
            signal: Trading signal to execute
            
        Returns:
            Order object if successful, None otherwise
        """
        try:
            # Generate order ID
            self.order_counter += 1
            order_id = f"KEEN_{datetime.now().strftime('%Y%m%d')}_{self.order_counter:04d}"
            
            # Map signal direction to action
            action = "BUY" if signal.direction == OrderDirection.BUY else "SELL"
            
            # Determine order type
            order_type = OrderType.MARKET  # Default to market orders
            price = None
            
            # Place order via OpenAlgo
            success, response = self.wrapper.place_order(
                symbol=signal.pair,
                action=action,
                quantity=signal.size,
                price_type="MARKET",
                price=price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            if not success:
                print(f"❌ Order submission failed: {response.get('error', 'Unknown error')}")
                return None
            
            # Extract broker order ID from response
            broker_order_id = response.get('orderid', order_id)
            
            # Create order object
            order = Order(
                order_id=broker_order_id,
                pair=signal.pair,
                direction=signal.direction,
                order_type=order_type,
                size=signal.size,
                price=price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                status=OrderStatus.PENDING,
                created_at=datetime.now()
            )
            
            # Track order
            self.active_orders[broker_order_id] = order
            self.order_history.append(order)
            
            print(f"✅ Order submitted: {broker_order_id}")
            print(f"   Pair: {signal.pair}")
            print(f"   Direction: {action}")
            print(f"   Size: {signal.size}")
            
            return order
            
        except Exception as e:
            print(f"❌ Error submitting order: {e}")
            return None
    
    def track_order(self, order_id: str) -> Optional[OrderStatus]:
        """
        Track order status
        
        Args:
            order_id: Order ID to track
            
        Returns:
            Current order status or None
        """
        if order_id not in self.active_orders:
            return None
        
        try:
            # Get orderbook from broker
            success, orders = self.wrapper.get_orderbook()
            
            if not success:
                return None
            
            # Find our order
            for broker_order in orders:
                if broker_order.get('orderid') == order_id:
                    # Update order status
                    status_map = {
                        'complete': OrderStatus.FILLED,
                        'open': OrderStatus.PENDING,
                        'rejected': OrderStatus.REJECTED,
                        'cancelled': OrderStatus.CANCELLED
                    }
                    
                    broker_status = broker_order.get('status', '').lower()
                    new_status = status_map.get(broker_status, OrderStatus.PENDING)
                    
                    # Update our order
                    order = self.active_orders[order_id]
                    order.status = new_status
                    
                    if new_status == OrderStatus.FILLED:
                        order.filled_at = datetime.now()
                        order.filled_price = float(broker_order.get('price', 0))
                        order.filled_size = float(broker_order.get('quantity', 0))
                    
                    return new_status
            
            return None
            
        except Exception as e:
            print(f"❌ Error tracking order: {e}")
            return None
    
    def modify_order(
        self,
        order_id: str,
        new_quantity: Optional[float] = None,
        new_price: Optional[float] = None
    ) -> bool:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            new_quantity: New quantity
            new_price: New price
            
        Returns:
            True if successful
        """
        if order_id not in self.active_orders:
            print(f"⚠️ Order {order_id} not found")
            return False
        
        try:
            success, response = self.wrapper.modify_order(
                order_id=order_id,
                quantity=new_quantity,
                price=new_price
            )
            
            if success:
                # Update local order
                order = self.active_orders[order_id]
                if new_quantity:
                    order.size = new_quantity
                if new_price:
                    order.price = new_price
                
                print(f"✅ Order {order_id} modified")
                return True
            else:
                print(f"❌ Failed to modify order: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error modifying order: {e}")
            return False
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        if order_id not in self.active_orders:
            print(f"⚠️ Order {order_id} not found")
            return False
        
        try:
            success, response = self.wrapper.cancel_order(order_id)
            
            if success:
                # Update local order
                order = self.active_orders[order_id]
                order.status = OrderStatus.CANCELLED
                
                # Remove from active orders
                del self.active_orders[order_id]
                
                print(f"✅ Order {order_id} cancelled")
                return True
            else:
                print(f"❌ Failed to cancel order: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error cancelling order: {e}")
            return False
    
    def update_all_orders(self) -> None:
        """Update status of all active orders"""
        for order_id in list(self.active_orders.keys()):
            status = self.track_order(order_id)
            
            # Remove filled/cancelled/rejected orders from active list
            if status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                if order_id in self.active_orders:
                    del self.active_orders[order_id]
    
    def get_active_orders(self) -> List[Order]:
        """
        Get list of active orders
        
        Returns:
            List of active orders
        """
        return list(self.active_orders.values())
    
    def get_order_history(self, limit: int = 100) -> List[Order]:
        """
        Get order history
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            List of historical orders
        """
        return self.order_history[-limit:]
    
    def get_order_stats(self) -> Dict[str, Any]:
        """
        Get order statistics
        
        Returns:
            Dictionary with order stats
        """
        total_orders = len(self.order_history)
        active_count = len(self.active_orders)
        
        # Count by status
        status_counts = defaultdict(int)
        for order in self.order_history:
            status_counts[order.status.value] += 1
        
        # Count by direction
        direction_counts = defaultdict(int)
        for order in self.order_history:
            direction_counts[order.direction.value] += 1
        
        return {
            'total_orders': total_orders,
            'active_orders': active_count,
            'status_breakdown': dict(status_counts),
            'direction_breakdown': dict(direction_counts),
            'filled_orders': status_counts[OrderStatus.FILLED.value],
            'cancelled_orders': status_counts[OrderStatus.CANCELLED.value],
            'rejected_orders': status_counts[OrderStatus.REJECTED.value]
        }
    
    def clear_history(self) -> None:
        """Clear order history"""
        self.order_history.clear()
        print(f"🗑️ Order history cleared")


# Global instance
order_manager = OrderManager()
