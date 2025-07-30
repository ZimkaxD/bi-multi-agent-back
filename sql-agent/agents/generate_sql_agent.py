import requests, os
from dotenv import load_dotenv
load_dotenv()
yandex_api=os.environ.get("YANDEX_API_KEY")

class GenerateSQLAgent:
    def __init__(self, temperature=0.2, max_tokens=1500):
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_sql(self, schema: str, user_prompt: str)->dict:
        prompt_messages = [
            {
                "role": "system",
                "text": (
                         "Твоя задача — по описанию структуры данных (schema) и запроса пользователя (user_prompt) сгенерировать корректный SQL-запрос для PostgreSQL используя его синтаксис. "
                         "Отвечай только SQL-кодом без пояснений."
                )
            },
            {
                "role": "user",
                "text": (
                    f"У меня есть таблица со следующей схемой : {schema}. Напиши такой SQL-запрос:"
                    f"Запрос пользователя:\n{user_prompt}\n\n"
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

        data = response.json()
        return data["result"]["alternatives"][0]["message"]["text"].strip()