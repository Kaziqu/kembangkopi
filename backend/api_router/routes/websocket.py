# websocket.py - WebSocket Endpoints
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from connection_manager import manager
import asyncio

router = APIRouter()

@router.websocket("/ws-dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    print("New WebSocket connection attempt")
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive with periodic heartbeat
            try:
                # Wait for any message or heartbeat from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                print(f"Received WebSocket data: {data}")
                
                # Echo back to confirm connection is alive
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send heartbeat if no message received
                try:
                    await websocket.send_text('{"type":"heartbeat","message":"keepalive"}')
                    print("Sent heartbeat to maintain connection")
                except:
                    print("Failed to send heartbeat, connection likely dead")
                    break
                    
    except WebSocketDisconnect:
        print("WebSocket disconnected normally")
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error occurred: {e}")
        await manager.disconnect(websocket)