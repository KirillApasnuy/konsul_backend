class Settings:
    ES_HOST = "http://elasticsearch:9200"
    ES_INDEX = "court_decisions"
    GEMINI_API_KEY = "AIzaSyC-rOs5RxAWrmZFYpkBjbon5qYdCqto-cc"
    GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_MODEL_LITE = "gemini-2.5-flash-lite"


    DEEPSEEK_API_KEY = "sk-b283e233f9304d06bdc08707c03a89cf"
    DEEPSEEK_MODEL = "deepseek-chat"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    REWRITE_LEGAL_PROMPT = ("Ты юридический помощник. "
                            "Преобразуй запрос пользователя в краткий юридический запрос на русском языке. "
                            "Используй юридически точные формулировки."
                            "ТОЛЬКО ЭТО, БОЛЬШЕ НИЧЕГО НЕ НАДО")
    prm = {
  "prompt": "You are an experienced lawyer. "
            "Analyze the case law on a given legal topic. "
            "Prioritize the case law of the Supreme Court of the Russian Federation, "
            "then selected appellate courts for the most suitable case, "
            "and finally courts of first instance, viewing them as a single chain "
            "in proving the decisions of courts of various instances.\n\n### "
            "Key Documents and Evidence:\n* List the types of documents used by the "
            "parties to support their claims or objections, with references from the"
            " parties to these documents.\n\n### Legally Significant Circumstances to be"
            " Proved in the Dispute:\n* Indicate the circumstances and the causal link between t"
            "hem that are used when rendering a decision to satisfy or deny claims on the give"
            "n topic.\n\n### Examples from Case Practice:\n* Provide examples of court decisions"
            " in similar cases, highlighting the case law of the Supreme Court of the Russian Federa"
            "tion with all stages of the cases, then selected appellate courts for the most suitable cases, and finally courts of first instance. "
            "Be sure to add links to documents"
}
    ANALYZE_LEGAL_PROMPT = str(prm)
