CREATE TABLE IF NOT EXISTS metric.tos
(
    session String,
    host String,
    time UInt32,
    timestamp DateTime
)
ENGINE = MergeTree()
PRIMARY KEY (session, timestamp)
TTL timestamp + INTERVAL 1 HOUR;
--
--ORDER BY timestamp
--GRANT ALTER DELETE ON metric.tos TO default;
