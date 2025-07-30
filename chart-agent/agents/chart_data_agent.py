import requests, json, os
from dotenv import load_dotenv
from utils.str_cleaner import clean_str

load_dotenv()

yandex_api=os.environ.get("YANDEX_API_KEY")

class ChartDataAgent:
    def __init__(self, temperature=0.2, max_tokens=1000):
        self.temperature = temperature
        self.max_tokens = max_tokens


    def generate_chart_data(self, user_prompt: str, sql_results: list, chart_type: str) -> list:
        data_json = json.dumps(sql_results, ensure_ascii=False, default=str)
        prompt_messages = [
            {
                "role":"system",
                "text":(
                    "Отвечай в JSON-формате, подходящем для Recharts (список объектов со свойствами 'name' и 'value'). "
                    "Данные подходят для типа графика, указанного в сообщении пользователя."
                    "Не добавляй никаких комментариев или текста, только JSON."
                )
            },
            {
                "role":"user",
                "text":(
                    f"Тип графика: {chart_type}\n"
                    f"Запрос: {user_prompt}\n"
                    f"Данные SQL:\n{data_json}"
                )
            }
        ]
        payload = {
            "modelUri": os.environ.get("YANDEX_GPT_MODEL_URI"),
            "completionOptions": {
                "stream":False,
                "temperature":self.temperature,
                "maxTokens":self.max_tokens},
            "messages": prompt_messages
        }
        headers = {
            "Content-Type":"application/json",
            "Authorization": f"Api-Key {yandex_api}"
        }
        response = requests.post(os.environ.get("YANDEX_GPT_URL"), headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()["result"]["alternatives"][0]["message"]["text"].strip()
        clean_data = clean_str(data)
        return json.loads(clean_data)
