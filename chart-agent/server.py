from flask import Flask, request, jsonify
from dotenv import load_dotenv
from agents.chart_type_agent import ChartTypeAgent
from agents.chart_data_agent import ChartDataAgent

load_dotenv()
app = Flask(__name__)
type_agent = ChartTypeAgent()
data_agent = ChartDataAgent()

@app.route("/suggest_types", methods=["POST"])
def suggest_types():
    body = request.get_json()
    types = type_agent.suggest_chart_types(body.get("user_prompt", ""), body.get("results", []))
    return jsonify({"charts_type": types or []})

@app.route("/generate_data", methods=["POST"])
def gen_data():
    body = request.get_json()
    data = data_agent.generate_chart_data(body["user_prompt"], body["results"], body["chart_type"])
    return jsonify({"chart_data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
