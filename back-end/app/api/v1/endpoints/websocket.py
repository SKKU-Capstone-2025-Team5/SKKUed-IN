from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.message import MessageRead

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {} # user_id -> WebSocket

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str, recipient_ids: List[int]):
        for user_id in recipient_ids:
            if user_id in self.active_connections:
                await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # For now, just echo back or handle specific commands
            # In a real app, this would parse incoming messages (e.g., read receipts, typing indicators)
            # await manager.send_personal_message(f"You sent: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected.")
