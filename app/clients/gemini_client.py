from typing import List
from google.genai import Client

from settings import Settings


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.client = Client(api_key=api_key)
        self.model = model
    def analyze(self, query: str, documents: List[str]) -> str:
        """
        Выполняет анализ судебной практики через Gemini
        """
        # Формируем длинный контекст из всех документов
        context = "\n\n---\n\n".join(documents)

        prompt = f"""
             {Settings.SYSTEM_PROMPT}
            
            **Запрос:** {query}
            
            **Судебная практика:** 
            {context}
            
        """

        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text
