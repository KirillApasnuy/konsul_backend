from clients.deepseek_client import DeepseekClient
from clients.gemini_client import GeminiClient
from settings import Settings

query =  "Исследуй практику применения статьи 333 Гражданского кодекса РФ (уменьшение размера неустойки) в арбитражных судах по спорам о взыскании задолженности по договорам оказания услуг. Какие критерии суды используют для определения соразмерности неустойки последствиям нарушения обязательства? Какие доказательства должен представить ответчик для обоснования необходимости снижения неустойки?   "
# client = DeepseekClient(api_key=Settings.DEEPSEEK_API_KEY, model=Settings.DEEPSEEK_MODEL, base_url=Settings.DEEPSEEK_BASE_URL)

client = GeminiClient(api_key=Settings.GEMINI_API_KEY, model="gemini-2.5-flash-lite")

res = client.rewrite(query)
print(res)