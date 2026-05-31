-- FinShield AI — Hive Schema
-- Run inside HiveQL shell: hive -f schema.hql

CREATE DATABASE IF NOT EXISTS finshield;
USE finshield;

-- Raw transactions (partitioned for fast scans)
CREATE TABLE IF NOT EXISTS transactions_raw (
    transaction_id  STRING,
    user_id         STRING,
    merchant_id     STRING,
    amount          DOUBLE,
    currency        STRING,
    transaction_type STRING,
    status          STRING,
    device_id       STRING,
    ip_address      STRING,
    geo_lat         DOUBLE,
    geo_lon         DOUBLE,
    city            STRING,
    timestamp       STRING,
    is_synthetic_fraud BOOLEAN,
    fraud_scenario  STRING
)
PARTITIONED BY (dt STRING, region STRING)
STORED AS PARQUET
TBLPROPERTIES ("parquet.compression"="SNAPPY");

-- Fraud decisions history
CREATE TABLE IF NOT EXISTS fraud_decisions_history (
    transaction_id  STRING,
    user_id         STRING,
    merchant_id     STRING,
    amount          DOUBLE,
    risk_score      FLOAT,
    rule_score      FLOAT,
    ml_score        FLOAT,
    decision        STRING,
    fraud_type      STRING,
    fraud_scenario  STRING,
    timestamp       STRING
)
PARTITIONED BY (dt STRING, decision STRING)
STORED AS PARQUET
TBLPROPERTIES ("parquet.compression"="SNAPPY");

-- Merchant daily summary
CREATE TABLE IF NOT EXISTS merchant_daily_summary (
    merchant_id     STRING,
    total_txns      BIGINT,
    fraud_txns      BIGINT,
    total_amount    DOUBLE,
    blocked_amount  DOUBLE,
    avg_risk_score  FLOAT
)
PARTITIONED BY (dt STRING)
STORED AS PARQUET;
