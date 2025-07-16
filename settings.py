class Settings():
    def __init__(self):
        self.MONGO_URI = "mongodb://localhost:27017"
        self.MONGO_DB = "konsul-db"
        self.MONGO_DB_SS = "konsul_es"
        self.MONGO_COLLECTION = "konsul"
        self.ES_HOST = "http://localhost:9200"
        self.ES_INDEX = "documents"
        self.ES_INDEX_SS = "konsul_cases"
        self.DEEPSEEK_URL = "https://api.deepseek.com"
        self.EDMY_FLASK_URL = "http://147.45.135.236:8443"
        self.EDMY_FLASK_API_KEY = "aWxvdmVzdXp1a2k="
