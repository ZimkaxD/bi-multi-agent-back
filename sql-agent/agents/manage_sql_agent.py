import requests, os, re
from agents.generate_sql_agent import GenerateSQLAgent
from agents.execute_sql_agent import ExecuteSQLAgent
from utils.str_cleaner import clean_str
from dotenv import load_dotenv
load_dotenv()
yandex_api=os.environ.get("YANDEX_API_KEY")

class ManageSQLAgent:
    def __init__(self, temperature=0.1, max_tokens=1500):
        self.generator = GenerateSQLAgent(temperature,max_tokens)
        self.executor = ExecuteSQLAgent()

    def ask_llm_to_fix_sql(self, bad_sql: str, error_msg: str, schema: str) -> str:

        prompt_messages = [
            {
                "role": "system",
                "text": (
                    "Мы получили ошибку при выполнении запроса. "
                    "Твоя задача — проанализировать SQL и сообщение об ошибке, после чего исправить SQL-код. "
                    "Отвечай только исправленным SQL-кодом без пояснений."
                )
            },
            {
                "role": "user",
                "text": (
                     f"Исходный SQL:\n{bad_sql}\n"
                     f"Ошибка выполнения:\n{error_msg}\n"
                     f"Описание схемы:\n{schema}"
                )
            }
        ]

        payload = {
            "modelUri": os.environ.get("YANDEX_GPT_MODEL_URI"),
            "completionOptions": {
                "stream": False,
                "temperature": self.generator.temperature,
                "maxTokens": self.generator.max_tokens},
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

    def generate_execute_loop(self, schema: str, user_prompt: str, max_attempts: int = 3)->dict:

        sql_code = self.generator.generate_sql(schema, user_prompt)
        clean_sql = clean_str(sql_code)

        for attempt in range(1, max_attempts + 1):
            result = self.executor.safe_execute(clean_sql)
            if result.get("success"):
                return {"sql": clean_sql, "results": result.get("data")}

            error_message=result.get("error", "Неизвестная ошибка")

            if "missing FROM-clause entry for table" in error_message:
                clean_sql = re.sub(r'\bprojects\.(\w+)', r'\1', clean_sql)
                continue

            fixed_sql=self.ask_llm_to_fix_sql(clean_sql,error_message,schema)
            clean_sql=clean_str(fixed_sql)

        return {"sql": clean_sql, "error": f"Не удалось выполнить запрос после {max_attempts} попыток"}
