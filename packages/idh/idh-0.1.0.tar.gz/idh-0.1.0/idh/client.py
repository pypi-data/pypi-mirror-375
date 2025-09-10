import requests
from .types import Token


class IDHError(Exception):
    """Базовое исключение для IDH"""


class UnauthorizedToken(IDHError):
    """Токен недействителен"""


class IDHClient:
    def __init__(self, token: Token, base_url: str = "https://api-idh.mainplay-tg.ru/api"):
        self.token = token
        self.base_url = base_url.rstrip("/")

    def request(self, endpoint: str, phone: str) -> dict:
        """
        Отправить один запрос к API.

        :param endpoint: то, что идёт после /api/
        :param phone: номер телефона в виде строки
        :return: dict/list — JSON ответ от сервера
        """
        params = {
            "token": str(self.token),
            "phone": phone
        }

        url = f"{self.base_url}/{endpoint}"

        # ОДИН запрос
        resp = requests.get(url, params=params)

        if resp.status_code == 401 or resp.text.strip() == "UNAUTH_TOKEN":
            raise UnauthorizedToken("Токен недействителен")

        try:
            return resp.json()
        except Exception:
            raise IDHError(f"Не удалось распарсить ответ: {resp.text}")
