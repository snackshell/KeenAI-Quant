"""
WebSocket Connection Manager
Manages WebSocket connections and broadcasts
"""

from typing import List, Dict
from fastapi import WebSocket
import asyncio
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic in self.subscriptions:
            if websocket in self.subscriptions[topic]:
                self.subscriptions[topic].remove(websocket)
        
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe a connection to a topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
            print(f"📡 Subscribed to topic: {topic}")
    
    def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe a connection from a topic"""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
            print(f"📴 Unsubscribed from topic: {topic}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict, topic: str = None):
        """Broadcast a message to all connections or specific topic"""
        connections = self.subscriptions.get(topic, []) if topic else self.active_connections
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"❌ Error broadcasting: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_price_update(self, pair: str, price: float):
        """Broadcast price update"""
        message = {
            "type": "price_update",
            "data": {
                "pair": pair,
                "price": price,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(message, topic="prices")
    
    async def broadcast_position_update(self, position: dict):
        """Broadcast position update"""
        message = {
            "type": "position_update",
            "data": position,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message, topic="positions")
    
    async def broadcast_trade_execution(self, trade: dict):
        """Broadcast trade execution"""
        message = {
            "type": "trade_executed",
            "data": trade,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message, topic="trades")
    
    async def broadcast_system_status(self, status: dict):
        """Broadcast system status"""
        message = {
            "type": "system_status",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message, topic="status")


# Global connection manager instance
manager = ConnectionManager()
