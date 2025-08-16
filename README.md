# Temporal Cities Game

Пример workflow на Temporal и Python, который играет с пользователем в игру «Города» через простой веб‑интерфейс.

## Запуск

1. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустить worker:
   ```bash
   python worker.py
   ```
3. Запустить веб-сервер:
   ```bash
   uvicorn web.server:app --reload
   ```

### HTTP‑эндпоинты
- `POST /start` — начать игру.
- `POST /move` — сделать ход, тело: `{ "city": "Москва" }`.
- `POST /give_up` — сдаться.

Состояние игры хранится внутри workflow и сохраняется при перезапусках worker.
