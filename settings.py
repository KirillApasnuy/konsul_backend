class Settings():
    def __init__(self):
        self.MONGO_URI = "mongodb://localhost:27017"
        self.MONGO_DB = "konsul-db"
        self.MONGO_COLLECTION = "konsul"
        self.ES_HOST = "http://localhost:9200"
        self.ES_INDEX = "documents"
        self.DEEPSEEK_API_KEY = "sk-2219ca020f024cdca3e02017be2b37c3"
        self.DEEPSEEK_URL = "https://api.deepseek.com"