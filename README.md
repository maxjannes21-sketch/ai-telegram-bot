# 🤖 AI Telegram Bot с памятью

Telegram-бот на Python с интеграцией GPT-4o-mini и долговременной памятью 
диалогов в PostgreSQL. Бот помнит контекст переписки с каждым пользователем 
и отвечает с его учётом.

## Возможности

- 💬 Ответы через LLM (GPT-4o-mini через OpenRouter API)
- 🧠 Память диалога: бот помнит предыдущие сообщения (последние 10)
- 👥 Автоматическая регистрация пользователей (дедупликация по telegram_id)
- 💾 Полная история переписки в PostgreSQL
- 📱 Telegram Mini App (веб-приложение внутри Telegram)
- 🔒 Секреты вынесены в переменные окружения (.env)
- 🌐 REST API на FastAPI со Swagger-документацией (/docs)
- 📊 Веб-дашборд статистики (stats.html → API → PostgreSQL)

## Стек

| Компонент | Технология |
|---|---|
| Язык | Python 3.14 |
| Telegram API | python-telegram-bot |
| LLM | OpenRouter API (GPT-4o-mini) |
| База данных | PostgreSQL 18 |
| Mini App | HTML / CSS / JavaScript |
| Хостинг Mini App | GitHub Pages |
| RAG | sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| API | FastAPI + Uvicorn |

## Структура проекта
my_bot/
├── bot.py                # Логика бота, обработчики команд
├── db.py                 # Работа с PostgreSQL (пользователи, сообщения, история)
├── rag.py                # RAG: векторный поиск по базе знаний
├── api.py                # REST API на FastAPI
├── load_knowledge.py     # Загрузка knowledge.txt → PostgreSQL (черновые эмбеддинги)
├── migrate_knowledge.py  # Создание таблицы knowledge_chunks
├── check_db.py           # Утилита для просмотра содержимого базы
├── stats.html            # Веб-дашборд статистики
├── mini_app.html         # Mini App: интерфейс внутри Telegram
├── knowledge.txt         # Исходник базы знаний (чанки через пустую строку)
├── .env                  # Секреты (не в репозитории)
└── .env.example          # Шаблон для .env

## Схема базы данных

**users** — пользователи бота
| Поле | Тип | Описание |
|---|---|---|
| id | SERIAL PK | Внутренний ID |
| telegram_id | BIGINT UNIQUE | ID в Telegram (дедупликация) |
| username | VARCHAR(100) | Имя пользователя |
| created_at | TIMESTAMP | Дата первого сообщения |

**messages** — история сообщений
| Поле | Тип | Описание |
|---|---|---|
| id | SERIAL PK | ID сообщения |
| user_id | INTEGER → users(id) | Связь с пользователем (FK) |
| message_text | TEXT | Сообщение пользователя |
| bot_reply | TEXT | Ответ бота |
| created_at | TIMESTAMP | Время сообщения |

## Как работает память

1. Пользователь пишет сообщение
2. Бот находит/создаёт пользователя в `users` (INSERT ... ON CONFLICT)
3. Из `messages` загружаются последние 10 сообщений диалога
4. История + новое сообщение отправляются в GPT-4o-mini
5. Ответ и сообщение сохраняются в `messages`

## Установка и запуск

```bash
pip install -r requirements.txt

# Заполнить .env по шаблону .env.example
python bot.py
```

## Планы по развитию

- [x] REST API на FastAPI поверх базы
- [x] RAG: ответы по базе знаний (эмбеддинги в PostgreSQL, JSONB + numpy)
- [x] Команда /stats — статистика из БД
- [ ] Деплой в Docker на VPS