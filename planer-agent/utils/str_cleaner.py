import re

def clean_str(sql_text: str or dict) -> str:
    cleaned = sql_text.replace("```", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", cleaned)