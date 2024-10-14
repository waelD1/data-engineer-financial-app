CREATE KEYSPACE IF NOT EXISTS finnhub_db
WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1};

USE finnhub_db;

CREATE TABLE IF NOT EXISTS trading_data (
    stock_price DOUBLE,
    stock_symbol TEXT,
    trade_volume DOUBLE,
    unix_trade_timestamp TIMESTAMP,
    date_trade_timestamp TEXT,
    unique_id UUID,
    PRIMARY KEY (stock_symbol, unix_trade_timestamp)
);
