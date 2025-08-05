import psycopg2, psycopg2.extras
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, traceback
from dotenv import load_dotenv

load_dotenv()
PLANNER_URL = os.getenv("PLANNER_ROUTER_URL")

DB_CONNECTION= os.getenv("DB_CONNECTION")

app = Flask(__name__)
CORS(app)


@app.route("/agent", methods=["POST"])
def route_agent_request():
    try:
        body = request.get_json() or {}
        prompt = body.get("user_prompt", "").strip()
        schema ='''
    Таблица users(user_id, username, email, created_at)

    Таблица wallets(wallet_id, user_id, currency, balance)
    wallets.user_id = users.user_id
    
    Таблица markets(market_id, base_currency, quote_currency)
    
    Таблица orders(order_id, user_id, market_id, side, price, amount, status, created_at)
    orders.user_id = users.user_id  
    orders.market_id = markets.market_id
    
    Таблица trades(trade_id, market_id, buy_order_id, sell_order_id, price, amount, traded_at)
    trades.market_id = markets.market_id  
    trades.buy_order_id = orders.order_id  
    trades.sell_order_id = orders.order_id

'''

        if not prompt:
            return jsonify({"error": "user_prompt не задан"}), 400

        resp = requests.post(f"{PLANNER_URL}/plan", json={"user_prompt": prompt, "schema": schema})
        resp.raise_for_status()
        return jsonify(resp.json()), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Ошибка при обращении к planner-agent",
            "details": traceback.format_exc()
        }), 502

    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "details": traceback.format_exc()
        }), 500


@app.route("/dbinfo", methods=["GET"])
def dbinfo():
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        tables = {}
        for row in cur.fetchall():
            tname, cname, dtype = row["table_name"], row["column_name"], row["data_type"]
            tables.setdefault(tname, []).append({"name": cname, "type": dtype})

        schema = {"tables": [{"name": t, "columns": cols} for t, cols in tables.items()]}

        data = {}
        for t in tables.keys():
            cur.execute(f"SELECT * FROM {t} LIMIT 10")
            data[t] = [dict(r) for r in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify({"schema": schema, "data": data}), 200

    except Exception as e:
        return jsonify({"error": "Не удалось получить информацию о БД", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
