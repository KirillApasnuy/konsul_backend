import functools
import time
from typing import List

from settings import Settings


def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        print(f"[{func.__name__}] Выполнено за {duration:.4f} сек.")
        return result
    return wrapper

def build_analyze_prompt(query: str, documents: List[str]) -> str:
    context = "\n\n---\n\n".join(documents)
    return f"""
    {Settings.ANALYZE_LEGAL_PROMPT}

    **Запрос:** {query}

    **Судебная практика:** 
    {context}
    """.strip()