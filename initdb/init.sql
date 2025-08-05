DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'business') THEN
        CREATE DATABASE business;
    END IF;
END
$$;

\connect business

DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent') THEN
      CREATE ROLE agent LOGIN PASSWORD 'agent_pass';
   END IF;
END
$$;
GRANT CONNECT ON DATABASE business TO agent;

CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wallets (
    wallet_id SERIAL     PRIMARY KEY,
    user_id   INT        NOT NULL REFERENCES users(user_id),
    currency  VARCHAR(10) NOT NULL,
    balance   NUMERIC(20,8) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS markets (
    market_id      SERIAL PRIMARY KEY,
    base_currency  VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    UNIQUE(base_currency, quote_currency)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id   SERIAL     PRIMARY KEY,
    user_id    INT        NOT NULL REFERENCES users(user_id),
    market_id  INT        NOT NULL REFERENCES markets(market_id),
    side       VARCHAR(4) NOT NULL CHECK (side IN ('buy','sell')),
    price      NUMERIC(20,8),
    amount     NUMERIC(20,8) NOT NULL,
    status     VARCHAR(10) NOT NULL DEFAULT 'open'
                     CHECK (status IN ('open','filled','cancelled')),
    created_at TIMESTAMP  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades (
    trade_id      SERIAL PRIMARY KEY,
    market_id     INT    NOT NULL REFERENCES markets(market_id),
    buy_order_id  INT    REFERENCES orders(order_id),
    sell_order_id INT    REFERENCES orders(order_id),
    price         NUMERIC(20,8) NOT NULL,
    amount        NUMERIC(20,8) NOT NULL,
    traded_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO users(username,email) VALUES
  ('alice','alice@whitebird.com'),
  ('bob','bob@whitebird.com'),
  ('carol','carol@whitebird.com'),
  ('dave','dave@whitebird.com'),
  ('eve','eve@whitebird.com');

INSERT INTO wallets(user_id,currency,balance) VALUES
  (1,'BTC',1.23456789),
  (1,'USDT',10000),
  (2,'ETH',5.67891234),
  (3,'USDT',2500),
  (4,'BTC',0.5);

INSERT INTO markets(base_currency,quote_currency) VALUES
  ('BTC','USDT'),
  ('ETH','USDT'),
  ('BTC','ETH'),
  ('DOGE','USDT'),
  ('ADA','USDT');

INSERT INTO orders(user_id,market_id,side,price,amount,status) VALUES
  (1,1,'buy',50000,0.1,'open'),
  (2,1,'sell',51000,0.05,'filled'),
  (3,2,'buy',3000,1.0,'open'),
  (4,4,'sell',0.2,1000,'open'),
  (5,5,'buy',1.5,200,'open');

INSERT INTO trades(market_id,buy_order_id,sell_order_id,price,amount) VALUES
  (1,1,2,50500,0.05),
  (2,3,NULL,3000,1.0),
  (4,NULL,4,0.2,1000),
  (5,5,NULL,1.5,200),
  (1,1,2,50700,0.02);

GRANT USAGE ON SCHEMA public TO agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE ON TABLES TO agent;
