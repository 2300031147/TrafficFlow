import asyncio
from fastapi import WebSocket
from server.config.settings import settings
import structlog
from server.db.connection import get_pool

logger = structlog.get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, city_id: str):
        await websocket.accept()
        if city_id not in self.active_connections:
            self.active_connections[city_id] = []
        self.active_connections[city_id].append(websocket)
        logger.info("ws_client_connected", city=city_id, count=len(self.active_connections[city_id]))

    def disconnect(self, websocket: WebSocket, city_id: str):
        if city_id in self.active_connections and websocket in self.active_connections[city_id]:
            self.active_connections[city_id].remove(websocket)
            logger.info("ws_client_disconnected", city=city_id)

    async def broadcast_to_city(self, message: dict, city_id: str):
        if city_id in self.active_connections:
            for connection in list(self.active_connections[city_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    self.disconnect(connection, city_id)

manager = ConnectionManager()

async def broadcast_loop():
    logger.info("starting_ws_broadcast_loop")
    while True:
        await asyncio.sleep(settings.websocket_interval_seconds)
        
        cities = list(manager.active_connections.keys())
        if not cities:
            continue
            
        try:
            pool = await get_pool()
            for city in cities:
                if not manager.active_connections.get(city):
                    continue
                    
                async with pool.acquire() as conn:
                    query = """
                    SELECT DISTINCT ON (sd.junction_id)
                        sd.time, sd.junction_id, sd.cycle_length, sd.ns_green, sd.ew_green,
                        sd.ns_demand, sd.ew_demand, sd.efficiency_gain, sd.source,
                        sd.active_event, sd.pattern_confidence, sd.decision_reason
                    FROM signal_decisions sd
                    JOIN junctions j ON sd.junction_id = j.id
                    WHERE j.city = $1
                    ORDER BY sd.junction_id, sd.time DESC
                    """
                    records = await conn.fetch(query, city)

                    for row in records:
                        raw = dict(row)
                        # Serialize all non-JSON-native types (UUIDs, datetimes, Decimals)
                        serialized = {
                            k: str(v) if hasattr(v, 'hex')
                            else v.isoformat() if hasattr(v, 'isoformat')
                            else float(v) if hasattr(v, '__float__') and not isinstance(v, (int, float, bool))
                            else v
                            for k, v in raw.items()
                        }
                        msg = {
                            "type": "SIGNAL_UPDATE",
                            "junction_id": str(row['junction_id']),
                            "data": serialized
                        }
                        await manager.broadcast_to_city(msg, city)
        except Exception as e:
            logger.error("ws_broadcast_error", error=str(e))
