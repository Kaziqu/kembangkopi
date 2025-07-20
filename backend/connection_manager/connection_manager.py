# connection-manager.py
from fastapi import WebSocket
from typing import List

from fastapi.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            # Send JSON format instead of plain text
            await self.send_json_message(websocket, {
                "type": "connection_status",
                "message": "Connected to server",
                "status": "connected"
            })
        except Exception as e:
            print(f"Error connecting websocket: {e}")

    async def send_json_message(self, websocket: WebSocket, data: dict):
        try:
            if websocket in self.active_connections:
                import json
                await websocket.send_text(json.dumps(data))
        except Exception as e:
            print(f"Error sending JSON message: {e}")

    async def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Check if websocket is still open before closing
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close()
        except Exception as e:
            print(f"Error closing websocket: {e}")

    async def send_message(self, websocket: WebSocket, message: str):
        try:
            if websocket in self.active_connections and websocket.client_state.name == "CONNECTED":
                await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            # Remove dead connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)  

    async def broadcast(self, message: str):
        print(f"Broadcasting to {len(self.active_connections)} active connections")
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                if connection.client_state.name == WebSocketState.CONNECTED:
                    await connection.send_text(message)
                    print(f"Message sent to connection")
                else:
                    print(f"Connection is not active, state: {connection.client_state.name}")
                    disconnected_connections.append(connection)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected_connections:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
                print(f"Removed disconnected connection")