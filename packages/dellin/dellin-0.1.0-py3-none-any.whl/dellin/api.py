import requests
from typing import Any, Dict, Optional, Union
from datetime import date, datetime


class DellinAPIError(Exception):
    pass


def _date_str(d: Union[str, date, datetime, None]) -> Optional[str]:
    if d is None:
        return None
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m-%d")
    # если уже строка — вернём как есть
    return str(d)


class DellinOrdersClient:
    def __init__(
        self,
        appkey: str,
        *,
        base_url: str = "https://api.dellin.ru",
        login_path: str = "/v3/auth/login.json",
        orders_path: str = "/v3/orders.json",
        timeout: float = 30.0,
    ) -> None:
        self.appkey = appkey
        self.base_url = base_url.rstrip("/")
        self.login_path = login_path
        self.orders_path = orders_path
        self.timeout = timeout
        self.session = requests.Session()
        self.session_id: Optional[str] = None

    # --- Авторизация ---
    def login(self, login: str, password: str) -> str:
        url = f"{self.base_url}{self.login_path}"
        resp = self.session.post(
            url,
            json={"appkey": self.appkey, "login": login, "password": password},
            timeout=self.timeout,
        )
        if resp.status_code == 401:
            raise DellinAPIError("Unauthorized: проверьте appkey/логин/пароль")
        if not resp.ok:
            raise DellinAPIError(f"Login failed: HTTP {resp.status_code} {resp.text}")

        data = resp.json()
        sid = (
            data.get("sessionID")
            or data.get("sessionId")
            or data.get("session_id")
            or (data.get("data") or {}).get("sessionID")
        )
        if not sid:
            raise DellinAPIError(f"Не найден sessionID в ответе: {data}")
        self.session_id = str(sid)
        return self.session_id

    # --- Список заказов ---
    def list_orders(
        self,
        *,
        receiver: Optional[str] = None,  # <-- всегда строка!
        receiver_inn: Optional[str] = None,  # <-- отдельное поле
        date_from: Optional[Union[str, date, datetime]] = None,
        date_to: Optional[Union[str, date, datetime]] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.session_id:
            raise DellinAPIError("Требуется login(): sessionID отсутствует")

        url = f"{self.base_url}{self.orders_path}"
        payload: Dict[str, Any] = {"appkey": self.appkey, "sessionID": self.session_id}

        # --- фильтры ---
        if receiver is not None:
            if isinstance(receiver, dict):
                raise DellinAPIError("receiver должен быть строкой (а не объектом)")
            payload["receiver"] = str(receiver)

        # ИНН передаём отдельным ключом (под вашу схему; если нужен другой — передайте через extra)
        if receiver_inn:
            # Популярные варианты на бекенде встречаются разные — поддержим оба.
            payload["receiverInn"] = receiver_inn
            payload["receiver_inn"] = (
                receiver_inn  # не помешает, бэк обычно игнорит лишнее
            )

        if date_from or date_to:
            payload["date"] = {}
            df = _date_str(date_from)
            dt = _date_str(date_to)
            if df:
                payload["date"]["from"] = df
            if dt:
                payload["date"]["to"] = dt

        if page is not None:
            payload["page"] = page
        if page_size is not None:
            payload["page_size"] = page_size

        if extra:
            # extra перекрывает мои значения (если нужно тонко подогнать схему под ваш метод)
            payload.update(extra)

        resp = self.session.post(url, json=payload, timeout=self.timeout)
        if resp.status_code == 401:
            raise DellinAPIError(
                "Unauthorized: просрочен/неверен sessionID (перелогиньтесь)"
            )
        if not resp.ok:
            raise DellinAPIError(f"Orders failed: HTTP {resp.status_code} {resp.text}")

        data = resp.json()
        if isinstance(data, dict) and data.get("errors"):
            raise DellinAPIError(f"API errors: {data['errors']}")
        return data
