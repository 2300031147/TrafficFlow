-- Production schema utilizing TimescaleDB extension for time-series.
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Junctions: All location metadata stays here. Never hardcoded.
CREATE TYPE junction_type_enum AS ENUM ('highway', 'market', 'temple', 'bus_stand', 'residential', 'school', 'hospital', 'railway', 'default');
CREATE TYPE status_enum AS ENUM ('active', 'offline', 'maintenance');

CREATE TABLE junctions (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    district VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    junction_type junction_type_enum NOT NULL DEFAULT 'default',
    pi_device_id VARCHAR UNIQUE,
    vpn_ip VARCHAR UNIQUE,
    api_token_hash VARCHAR,
    status status_enum NOT NULL DEFAULT 'offline',
    camera_count INT DEFAULT 4,
    config_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Counts Hypertable
CREATE TYPE congestion_enum AS ENUM ('clear', 'moderate', 'heavy');

CREATE TABLE vehicle_counts (
    time TIMESTAMPTZ NOT NULL,
    junction_id UUID NOT NULL REFERENCES junctions(id),
    lane VARCHAR NOT NULL,
    count INT NOT NULL,
    queue_length INT NOT NULL DEFAULT 0,
    stopped_count INT NOT NULL DEFAULT 0,
    avg_speed FLOAT NOT NULL DEFAULT 0,
    cars INT NOT NULL DEFAULT 0,
    trucks INT NOT NULL DEFAULT 0,
    buses INT NOT NULL DEFAULT 0,
    motorcycles INT NOT NULL DEFAULT 0,
    autorickshaws INT NOT NULL DEFAULT 0,
    congestion congestion_enum NOT NULL DEFAULT 'clear'
);

SELECT create_hypertable('vehicle_counts', 'time');
CREATE INDEX ix_vc_junction_time ON vehicle_counts (junction_id, time DESC);

-- Signal Decisions Hypertable
CREATE TYPE decision_source_enum AS ENUM ('webster', 'pattern', 'lstm', 'rl', 'manual', 'fallback');

CREATE TABLE signal_decisions (
    time TIMESTAMPTZ NOT NULL,
    junction_id UUID NOT NULL REFERENCES junctions(id),
    cycle_length INT NOT NULL,
    ns_green INT NOT NULL,
    ew_green INT NOT NULL,
    ns_demand FLOAT NOT NULL,
    ew_demand FLOAT NOT NULL,
    efficiency_gain FLOAT NOT NULL DEFAULT 0,
    source decision_source_enum NOT NULL,
    active_event VARCHAR,
    pattern_confidence FLOAT,
    raw_counts JSONB,
    adjusted_counts JSONB,
    decision_reason TEXT
);

SELECT create_hypertable('signal_decisions', 'time');
CREATE INDEX ix_sd_junction_time ON signal_decisions (junction_id, time DESC);

-- Authentication and authorization tables
CREATE TYPE user_role_enum AS ENUM ('viewer', 'operator', 'admin', 'superadmin');

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'viewer',
    city_access TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    last_login_ip INET,
    failed_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    refresh_token_hash VARCHAR
);

-- Forecasts
CREATE TABLE forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    junction_id UUID NOT NULL REFERENCES junctions(id),
    horizon_minutes INT NOT NULL,
    predictions JSONB NOT NULL,
    model_version VARCHAR,
    accuracy_score FLOAT
);
CREATE INDEX ON forecasts (junction_id, created_at DESC);

-- Overrides
CREATE TABLE overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    junction_id UUID NOT NULL REFERENCES junctions(id),
    operator_id UUID NOT NULL REFERENCES users(id),
    phase VARCHAR NOT NULL,
    duration INT NOT NULL,
    reason TEXT,
    ip_address INET,
    cancelled_at TIMESTAMPTZ,
    cancelled_by UUID REFERENCES users(id)
);
CREATE INDEX ON overrides (junction_id, created_at DESC);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    junction_id UUID NOT NULL REFERENCES junctions(id),
    type VARCHAR NOT NULL,
    severity VARCHAR NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    message TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    resolution_note TEXT
);
CREATE INDEX ON alerts (junction_id, created_at DESC);
CREATE INDEX ON alerts (resolved_at) WHERE resolved_at IS NULL;

-- Pi Heartbeats
CREATE TABLE pi_heartbeats (
    time TIMESTAMPTZ NOT NULL,
    junction_id UUID NOT NULL REFERENCES junctions(id),
    cpu_percent FLOAT,
    ram_percent FLOAT,
    npu_temp FLOAT,
    disk_percent FLOAT,
    latency_ms FLOAT,
    packet_loss_pct FLOAT,
    connection_quality VARCHAR,
    cameras_online INT,
    decisions_last_window INT,
    buffer_pending INT
);
SELECT create_hypertable('pi_heartbeats', 'time');
CREATE INDEX ON pi_heartbeats (junction_id, time DESC);

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    action VARCHAR NOT NULL,
    resource VARCHAR,
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT
);
CREATE INDEX ON audit_log (user_id, created_at DESC);
