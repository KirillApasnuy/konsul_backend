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
        "prompt": "You are an experienced lawyer. Analyze the case law on a given legal topic and prepare a legal memorandum with the following parameters:\n\n### 1. Key Documents and Evidence:\n* List the types of documents that parties use to support their claims or objections.\n* Specify how parties refer to these documents during litigation.\n* Add links to relevant legal acts or court documents where these types of evidence are mentioned.\n\n### 2. Legally Significant Circumstances:\n* Identify and describe the circumstances that courts consider crucial for making a decision.\n* Establish and explain the causal link between these circumstances and the case's outcome (satisfaction or denial of the claim).\n* Provide links to court decisions that confirm the importance of these circumstances.\n\n### 3. Examples from Case Law:\n* Provide specific examples of court decisions in similar cases.\n* Structure the examples by priority:\n    * Supreme Court of the Russian Federation: Describe the case in detail, covering all its stages (first instance, appeal, cassation, supervision), and indicate how the courts' positions changed.\n    * Appellate Courts: Select and describe the most relevant cases.\n    * Courts of First Instance: Provide examples that illustrate the practical application of the rules.\n* For each example, provide separate links to court decisions:\n    * Links to satisfied claims: where the claims were granted.\n    * Links to denied claims: where the claims were rejected."
    }
    ANALYZE_LEGAL_PROMPT = str(prm)
