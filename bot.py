#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram bot for 5-letter Russian word search.
Parses messages directly without requiring commands (except /start and /help).

Uses webhook mode for Render.com deployment.
"""

import logging
import os

from aiohttp import web
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from core import (
    load_lexicon,
    get_search_params,
    filter_words,
    sort_by_frequency,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

# Load lexicon once at startup (global)
logger.info("Loading lexicon...")
try:
    WORDS, FREQ_MAP = load_lexicon('data/lexicon_ru_5.jsonl.gz')
    logger.info(f"Loaded {len(WORDS)} words")
except Exception as e:
    logger.error(f"Failed to load lexicon: {e}")
    exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued."""
    welcome_text = """
👋 Привет! Я бот для поиска 5-буквенных русских слов (Wordle helper).

📝 *Синтаксис:*
  `-абв`  — серые буквы (исключить)
  `+где`  — жёлтые буквы (обязательные)
  `_а___` — паттерн (зелёные, 5 символов с `_`)
  `1а5б`  — антипаттерн (позиция + запрещённые буквы)

💡 *Примеры:*
  `-нзф +ки _а___ 2к`
  `+ки -нзф 2к _а___`  (порядок не важен)
  `-абв +где`  (без паттерна)

Просто отправь мне сообщение с параметрами поиска!

Используй /help для справки.
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when /help is issued."""
    help_text = """
📖 *Справка по использованию*

*Синтаксис поиска:*
  `-абв`  — серые буквы (не должны быть в слове)
  `+где`  — жёлтые буквы (обязательно есть в слове)
  `_а___` — паттерн из 5 символов (`_` = любая буква)
  `1а5б`  — антипаттерн (позиция + запрещённые там буквы)

*Примеры запросов:*

1. Найти слова с буквами "к" и "и", без "н", "з", "ф":
   `+ки -нзф`

2. Найти слова, где 1-я буква "а", есть "к" и "и":
   `_а___ +ки -нзф`

3. Найти слова с "к" и "и", где на позиции 2 не может быть "к":
   `+ки -нзф 2к`

4. Полный пример:
   `-нзф +ки _а___ 2к`

*Замечания:*
- Порядок параметров не важен
- Буква "ё" заменяется на "е"
- Результаты сортируются по частоте использования

Просто отправь сообщение с параметрами!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def search_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse message text and return matching words."""
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("Пустой запрос. Используй /help для справки.")
        return

    # Parse search parameters
    params = get_search_params(text)

    # Check for conflicts
    if params['conflicts']:
        conflict_msg = "❌ *Конфликты в параметрах:*\n\n"
        for msg in params['conflicts']:
            conflict_msg += f"• {msg}\n"
        conflict_msg += "\nПроверь параметры и попробуй снова."
        await update.message.reply_text(conflict_msg, parse_mode='Markdown')
        return

    # Filter words
    filtered_words, fstats = filter_words(
        WORDS,
        params['must_have'],
        params['excluded'],
        params['pattern'],
        params['antipattern_constraints']
    )

    # Sort by frequency
    if FREQ_MAP:
        filtered_words = sort_by_frequency(filtered_words, FREQ_MAP)

    # Format response
    total = len(filtered_words)

    if total == 0:
        response = "😕 *Слова не найдены*\n\n"
        response += "*Параметры поиска:*\n"
        if params['excluded']:
            response += f"  Серые: `{''.join(sorted(params['excluded']))}`\n"
        if params['must_have']:
            response += f"  Жёлтые: `{''.join(sorted(params['must_have']))}`\n"
        if params['pattern']:
            response += f"  Паттерн: `{params['pattern']}`\n"
        if params['raw_antipattern']:
            response += f"  Антипаттерн: `{params['raw_antipattern']}`\n"
        await update.message.reply_text(response, parse_mode='Markdown')
        return

    # Limit output to 50 words
    max_words = 50
    display_words = filtered_words[:max_words]

    response = f"✅ *Найдено: {total} {'слово' if total == 1 else 'слов' if total < 5 else 'слов'}*\n\n"

    for i, word in enumerate(display_words, 1):
        response += f"{i}. `{word}`\n"

    if total > max_words:
        response += f"\n_...и ещё {total - max_words} слов_\n"

    response += "\n*Параметры:*\n"
    if params['excluded']:
        response += f"  Серые: `{''.join(sorted(params['excluded']))}`\n"
    if params['must_have']:
        response += f"  Жёлтые: `{''.join(sorted(params['must_have']))}`\n"
    if params['pattern']:
        response += f"  Паттерн: `{params['pattern']}`\n"
    if params['raw_antipattern']:
        response += f"  Антипаттерн: `{params['raw_antipattern']}`\n"

    await update.message.reply_text(response, parse_mode='Markdown')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


async def health(request):
    """Health check endpoint for Render.com."""
    return web.Response(text="OK")


async def webhook(request):
    """Handle incoming Telegram updates."""
    application = request.app['bot_app']
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return web.Response()


async def on_startup(app):
    """Initialize bot on startup."""
    application = app['bot_app']
    await application.initialize()
    await application.start()

    webhook_url = app['webhook_url']
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")


async def on_shutdown(app):
    """Cleanup on shutdown."""
    application = app['bot_app']
    await application.stop()
    await application.shutdown()


def main():
    """Start the bot."""
    logger.info("Starting 5Letters bot...")

    # Get configuration from environment
    port = int(os.getenv('PORT', 10000))
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')  # Auto-provided by Render.com

    if not webhook_url:
        logger.error("RENDER_EXTERNAL_URL not set! Are you running on Render.com?")
        exit(1)

    # Create PTB application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_words))
    application.add_error_handler(error_handler)

    # Create aiohttp web app
    app = web.Application()
    app['bot_app'] = application
    app['webhook_url'] = webhook_url

    # Routes
    app.router.add_get('/health', health)
    app.router.add_post('/', webhook)

    # Lifecycle
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Start server
    logger.info(f"Bot starting with webhook at {webhook_url}")
    web.run_app(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
