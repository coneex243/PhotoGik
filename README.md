# PhotoGik - примитивный osint инструмент для поиска по фотографиям

Telegram-бот для распознавания лиц и поиска похожих знаменитостей на фото с помощью API биометрического анализа **Betaface API**.

## 🔍 Как это работает

1. Пользователь отправляет в чат фотографию лица.
2. Бот загружает изображение в максимальном разрешении.
3. Отправляет запрос к сервису **Betaface API** (`/api/v2/media`) с параметрами распознавания:
   - Детекция всех лиц на фото (`detect_all=true`).
   - Сравнение с публичной базой данных знаменитостей и персоналий Википедии (`recognize=all@celebrities.betaface.com`).
4. Betaface выполняет поиск биометрических соответствий и возвращает список найденных персон (`person_id`) с коэффициентом уверенности (`confidence`).
5. Бот отправляет пользователю список совпадений с оценкой сходства.

## 🛠 Требования и стек

- **Python 3.10+**
- `python-telegram-bot` (v20+) — асинхронная библиотека для работы с Telegram Bot API.
- `requests` — отправка HTTP-запросов к Betaface API.
- `Pillow` (PIL) — обработка и временное сохранение изображений.
- `python-dotenv` — безопасное хранение ключей в переменных окружения.

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/coneex243/photogik.git
cd photogik
```

### 2. Установка зависимостей
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Конфигурация
Скопируйте пример файла конфигурации:
```bash
cp .env.example .env
```
Заполните параметры в `.env`:
- `TELEGRAM_TOKEN`: токен вашего бота от `@BotFather`.
- `BETAFACE_API_KEY`: API ключ от сервиса [Betaface](https://www.betafaceapi.com/).

### 4. Запуск бота
```bash
python photo.py
```
