import time
from datetime import datetime
from typing import List, Generator

from google.genai import Client

from settings import Settings
from utils.utils import build_analyze_prompt


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.client = Client(api_key=api_key)
        self.model = model

    def analyze(self, query: str, documents: List[str]) -> str:
        """
        Выполняет анализ судебной практики через Gemini
        """
        prompt = build_analyze_prompt(query, documents)

        response = self.client.models.generate_content(model=self.model, contents=prompt, )
        return response.text

    def analyze_stream(self, query: str, documents: List[str]) -> Generator[str, None, None]:
        """
        Выполняет анализ судебной практики через Gemini, ответ stream
        """
        prompt = build_analyze_prompt(query, documents)

        try:
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text
                    time.sleep(0.1)

        except Exception as e:
            # Можно залогировать или пробросить
            yield f"\n[Ошибка анализа]: {str(e)}"

    def rewrite_to_legal_query(self, query: str) -> str:
        prompt = f"""
             {Settings.REWRITE_LEGAL_PROMPT}

            **Запрос:** {query}

        """

        response = self.client.models.generate_content(model=Settings.GEMINI_MODEL_LITE, contents=prompt)
        return response.text
