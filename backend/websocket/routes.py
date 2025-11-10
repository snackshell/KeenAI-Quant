"""
WebSocket Routes
Real-time data streaming via WebSocket
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

from backend.websocket.manager import manager
from main_orchestrator import main_orchestrator

websocket_router = APIRouter()


@websocket_router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    Clients can subscribe to topics:
    - prices: Price updates every 1 second
    - positions: Position updates on change
    - trades: Trade executions immediately
    - status: System status updates
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to KeenAI-Quant WebSocket",
            "available_topics": ["prices", "positions", "trades", "status"]
        }, websocket)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle subscription requests
            if message.get("action") == "subscribe":
                topic = message.get("topic")
                if topic:
                    manager.subscribe(websocket, topic)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "topic": topic
                    }, websocket)
            
            elif message.get("action") == "unsubscribe":
                topic = message.get("topic")
                if topic:
                    manager.unsubscribe(websocket, topic)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "topic": topic
                    }, websocket)
            
            elif message.get("action") == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {str(e)}")
        manager.disconnect(websocket)


async def start_price_broadcaster():
    """Background task to broadcast price updates"""
    while True:
        try:
            # Get current prices from main orchestrator
            # This would be connected to Data Engine
            # For now, just broadcast system status
            if main_orchestrator.state.value == "RUNNING":
                status = main_orchestrator.get_system_status()
                await manager.broadcast_system_status(status)
            
            await asyncio.sleep(1)  # Broadcast every second
        except Exception as e:
            print(f"❌ Price broadcaster error: {str(e)}")
            await asyncio.sleep(5)
