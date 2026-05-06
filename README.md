# КР №4 — Технологии разработки серверных приложений


Главная цель здесь показать работу с API, обработкой ошибок, валидацией данных, миграциями базы данных и тестированием.


## Установка и запуск проекта

Склонируйте репозиторий:

```bash
git clone https://github.com/Plovika/kr4_TRSP.git
cd kr4_TRSP
```

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его:

### для Windows

```bash
.venv\Scripts\activate
```

###  для mac

```bash
source .venv/bin/activate
```


### Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Запуск FastAPI приложения

```bash
uvicorn main:app --reload
```

После запуска документация будет доступна по адресам:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Проверка тестов

Запуск всех тестов:

```bash
pytest
```

Запуск тестов с подробным выводом:

```bash
pytest -v
```

---

## Проверка миграций Alembic

Создание новой миграции:

```bash
alembic revision --autogenerate -m "migration_name"
```

Применение миграций:

```bash
alembic upgrade head
```
