import requests

from settings import Settings


class EdmyFlaskRepo:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def ask(self, messages):
        response = requests.post(
            url=self.settings.EDMY_FLASK_URL + "/ask" ,
            headers={
                "Authorization": f"Bearer {self.settings.EDMY_FLASK_API_KEY}"
            }
        )