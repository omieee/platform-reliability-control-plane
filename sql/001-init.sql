-- Create all enums required

CREATE TYPE probe_status AS ENUM (
    'FAIL',
    'PASS',
    'UNKNOWN'
    );

CREATE TYPE fail_reason AS ENUM (
    'TIMEOUT',
    'DNS_ERROR',
    'CONNECTION_ERROR',
    'HTTP_ERROR',
    'INVALID_RESPONSE',
    'UNKNOWN'
    );

CREATE TYPE gate_status AS ENUM (
    'PASS',
    'WARN',
    'BLOCK',
    'UNKNOWN'
    );

CREATE TYPE http_method_type AS ENUM (
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT'
    );

-- Create service table

CREATE TABLE service
(
    id   BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url  TEXT NOT NULL
);

-- Create environment table

CREATE TABLE environment
(
    id      BIGSERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    region  TEXT,
    cluster TEXT
);

-- Create probe table

CREATE TABLE probe
(
    id                   UUID PRIMARY KEY,
    probe_env            BIGINT           NOT NULL,
    probe_serv           BIGINT           NOT NULL,
    method               http_method_type NOT NULL,
    path                 TEXT             NOT NULL,
    expected_status_code SMALLINT         NOT NULL CHECK (expected_status_code BETWEEN 100 AND 599),
    timeout_seconds      DECIMAL DEFAULT 2.0 CHECK (timeout_seconds > 0),

    CONSTRAINT fk_probe_environment
        FOREIGN KEY (probe_env)
            REFERENCES environment (id)
            ON DELETE CASCADE,

    CONSTRAINT fk_probe_service
        FOREIGN KEY (probe_serv)
            REFERENCES service (id)
            ON DELETE CASCADE,

    UNIQUE (probe_env, probe_serv, method, path)
);

-- Create probe_result table

CREATE TABLE probe_result
(
    id                 UUID PRIMARY KEY,
    status             probe_status NOT NULL,
    actual_status_code SMALLINT              DEFAULT NULL CHECK (actual_status_code BETWEEN 100 AND 599),
    failure_reason     fail_reason           DEFAULT NULL,
    latency_ms         DECIMAL               DEFAULT NULL CHECK (latency_ms > 0),
    probe_id           UUID         NOT NULL,
    checked_at         timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT fk_probe_probe_result
        FOREIGN KEY (probe_id)
            REFERENCES probe (id)
            ON DELETE RESTRICT
);

-- Create gate_decision table

CREATE TABLE gate_decision
(
    id              uuid PRIMARY KEY,
    status          gate_status,
    decided_at      timestamptz NOT NULL DEFAULT now(),
    probe_result_id UUID,
    service_id      BIGINT,
    env_id          BIGINT,
    CONSTRAINT fk_gate_probe_result
        FOREIGN KEY (probe_result_id)
            REFERENCES probe (id)
            ON DELETE RESTRICT,

    CONSTRAINT fk_gate_service
        FOREIGN KEY (service_id)
            REFERENCES service (id)
            ON DELETE RESTRICT,

    CONSTRAINT fk_gate_environment
        FOREIGN KEY (env_id)
            REFERENCES environment (id)
            ON DELETE RESTRICT

);