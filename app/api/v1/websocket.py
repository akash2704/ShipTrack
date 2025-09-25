import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from app.core.database import get_db

router = APIRouter()

@router.websocket("/ws/tracking")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, client_id)

                elif message_type == "subscribe":
                    shipment_id = message.get("shipment_id")
                    if shipment_id:
                        # Use the same get_db dependency as REST API
                        async for db in get_db():
                            await manager.subscribe_to_shipment(client_id, shipment_id, db)
                            break

                elif message_type == "unsubscribe":
                    shipment_id = message.get("shipment_id")
                    if shipment_id:
                        await manager.unsubscribe_from_shipment(client_id, shipment_id)

                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }, client_id)

            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, client_id)

            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)