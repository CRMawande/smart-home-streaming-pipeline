CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS measurements (
    time        TIMESTAMPTZ       NOT NULL,
    location    TEXT              NOT NULL,
    metric      TEXT              NOT NULL,
    value       DOUBLE PRECISION  NOT NULL,
    CONSTRAINT value_not_nan CHECK (value IS NOT NULL)
);

SELECT create_hypertable('measurements', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_measurements_metric
ON measurements (metric, time DESC);

