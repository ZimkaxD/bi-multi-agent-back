from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from agents.manage_sql_agent import ManageSQLAgent

load_dotenv()
DB_CONN = os.getenv("DB_CONNECTION")

app = Flask(__name__)
agent = ManageSQLAgent()

@app.route("/generate_execute", methods=["POST"])
def generate_execute():
    data   = request.get_json()
    schema = data["schema"]
    prompt = data["user_prompt"]
    attempts = data.get("max_attempts", 3)
    out = agent.generate_execute_loop(schema, prompt, attempts)
    code = 200 if "error" not in out else 500
    return jsonify(out), code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
