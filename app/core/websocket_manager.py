import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.shipment_subscriptions: Dict[int, Set[str]] = {}
        self.client_subscriptions: Dict[str, Set[int]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()

        await self.send_personal_message({
            "type": "welcome",
            "client_id": client_id,
            "message": "Connected to ShipTrack real-time tracking"
        }, client_id)

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            for shipment_id in self.client_subscriptions.get(client_id, set()):
                if shipment_id in self.shipment_subscriptions:
                    self.shipment_subscriptions[shipment_id].discard(client_id)
                    if not self.shipment_subscriptions[shipment_id]:
                        del self.shipment_subscriptions[shipment_id]

            del self.active_connections[client_id]
            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                self.disconnect(client_id)

    async def broadcast_to_shipment(self, message: dict, shipment_id: int):
        if shipment_id in self.shipment_subscriptions:
            clients = self.shipment_subscriptions[shipment_id].copy()
            for client_id in clients:
                await self.send_personal_message(message, client_id)

    async def subscribe_to_shipment(self, client_id: str, shipment_id: int, db: AsyncSession):
        # Import here to avoid circular imports
        from app.models.shipment import Shipment

        result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
        shipment = result.scalar_one_or_none()

        if not shipment:
            await self.send_personal_message({
                "type": "error",
                "message": "Shipment not found"
            }, client_id)
            return False

        if shipment_id not in self.shipment_subscriptions:
            self.shipment_subscriptions[shipment_id] = set()

        self.shipment_subscriptions[shipment_id].add(client_id)
        self.client_subscriptions[client_id].add(shipment_id)

        await self.send_personal_message({
            "type": "subscribed",
            "shipment_id": shipment_id,
            "status": "success",
            "tracking_number": shipment.tracking_number
        }, client_id)

        return True

    async def unsubscribe_from_shipment(self, client_id: str, shipment_id: int):
        if shipment_id in self.shipment_subscriptions:
            self.shipment_subscriptions[shipment_id].discard(client_id)
            if not self.shipment_subscriptions[shipment_id]:
                del self.shipment_subscriptions[shipment_id]

        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(shipment_id)

        await self.send_personal_message({
            "type": "unsubscribed",
            "shipment_id": shipment_id
        }, client_id)

manager = ConnectionManager()

