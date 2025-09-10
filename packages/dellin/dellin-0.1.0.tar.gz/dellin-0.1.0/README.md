# dellin

Python‑клиент для Dellin API (заказы). Минимальный, типизированный каркас на базе `requests`.

## Установка
- Из исходников (для разработки):
  - `python -m venv .venv && .\.venv\Scripts\activate`
  - `pip install -e .[dev]`

## Быстрый старт
```python
from dellin.api import DellinOrdersClient

client = DellinOrdersClient(appkey="YOUR_APPKEY")
session_id = client.login(login="user", password="pass")
orders = client.list_orders(receiver_inn="7700000000")
print(len(orders))
```

Пример запуска: `python examples/basic.py`

## Команды разработки
- Тесты: `pytest`
- Линт/формат/типы: `ruff check .` | `black .` | `mypy src`
- Сборка пакета: `python -m build` (артефакты в `dist/`)

## Структура
- `src/dellin/` — код пакета (`api.py`, `__init__.py`, `py.typed`)
- `tests/` — базовые тесты `pytest`
- `examples/` — примеры использования

## Лицензия
MIT — см. файл `LICENSE`.
