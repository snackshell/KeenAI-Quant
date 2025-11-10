"""
Main Orchestrator for KeenAI-Quant Trading System
Coordinates all system components and manages trading lifecycle
"""

import asyncio
import logging
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System operational states"""
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


class MainOrchestrator:
    """
    Main orchestrator for the trading system
    Manages system lifecycle and coordinates components
    """
    
    def __init__(self):
        """Initialize main orchestrator"""
        self.state = SystemState.STOPPED
        self.start_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        
        # Component managers
        self.account_manager = None
        self.position_manager = None
        self.order_manager = None
        self.agent_orchestrator = None
        
        logger.info("Main Orchestrator initialized")
    
    async def start_trading(self):
        """Start the trading system"""
        try:
            logger.info("Starting trading system...")
            self.state = SystemState.STARTING
            
            # Initialize components
            await self._initialize_components()
            
            # Start trading loop
            self.state = SystemState.RUNNING
            self.start_time = datetime.now()
            
            logger.info("✅ Trading system started successfully")
            
            # Run main trading loop
            await self._trading_loop()
            
        except Exception as e:
            logger.error(f"Error starting trading system: {e}")
            self.state = SystemState.ERROR
            self.error_message = str(e)
            raise
    
    async def stop_trading(self):
        """Stop the trading system"""
        try:
            logger.info("Stopping trading system...")
            self.state = SystemState.STOPPING
            
            # Stop components
            await self._shutdown_components()
            
            self.state = SystemState.STOPPED
            logger.info("✅ Trading system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping trading system: {e}")
            self.state = SystemState.ERROR
            self.error_message = str(e)
            raise
    
    async def pause_trading(self):
        """Pause the trading system"""
        if self.state == SystemState.RUNNING:
            self.state = SystemState.PAUSED
            logger.info("Trading system paused")
    
    async def resume_trading(self):
        """Resume the trading system"""
        if self.state == SystemState.PAUSED:
            self.state = SystemState.RUNNING
            logger.info("Trading system resumed")
    
    async def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Import components
            from Broker_Integration.account_manager import account_manager
            from Broker_Integration.position_manager import position_manager
            from Broker_Integration.order_manager import order_manager
            
            self.account_manager = account_manager
            self.position_manager = position_manager
            self.order_manager = order_manager
            
            # Initialize account
            self.account_manager.update_account()
            
            # Initialize positions
            self.position_manager.update_positions()
            
            logger.info("Components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    async def _shutdown_components(self):
        """Shutdown all system components"""
        try:
            # Stop auto-updates
            if self.account_manager:
                self.account_manager.stop_auto_update()
            
            logger.info("Components shutdown successfully")
            
        except Exception as e:
            logger.error(f"Error shutting down components: {e}")
            raise
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.state == SystemState.RUNNING:
            try:
                # Update account and positions
                if self.account_manager:
                    self.account_manager.update_account()
                
                if self.position_manager:
                    self.position_manager.update_positions()
                
                # Sleep for update interval
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status
        
        Returns:
            Dictionary with system status information
        """
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        status = {
            'state': self.state.value,
            'uptime_seconds': uptime,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'error_message': self.error_message,
            'components': {
                'account_manager': self.account_manager is not None,
                'position_manager': self.position_manager is not None,
                'order_manager': self.order_manager is not None,
            }
        }
        
        # Add account info if available
        if self.account_manager:
            account = self.account_manager.get_account()
            if account:
                status['account'] = {
                    'balance': account.balance,
                    'equity': account.equity,
                    'margin_used': account.margin_used,
                    'unrealized_pnl': account.unrealized_pnl
                }
        
        # Add position info if available
        if self.position_manager:
            positions = self.position_manager.get_all_positions()
            status['positions'] = {
                'count': len(positions),
                'total_pnl': sum(p.unrealized_pnl for p in positions)
            }
        
        return status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        metrics = {
            'state': self.state.value,
            'uptime_seconds': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        }
        
        if self.start_time:
            metrics['uptime_seconds'] = (datetime.now() - self.start_time).total_seconds()
        
        # Add position metrics
        if self.position_manager:
            positions = self.position_manager.get_all_positions()
            metrics['open_positions'] = len(positions)
            metrics['total_unrealized_pnl'] = sum(p.unrealized_pnl for p in positions)
        
        return metrics


# Global instance
main_orchestrator = MainOrchestrator()
