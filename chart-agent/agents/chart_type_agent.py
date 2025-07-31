import requests, json, os
from dotenv import load_dotenv
from utils.str_cleaner import clean_str

load_dotenv()

yandex_api=os.environ.get("YANDEX_API_KEY")

class ChartTypeAgent:
    def __init__(self, temperature=0.2, max_tokens=1500):
        self.temperature = temperature
        self.max_tokens = max_tokens

    def suggest_chart_types(self, user_prompt: str, sql_results: list) -> list:
        data_json = json.dumps(sql_results, ensure_ascii=False, default=str)
        prompt_messages = [
            {
                "role": "system",
                "text": (
                    "На основе запроса и данных (список JSON объектов) выбери типы графикоа из: "
                    "['barchart','linechart','piechart','areachart','scatterchart']. "
                    "Верни JSON-массив строк без объяснений."
                )
            },
            {
                "role": "user",
                "text": (
                    f"Запрос:\n{user_prompt}\n"
                    f"Данные:\n{data_json}\n"
                )
            }
        ]
        payload = {
            "modelUri": os.environ.get("YANDEX_GPT_MODEL_URI"),
            "completionOptions": {
                "stream": False,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens
            },
            "messages": prompt_messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {yandex_api}"
        }
        response = requests.post(os.environ.get("YANDEX_GPT_URL"), headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()["result"]["alternatives"][0]["message"]["text"].strip()
        clean_data = clean_str(data)
        start = clean_data.find("[")
        if start == -1:
            return []
        depth = 0
        for i, ch in enumerate(clean_data[start:], start):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    json_text = clean_data[start: i + 1]
                    break
        else:
            return []
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            return []