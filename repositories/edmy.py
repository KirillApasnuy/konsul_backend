import requests

from settings import Settings


class EdmyRepository:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def ask(self, messages):
        response = requests.post(
            url=self.settings.EDMY_FLASK_URL + "/ask" ,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.EDMY_FLASK_API_KEY}"
            },
            json={
                "assistant_id": "asst_oko465JaABtS9CKnJ8LSMx3E",
                "messages": messages
            }
        )

        return response.text