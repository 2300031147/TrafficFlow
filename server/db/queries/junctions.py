from server.db.connection import get_connection

async def get_all_junctions(cities: list[str] = None) -> list[dict]:
    base_query = """
    SELECT j.id, j.name, j.city, j.district, j.state, j.country, j.lat, j.lng,
      j.junction_type, j.status, j.camera_count, j.created_at, j.updated_at,
      COALESCE(vc.congestion, 'clear'::congestion_enum) as congestion
    FROM junctions j
    LEFT JOIN LATERAL (
        SELECT congestion FROM vehicle_counts 
        WHERE junction_id = j.id 
        ORDER BY time DESC LIMIT 1
    ) vc ON true
    """
    
    async with get_connection() as conn:
        if cities:
            query = base_query + " WHERE j.city = ANY($1) AND j.status != 'offline' ORDER BY j.city, j.name"
            records = await conn.fetch(query, cities)
        else:
            query = base_query + " WHERE j.status != 'offline' ORDER BY j.city, j.name"
            records = await conn.fetch(query)
            
        return [dict(r) for r in records]

async def get_junction_by_id(junction_id: str) -> dict | None:
    query = """
    SELECT id, name, city, district, state, country, lat, lng,
      junction_type, status, camera_count, created_at, updated_at
    FROM junctions WHERE id = $1
    """
    async with get_connection() as conn:
        record = await conn.fetchrow(query, junction_id)
        return dict(record) if record else None

async def upsert_junction_heartbeat(junction_id: str, health_data: dict):
    update_q = """
    UPDATE junctions SET status='active', updated_at=NOW()
    WHERE id = $1
    """
    insert_q = """
    INSERT INTO pi_heartbeats (
        time, junction_id, cpu_percent, ram_percent, npu_temp, disk_percent,
        latency_ms, packet_loss_pct, connection_quality, cameras_online,
        decisions_last_window, buffer_pending
    ) VALUES (
        NOW(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
    )
    """
    async with get_connection() as conn:
        async with conn.transaction():
            await conn.execute(update_q, junction_id)
            await conn.execute(
                insert_q,
                junction_id,
                health_data.get('cpu_percent'),
                health_data.get('ram_percent'),
                health_data.get('npu_temp'),
                health_data.get('disk_percent'),
                health_data.get('latency_ms'),
                health_data.get('packet_loss_pct'),
                health_data.get('connection_quality'),
                health_data.get('cameras_online'),
                health_data.get('decisions_last_window'),
                health_data.get('buffer_pending')
            )

async def get_junction_vpn_ip(junction_id: str) -> str | None:
    query = "SELECT vpn_ip FROM junctions WHERE id = $1"
    async with get_connection() as conn:
        record = await conn.fetchrow(query, junction_id)
        return record['vpn_ip'] if record else None

