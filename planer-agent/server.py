from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, requests

load_dotenv()

app = Flask(__name__)

SQL_AGENT=os.getenv("SQL_AGENT_URL")
CHART_AGENT=os.getenv("CHART_AGENT_URL")

YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
YANDEX_GPT_URL = os.environ.get("YANDEX_GPT_URL")
YANDEX_GPT_MODEL_URI = os.environ.get("YANDEX_GPT_MODEL_URI")


def classify_goal(user_prompt: str, temperature=0.3, max_tokens=1500) -> str:
    prompt_messages = [
        {
            "role": "system",
            "text": (
                "Выбери одну метку: ['search','chart','both','insert','other']"
                "Если пользователь просит что-то найти или т.п. - это значит метка - search. "
                "Если пользователь просит что-то связанное с диаграммой, гистограммой или графиком - это метка - chart. "
                "Если пользователь просит и найти информацию, и визуализировать её — метка - both. "
                "Если пользователь просит что-либо добавить — метка - insert. "
                "Не добавляй никаких комментариев — только метка."
            )
        },
        {
            "role": "user",
            "text": f"Запрос пользователя:\n{user_prompt}\n"
        }
    ]

    payload = {
        "modelUri": YANDEX_GPT_MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": prompt_messages
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["result"]["alternatives"][0]["message"]["text"].strip()

    except Exception as e:
        raise e


@app.route("/plan", methods=["POST"])
def plan():
    body = request.get_json() or {}
    schema = body.get("schema", "")
    user_prompt = body.get("user_prompt", "")

    try:
        goal = classify_goal(user_prompt)

        if goal in ["search","insert"]:
            try:
                r = requests.post(f"{SQL_AGENT}/generate_execute", json={"schema": schema, "user_prompt": user_prompt})
                r.raise_for_status()
                sql_response = r.json()
                return jsonify({
                    "goal": goal,
                    "sql": sql_response.get("sql"),
                    "results": sql_response.get("results", []),
                    **({"inserted": True} if goal == "insert" and "error" not in sql_response else {})
                }), 200
            except Exception as e:
                import traceback
                return jsonify({
                    "error": "Ошибка планировщика",
                    "details": traceback.format_exc()
                }), 500

        if goal in ["chart", "both"]:
            try:
                r = requests.post(f"{SQL_AGENT}/generate_execute", json={"schema": schema, "user_prompt": user_prompt})
                r.raise_for_status()
                sql_response = r.json()
            except Exception as e:
                import traceback
                return jsonify({
                    "error": "Ошибка при SQL-запросе",
                    "details": traceback.format_exc()
                }), 500

            if "error" in sql_response:
                return jsonify({"goal": goal, **sql_response})

            results = sql_response["results"]
            try:
                r2 = requests.post(f"{CHART_AGENT}/suggest_types", json={
                    "user_prompt": user_prompt,
                    "results": results
                })
                r2.raise_for_status()
                types = r2.json().get("charts_type", [])
            except Exception as e:
                import traceback
                return jsonify({
                    "error": "Ошибка при выборе типа диаграмм",
                    "details": traceback.format_exc()
                }), 500

            charts_data = {}
            for chart_type in types:
                try:
                    r3 = requests.post(f"{CHART_AGENT}/generate_data", json={
                        "user_prompt": user_prompt,
                        "results": results,
                        "chart_type": chart_type
                    })
                    r3.raise_for_status()
                    charts_data[chart_type] = r3.json().get("chart_data",[])
                except Exception as e:
                    import traceback
                    return jsonify({
                        "error": "Ошибка генерации диаграмм",
                        "details": traceback.format_exc()
                    }), 500

            return jsonify({
                "goal": goal,
                "sql": sql_response["sql"],
                "results": results,
                "charts_type": types,
                "charts_data": charts_data
            })

        return jsonify({"goal": goal, "error": "Не удалось понять цель запроса"})


    except Exception as e:
        return jsonify({

            "error": "Ошибка планировщика",

            "details": str(e)

        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
