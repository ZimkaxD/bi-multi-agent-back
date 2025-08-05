-- Схема базы WhiteBird

-- 1. Таблица пользователей
CREATE TABLE users (
    user_id   SERIAL PRIMARY KEY,
    username  VARCHAR(50) NOT NULL UNIQUE,
    email     VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Таблица кошельков (каждый пользователь может иметь несколько валют)
CREATE TABLE wallets (
    wallet_id SERIAL PRIMARY KEY,
    user_id   INT NOT NULL REFERENCES users(user_id),
    currency  VARCHAR(10) NOT NULL,       -- например: BTC, ETH, USDT
    balance   NUMERIC(20,8) NOT NULL DEFAULT 0
);

-- 3. Таблица рынков (торговых пар)
CREATE TABLE markets (
    market_id   SERIAL PRIMARY KEY,
    base_currency  VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    UNIQUE(base_currency, quote_currency)
);

-- 4. Таблица ордеров
CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    user_id      INT NOT NULL REFERENCES users(user_id),
    market_id    INT NOT NULL REFERENCES markets(market_id),
    side         VARCHAR(4) NOT NULL CHECK (side IN ('buy','sell')),
    price        NUMERIC(20,8) NULL,       -- цена лимитного ордера
    amount       NUMERIC(20,8) NOT NULL,
    status       VARCHAR(10) NOT NULL DEFAULT 'open' CHECK (status IN ('open','filled','cancelled')),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 5. Таблица сделок (trades)
CREATE TABLE trades (
    trade_id     SERIAL PRIMARY KEY,
    market_id    INT NOT NULL REFERENCES markets(market_id),
    buy_order_id INT    REFERENCES orders(order_id),
    sell_order_id INT   REFERENCES orders(order_id),
    price        NUMERIC(20,8) NOT NULL,
    amount       NUMERIC(20,8) NOT NULL,
    traded_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Вставка тестовых данных

-- Пользователи
INSERT INTO users(username,email) VALUES
  ('alice','alice@whitebird.com'),
  ('bob','bob@whitebird.com'),
  ('carol','carol@whitebird.com'),
  ('dave','dave@whitebird.com'),
  ('eve','eve@whitebird.com');

-- Кошельки
INSERT INTO wallets(user_id,currency,balance) VALUES
  (1,'BTC',1.23456789),
  (1,'USDT',10000),
  (2,'ETH',5.67891234),
  (3,'USDT',2500),
  (4,'BTC',0.5);

-- Рынки
INSERT INTO markets(base_currency,quote_currency) VALUES
  ('BTC','USDT'),
  ('ETH','USDT'),
  ('BTC','ETH'),
  ('DOGE','USDT'),
  ('ADA','USDT');

-- Ордеры
INSERT INTO orders(user_id,market_id,side,price,amount,status) VALUES
  (1,1,'buy',50000,0.1,'open'),
  (2,1,'sell',51000,0.05,'filled'),
  (3,2,'buy',3000,1.0,'open'),
  (4,4,'sell',0.2,1000,'open'),
  (5,5,'buy',1.5,200,'open');

-- Сделки
INSERT INTO trades(market_id,buy_order_id,sell_order_id,price,amount) VALUES
  (1,1,2,50500,0.05),
  (2,3,NULL,3000,1.0),
  (4,NULL,4,0.2,1000),
  (5,5,NULL,1.5,200),
  (1,1,2,50700,0.02);
-- Схема базы WhiteBird

-- 1. Таблица пользователей
CREATE TABLE users (
    user_id   SERIAL PRIMARY KEY,
    username  VARCHAR(50) NOT NULL UNIQUE,
    email     VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Таблица кошельков (каждый пользователь может иметь несколько валют)
CREATE TABLE wallets (
    wallet_id SERIAL PRIMARY KEY,
    user_id   INT NOT NULL REFERENCES users(user_id),
    currency  VARCHAR(10) NOT NULL,       -- например: BTC, ETH, USDT
    balance   NUMERIC(20,8) NOT NULL DEFAULT 0
);

-- 3. Таблица рынков (торговых пар)
CREATE TABLE markets (
    market_id   SERIAL PRIMARY KEY,
    base_currency  VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    UNIQUE(base_currency, quote_currency)
);

-- 4. Таблица ордеров
CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    user_id      INT NOT NULL REFERENCES users(user_id),
    market_id    INT NOT NULL REFERENCES markets(market_id),
    side         VARCHAR(4) NOT NULL CHECK (side IN ('buy','sell')),
    price        NUMERIC(20,8) NULL,       -- цена лимитного ордера
    amount       NUMERIC(20,8) NOT NULL,
    status       VARCHAR(10) NOT NULL DEFAULT 'open' CHECK (status IN ('open','filled','cancelled')),
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 5. Таблица сделок (trades)
CREATE TABLE trades (
    trade_id     SERIAL PRIMARY KEY,
    market_id    INT NOT NULL REFERENCES markets(market_id),
    buy_order_id INT    REFERENCES orders(order_id),
    sell_order_id INT   REFERENCES orders(order_id),
    price        NUMERIC(20,8) NOT NULL,
    amount       NUMERIC(20,8) NOT NULL,
    traded_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Вставка тестовых данных

-- Пользователи
INSERT INTO users(username,email) VALUES
  ('alice','alice@whitebird.com'),
  ('bob','bob@whitebird.com'),
  ('carol','carol@whitebird.com'),
  ('dave','dave@whitebird.com'),
  ('eve','eve@whitebird.com');

-- Кошельки
INSERT INTO wallets(user_id,currency,balance) VALUES
  (1,'BTC',1.23456789),
  (1,'USDT',10000),
  (2,'ETH',5.67891234),
  (3,'USDT',2500),
  (4,'BTC',0.5);

-- Рынки
INSERT INTO markets(base_currency,quote_currency) VALUES
  ('BTC','USDT'),
  ('ETH','USDT'),
  ('BTC','ETH'),
  ('DOGE','USDT'),
  ('ADA','USDT');

-- Ордеры
INSERT INTO orders(user_id,market_id,side,price,amount,status) VALUES
  (1,1,'buy',50000,0.1,'open'),
  (2,1,'sell',51000,0.05,'filled'),
  (3,2,'buy',3000,1.0,'open'),
  (4,4,'sell',0.2,1000,'open'),
  (5,5,'buy',1.5,200,'open');

-- Сделки
INSERT INTO trades(market_id,buy_order_id,sell_order_id,price,amount) VALUES
  (1,1,2,50500,0.05),
  (2,3,NULL,3000,1.0),
  (4,NULL,4,0.2,1000),
  (5,5,NULL,1.5,200),
  (1,1,2,50700,0.02);
