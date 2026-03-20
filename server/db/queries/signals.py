from server.db.connection import get_connection
import json

# SEC-M3: must match decision_source_enum in schema.sql
VALID_SOURCES = {'webster', 'pattern', 'lstm', 'rl', 'manual', 'fallback'}

async def get_signal_history(junction_id: str, hours: int) -> list[dict]:
    query = """
    SELECT time, junction_id, cycle_length, ns_green, ew_green,
           ns_demand, ew_demand, efficiency_gain, source,
           active_event, pattern_confidence, decision_reason
    FROM signal_decisions
    WHERE junction_id = $1 AND time > NOW() - $2::interval
    ORDER BY time DESC
    LIMIT 500
    """
    interval_str = f"{hours} hours"
    async with get_connection() as conn:
        records = await conn.fetch(query, junction_id, interval_str)
        return [dict(r) for r in records]

async def insert_signal_decision(junction_id: str, decision: dict):
    query = """
    INSERT INTO signal_decisions (
        time, junction_id, cycle_length, ns_green, ew_green, ns_demand, ew_demand,
        efficiency_gain, source, active_event, pattern_confidence, raw_counts,
        adjusted_counts, decision_reason
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
    )
    """
    import datetime
    ts = decision.get('time')
    if not ts or ts == 'NOW()':
        ts = datetime.datetime.now(datetime.timezone.utc)
    elif isinstance(ts, (int, float)):
        ts = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    elif not isinstance(ts, datetime.datetime):
        # Fallback for unexpected types (strings etc.) — never let asyncpg crash
        ts = datetime.datetime.now(datetime.timezone.utc)
    async with get_connection() as conn:
        await conn.execute(
            query,
            ts, # requires correct mapping in production
            junction_id,
            decision.get('cycle_length', 0),
            decision.get('ns_green', 0),
            decision.get('ew_green', 0),
            decision.get('ns_demand', 0.0),
            decision.get('ew_demand', 0.0),
            decision.get('efficiency_gain', 0.0),
            decision.get('source', 'webster') if decision.get('source') in VALID_SOURCES else 'webster',
            decision.get('active_event'),
            decision.get('pattern_confidence'),
            json.dumps(decision.get('raw_counts')) if decision.get('raw_counts') else None,
            json.dumps(decision.get('adjusted_counts')) if decision.get('adjusted_counts') else None,
            decision.get('decision_reason')
        )

async def get_active_override(junction_id: str) -> dict | None:
    query = """
    SELECT id::text, junction_id::text, operator_id::text, phase, duration,
           reason, ip_address::text, created_at, cancelled_at, cancelled_by::text
    FROM overrides
    WHERE junction_id = $1
      AND cancelled_at IS NULL
      AND created_at + (duration || ' seconds')::interval > NOW()
    ORDER BY created_at DESC LIMIT 1
    """
    async with get_connection() as conn:
        record = await conn.fetchrow(query, junction_id)
        if record:
            return dict(record)
        return None
