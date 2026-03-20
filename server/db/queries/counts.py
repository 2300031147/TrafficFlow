from server.db.connection import get_connection
import datetime
import structlog

logger = structlog.get_logger(__name__)

# SEC-10: Only accept known lane names from Pi payloads
VALID_LANES = {'north_in', 'south_in', 'east_in', 'west_in',
               'north_out', 'south_out', 'east_out', 'west_out'}

async def get_latest_counts(junction_id: str) -> list[dict]:
    query = """
    SELECT DISTINCT ON (lane) lane, count, queue_length,
      stopped_count, avg_speed, congestion, time
    FROM vehicle_counts
    WHERE junction_id = $1
    ORDER BY lane, time DESC
    """
    async with get_connection() as conn:
        records = await conn.fetch(query, junction_id)
        return [dict(r) for r in records]

async def get_count_history(junction_id: str, minutes: int) -> list[dict]:
    query = """
    SELECT lane, count, queue_length, time
    FROM vehicle_counts
    WHERE junction_id = $1 AND time > NOW() - $2::interval
    ORDER BY time ASC
    LIMIT 1000
    """
    interval_str = f"{minutes} minutes"
    async with get_connection() as conn:
        records = await conn.fetch(query, junction_id, interval_str)
        return [dict(r) for r in records]

async def insert_counts(junction_id: str, timestamp, lanes: dict):
    query = """
    INSERT INTO vehicle_counts (
        time, junction_id, lane, count, queue_length, stopped_count,
        avg_speed, cars, trucks, buses, motorcycles, autorickshaws, congestion
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
    """
    
    if isinstance(timestamp, (int, float)):
        ts = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    elif isinstance(timestamp, datetime.datetime):
        ts = timestamp
    else:
        # M3: fallback for unexpected types (e.g. strings) — never let asyncpg crash
        ts = datetime.datetime.now(datetime.timezone.utc)
        
    async with get_connection() as conn:
        async with conn.transaction():
            for lane_name, data in lanes.items():
                if lane_name not in VALID_LANES:  # SEC-10
                    logger.warning("invalid_lane_name_rejected", lane=lane_name, junction=junction_id)
                    continue
                lane_count = data.get('total_count', 0)
                if lane_count <= 5:
                    congestion = 'clear'
                elif lane_count <= 12:
                    congestion = 'moderate'
                else:
                    congestion = 'heavy'
                    
                await conn.execute(
                    query,
                    ts,
                    junction_id,
                    lane_name,
                    lane_count,
                    data.get('queue_length', 0),
                    data.get('stopped_count', 0),
                    data.get('avg_speed', 0.0),
                    data.get('cars', 0),
                    data.get('trucks', 0),
                    data.get('buses', 0),
                    data.get('motorcycles', 0),
                    data.get('autorickshaws', 0),
                    congestion
                )
