import os
import io
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from PIL import Image
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены и API ключи (рекомендуется задавать через .env)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
BETAFACE_API_KEY = os.getenv('BETAFACE_API_KEY', 'YOUR_BETAFACE_API_KEY_HERE')
BETAFACE_URL = os.getenv('BETAFACE_URL', 'https://www.betafaceapi.com/api/v2/media')
BETAFACE_NAMESPACE = os.getenv('BETAFACE_NAMESPACE', 'all@celebrities.betaface.com')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '👋 Привет! Отправь мне фото лица, и я найду совпадения через Betaface API (публичные базы знаменитостей и Википедии).'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img_path = None
    try:
        # Получаем фотографию в максимальном доступном разрешении
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()

        # Сохраняем временное изображение
        image = Image.open(io.BytesIO(photo_bytes))
        img_path = f'temp_{update.message.from_user.id}.jpg'
        image.save(img_path)

        # Параметры запроса к сервису распознавания Betaface
        params = {
            'api_key': BETAFACE_API_KEY,
            'detect_all': 'true',  # Детекция всех лиц и биометрических точек
            'recognize': BETAFACE_NAMESPACE  # Проверка по базе
        }
        
        # Отправляем файл безопасным способом через контекстный менеджер
        with open(img_path, 'rb') as f:
            response = requests.post(BETAFACE_URL, params=params, files={'file': f})

        # Логируем ответ
        logger.info(f"Betaface status: {response.status_code}")

        # Обработка ответа
        if response.status_code == 200:
            data = response.json()
            faces = data.get('faces', [])
            if faces:
                reply_text = "🔍 Совпадения Betaface:\n\n"
                for i, face in enumerate(faces[:3], 1):  # До 3 лиц
                    matches = face.get('matches', [])
                    if matches:
                        reply_text += f"Лицо #{i}:\n"
                        for match in matches:
                            label = match.get('person_id', 'Неизвестно')
                            score = match.get('confidence', 'N/A')
                            reply_text += f"• {label} (уверенность: {score})\n"
                    else:
                        reply_text += f"Лицо #{i}: найдено, но точных совпадений в базе нет.\n"
            else:
                reply_text = "❌ На фотографии лица не обнаружены."
        else:
            reply_text = f"⚠️ Ошибка сервиса Betaface (код {response.status_code})."

        # Отправляем ответ пользователю
        await update.message.reply_text(reply_text[:4096])

    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {str(e)}")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}. Попробуйте ещё раз.")
    finally:
        # Корректное удаление временного файла
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                pass

def main():
    if TELEGRAM_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
        logger.warning("ВНИМАНИЕ: Задайте TELEGRAM_TOKEN в файле .env перед запуском бота!")

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()

if __name__ == '__main__':
    main()
