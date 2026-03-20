from server.db.connection import get_connection

async def get_active_alerts(cities: list[str], resolved: bool = False) -> list[dict]:
    query = """
    SELECT alerts.id::text, alerts.junction_id::text, alerts.type, 
           alerts.severity, alerts.message, alerts.created_at, 
           alerts.resolved_at, alerts.resolved_by::text, alerts.resolution_note,
           junctions.name as junction_name, junctions.city
    FROM alerts JOIN junctions ON alerts.junction_id = junctions.id
    WHERE junctions.city = ANY($1)
    """
    if not resolved:
        query += " AND alerts.resolved_at IS NULL "
    
    query += " ORDER BY alerts.created_at DESC"
    async with get_connection() as conn:
        records = await conn.fetch(query, cities)
        return [dict(r) for r in records]

async def insert_alert(junction_id: str, type: str, severity: str, message: str):
    check_query = """
    SELECT 1 FROM alerts 
    WHERE junction_id = $1 AND type = $2 AND resolved_at IS NULL 
      AND created_at > NOW() - interval '5 minutes'
    """
    insert_query = """
    INSERT INTO alerts (junction_id, type, severity, message)
    VALUES ($1, $2, $3, $4)
    """
    async with get_connection() as conn:
        existing = await conn.fetchrow(check_query, junction_id, type)
        if not existing:
            await conn.execute(insert_query, junction_id, type, severity, message)

async def resolve_alert(alert_id: str, user_id: str, resolution_note: str):
    query = """
    UPDATE alerts SET resolved_at=NOW(), resolved_by=$1, resolution_note=$2
    WHERE id = $3
    """
    async with get_connection() as conn:
        await conn.execute(query, user_id, resolution_note, alert_id)
