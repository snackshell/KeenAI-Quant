"""
Position Manager
Manages open positions and P&L tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.models.trading_models import Position, OrderDirection

# Optional OpenAlgo wrapper for fallback
try:
    from .openalgo_wrapper import OpenAlgoWrapper
    OPENALGO_AVAILABLE = True
except ImportError:
    OPENALGO_AVAILABLE = False
    OpenAlgoWrapper = None


class PositionManager:
    """
    Manages open positions and real-time P&L tracking
    """
    
    def __init__(self, wrapper: Optional[Any] = None):
        """
        Initialize position manager
        
        Args:
            wrapper: OpenAlgo wrapper instance (optional, for fallback)
        """
        # OpenAlgo wrapper is optional now
        if OPENALGO_AVAILABLE and wrapper is None:
            try:
                self.wrapper = OpenAlgoWrapper()
            except:
                self.wrapper = None
        else:
            self.wrapper = wrapper
        
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        
        print(f"📊 PositionManager initialized")
    
    def update_positions(self) -> bool:
        """
        Update positions from broker
        
        Returns:
            True if successful
        """
        try:
            # Use broker service for direct MT5 integration
            from .broker_service import broker_service
            
            success, response_data, status_code = broker_service.get_positions()
            
            if not success or 'data' not in response_data:
                print(f"⚠️ Failed to get position book from broker service")
                return False
            
            positions_data = response_data['data']
            
            # Clear current positions
            self.positions.clear()
            
            # Process each position
            for pos_data in positions_data:
                position = self._parse_position(pos_data)
                if position:
                    self.positions[position.pair] = position
            
            print(f"📊 Updated {len(self.positions)} positions")
            return True
            
        except Exception as e:
            print(f"❌ Error updating positions: {e}")
            return False
    
    def _parse_position(self, pos_data: Dict[str, Any]) -> Optional[Position]:
        """
        Parse position data from broker format
        
        Args:
            pos_data: Position data from broker
            
        Returns:
            Position object or None
        """
        try:
            # Extract position details from MT5 format
            symbol = pos_data.get('symbol', '')
            volume = float(pos_data.get('volume', 0))
            
            if volume == 0:
                return None
            
            # Determine direction from type
            position_type = pos_data.get('type', 'LONG')
            direction = OrderDirection.BUY if position_type == 'LONG' else OrderDirection.SELL
            
            # Extract prices
            entry_price = float(pos_data.get('price_open', 0))
            current_price = float(pos_data.get('price_current', entry_price))
            
            # Get P&L directly from broker
            unrealized_pnl = float(pos_data.get('profit', 0))
            
            # Get SL/TP
            stop_loss = float(pos_data.get('sl', 0))
            take_profit = float(pos_data.get('tp', 0))
            
            # Parse timestamp
            time_open_str = pos_data.get('time_open', '')
            try:
                opened_at = datetime.fromisoformat(time_open_str)
            except:
                opened_at = datetime.now()
            
            # Create position object
            position = Position(
                position_id=pos_data.get('position_id', f"{symbol}_{datetime.now().timestamp()}"),
                pair=symbol,
                direction=direction,
                size=volume,
                entry_price=entry_price,
                current_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                unrealized_pnl=unrealized_pnl,
                opened_at=opened_at
            )
            
            return position
            
        except Exception as e:
            print(f"⚠️ Error parsing position: {e}")
            return None
    
    def get_position(self, pair: str) -> Optional[Position]:
        """
        Get position for a specific pair
        
        Args:
            pair: Trading pair
            
        Returns:
            Position object or None
        """
        return self.positions.get(pair)
    
    def get_all_positions(self) -> List[Position]:
        """
        Get all open positions
        
        Returns:
            List of positions
        """
        return list(self.positions.values())
    
    def close_position(self, pair: str) -> bool:
        """
        Close a position
        
        Args:
            pair: Trading pair to close
            
        Returns:
            True if successful
        """
        if pair not in self.positions:
            print(f"⚠️ No open position for {pair}")
            return False
        
        try:
            success, response = self.wrapper.close_position(pair)
            
            if success:
                # Move to closed positions
                position = self.positions[pair]
                self.closed_positions.append(position)
                del self.positions[pair]
                
                print(f"✅ Position closed: {pair}")
                print(f"   P&L: ${position.unrealized_pnl:.2f}")
                return True
            else:
                print(f"❌ Failed to close position: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error closing position: {e}")
            return False
    
    def update_position_prices(self, price_updates: Dict[str, float]) -> None:
        """
        Update current prices for positions
        
        Args:
            price_updates: Dictionary mapping pair to current price
        """
        for pair, price in price_updates.items():
            if pair in self.positions:
                self.positions[pair].update_price(price)
    
    def check_stop_loss(self) -> List[str]:
        """
        Check if any positions hit stop-loss
        
        Returns:
            List of pairs that hit stop-loss
        """
        hit_stop_loss = []
        
        for pair, position in self.positions.items():
            if position.stop_loss == 0:
                continue
            
            if position.direction == OrderDirection.BUY:
                if position.current_price <= position.stop_loss:
                    hit_stop_loss.append(pair)
            else:  # SELL
                if position.current_price >= position.stop_loss:
                    hit_stop_loss.append(pair)
        
        return hit_stop_loss
    
    def check_take_profit(self) -> List[str]:
        """
        Check if any positions hit take-profit
        
        Returns:
            List of pairs that hit take-profit
        """
        hit_take_profit = []
        
        for pair, position in self.positions.items():
            if position.take_profit == 0:
                continue
            
            if position.direction == OrderDirection.BUY:
                if position.current_price >= position.take_profit:
                    hit_take_profit.append(pair)
            else:  # SELL
                if position.current_price <= position.take_profit:
                    hit_take_profit.append(pair)
        
        return hit_take_profit
    
    def monitor_positions(self) -> Dict[str, List[str]]:
        """
        Monitor all positions for stop-loss and take-profit
        
        Returns:
            Dictionary with 'stop_loss' and 'take_profit' lists
        """
        return {
            'stop_loss': self.check_stop_loss(),
            'take_profit': self.check_take_profit()
        }
    
    def calculate_total_pnl(self) -> float:
        """
        Calculate total unrealized P&L across all positions
        
        Returns:
            Total unrealized P&L
        """
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    def get_position_stats(self) -> Dict[str, Any]:
        """
        Get position statistics
        
        Returns:
            Dictionary with position stats
        """
        total_positions = len(self.positions)
        profitable = sum(1 for pos in self.positions.values() if pos.is_profitable)
        losing = total_positions - profitable
        
        total_pnl = self.calculate_total_pnl()
        
        # Calculate by direction
        buy_positions = sum(1 for pos in self.positions.values() if pos.direction == OrderDirection.BUY)
        sell_positions = total_positions - buy_positions
        
        return {
            'total_positions': total_positions,
            'profitable_positions': profitable,
            'losing_positions': losing,
            'buy_positions': buy_positions,
            'sell_positions': sell_positions,
            'total_unrealized_pnl': total_pnl,
            'closed_positions_count': len(self.closed_positions)
        }
    
    def get_closed_positions(self, limit: int = 100) -> List[Position]:
        """
        Get closed positions history
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of closed positions
        """
        return self.closed_positions[-limit:]
    
    def clear_closed_history(self) -> None:
        """Clear closed positions history"""
        self.closed_positions.clear()
        print(f"🗑️ Closed positions history cleared")


# Global instance
position_manager = PositionManager()
