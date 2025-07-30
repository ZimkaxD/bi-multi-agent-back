from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, traceback
from dotenv import load_dotenv

load_dotenv()
PLANNER_URL = os.getenv("PLANNER_ROUTER_URL")

app = Flask(__name__)
CORS(app)


@app.route("/agent", methods=["POST"])
def route_request():
    try:
        body = request.get_json() or {}
        prompt = body.get("user_prompt", "").strip()
        schema ='''
    Таблица clients(client_id, name, industry, contact_name, contact_email, contact_phone, created_at)
    Таблица analysts(analyst_id, first_name, last_name, email, phone, hire_date)
    Таблица projects(project_id, client_id, name, start_date, end_date, status, budget)
    projects.client_id = clients.client_id
    Таблица project_analysts(project_id, analyst_id, assigned_on, role)
    project_analysts.project_id = projects.project_id  
    project_analysts.analyst_id = analysts.analyst_id
    Таблица reports(report_id, project_id, title, created_by, created_at, file_path)
    reports.project_id = projects.project_id  
    reports.created_by = analysts.analyst_id 
    Таблица invoices(invoice_id, project_id, issue_date, due_date, amount, paid, paid_date)
    invoices.project_id = projects.project_id
    Таблица project_status_history(history_id, project_id, old_status, new_status, changed_by, changed_at)
    project_status_history.project_id = projects.project_id  
    project_status_history.changed_by = analysts.analyst_id
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
