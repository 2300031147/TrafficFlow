import asyncio
import logging
import uuid
import datetime
import json
import asyncpg
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_database():
    """Populates the junctions table with dummy data for local development testing."""
    db_url = os.getenv("DATABASE_URL", "postgres://urban_admin:urban_password@localhost:5432/urbanflow")
    logger.info("Connecting to local TSDB via connection pool...")
    
    conn = await asyncpg.connect(db_url)
    
    try:
        j_id = "e6a12b6e-bd98-4e89-a3e9-0260ef51f045"
        j2_id = str(uuid.uuid4())
        j3_id = str(uuid.uuid4())

        mock_junctions = [
            (j_id, "Tech Park Entrance", "Bengaluru", "South", "Karnataka", "India", "highway", 12.9716, 77.5946, 4, "10.8.0.2"),
            (j2_id, "MG Road X", "Bengaluru", "Central", "Karnataka", "India", "hospital", 12.9723, 77.6066, 4, "10.8.0.3"),
            (j3_id, "Indiranagar 100ft", "Bengaluru", "East", "Karnataka", "India", "residential", 12.9784, 77.6408, 4, "10.8.0.4")
        ]
        
        logger.info(f"Seeding {len(mock_junctions)} junctions into database.")
        for j in mock_junctions:
            await conn.execute("""
                INSERT INTO junctions (id, name, city, district, state, country, junction_type, lat, lng, camera_count, vpn_ip, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'active')
                ON CONFLICT (id) DO NOTHING
            """, *j)

        logger.info("Populating base users with SECURE passwords...")
        import secrets
        supersec = secrets.token_hex(8)
        opsec = secrets.token_hex(8)
        pwd = bcrypt.hashpw(supersec.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await conn.execute("""
            INSERT INTO users (id, name, email, password_hash, role, city_access)
            VALUES ($1, $2, $3, $4, 'superadmin', ARRAY['Bengaluru'])
            ON CONFLICT (email) DO NOTHING
        """, str(uuid.uuid4()), "System Admin", "admin@urbanflow.local", pwd)

        pwd_operator = bcrypt.hashpw(opsec.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await conn.execute("""
            INSERT INTO users (id, name, email, password_hash, role, city_access)
            VALUES ($1, $2, $3, $4, 'operator', ARRAY['Bengaluru'])
            ON CONFLICT (email) DO NOTHING
        """, str(uuid.uuid4()), "Operator Chief", "operator@urbanflow.local", pwd_operator)

        logger.info(f"*** GENERATED CREDENTIALS ***")
        logger.info(f"Admin: admin@urbanflow.local / {supersec}")
        logger.info(f"Operator: operator@urbanflow.local / {opsec}")

        logger.info("Seeding historical data (last 2 hours) so charts are not empty...")
        import random
        now = datetime.datetime.now(datetime.timezone.utc)
        for j in mock_junctions:
            curr_id = j[0]
            # 2 hours of data = 24 * 5 min windows
            for i in range(24):
                ts = now - datetime.timedelta(hours=2) + datetime.timedelta(minutes=5*i)
                for lane in ['north_in', 'south_in', 'east_in', 'west_in']:
                    c = random.randint(5, 40)
                    congestion = 'heavy' if c > 30 else 'moderate' if c > 15 else 'clear'
                    await conn.execute("""
                        INSERT INTO vehicle_counts (time, junction_id, lane, count, stopped_count, avg_speed, congestion)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, ts, curr_id, lane, c, c//4, random.uniform(10.0, 45.0), congestion)
                
                await conn.execute("""
                    INSERT INTO signal_decisions (time, junction_id, cycle_length, ns_green, ew_green, ns_demand, ew_demand, source)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 'webster')
                """, ts, curr_id, 120, random.randint(30, 60), random.randint(30, 60), random.uniform(0.1, 0.9), random.uniform(0.1, 0.9))

        logger.info("Database Successfully Seeded.")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
