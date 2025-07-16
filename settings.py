class Settings():
    def __init__(self):
        self.MONGO_URI = "mongodb://mongo:27017"
        self.MONGO_DB = "konsul-db"
        self.MONGO_DB_SS = "konsul_es"
        self.MONGO_COLLECTION = "konsul"
        self.ES_HOST = "http://elasticsearch:9200"
        self.ES_INDEX = "documents"
        self.ES_INDEX_SS = "konsul_cases"
        self.DEEPSEEK_API_KEY = "sk-2219ca020f024cdca3e02017be2b37c3"
        self.DEEPSEEK_URL = "https://api.deepseek.com"
        self.OPENAI_API_KEY = "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"
        self.EDMY_FLASK_URL = "http://147.45.135.236:8443"
        self.EDMY_FLASK_API_KEY = "aWxvdmVzdXp1a2k="
