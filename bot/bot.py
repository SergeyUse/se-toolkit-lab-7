#!/usr/bin/env python3
"""Telegram bot entry point for SE Toolkit Lab 7.

Supports two modes:
1. Test mode: `bot.py --test "/command"` - prints response to stdout
2. Telegram mode: `bot.py` - runs the Telegram bot

Features:
- Slash commands: /start, /help, /health, /labs, /scores
- Natural language queries with LLM-based intent routing
- Inline keyboard buttons for common actions
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_general_query,
    set_lms_client,
    set_llm_client,
)
from services import LMSClient, LLMClient
from router import IntentRouter, set_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_test_mode(query: str) -> None:
    """Run the bot in test mode.

    Calls handlers directly without Telegram connection.
    Prints response to stdout and exits with code 0.

    Args:
        query: The command or query to test (e.g., "/start", "/help").
    """
    config = load_config()

    # Initialize clients for test mode
    lms_client = LMSClient(config["lms_api_url"], config["lms_api_key"])
    llm_client = LLMClient(
        config["llm_api_base_url"],
        config["llm_api_key"],
        config["llm_api_model"],
    )
    
    set_lms_client(lms_client)
    set_llm_client(llm_client)

    try:
        # Parse the query
        query = query.strip()

        if query.startswith("/"):
            parts = query[1:].split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None

            # Route to appropriate handler
            if command == "start":
                response = await handle_start(args)
            elif command == "help":
                response = await handle_help(args)
            elif command == "health":
                response = await handle_health(args)
            elif command == "labs":
                response = await handle_labs(args)
            elif command == "scores":
                response = await handle_scores(args)
            else:
                response = f"⚠️ Unknown command: /{command}\nUse /help to see available commands."
        else:
            # General query - use intent router
            response = await handle_general_query(query)

        # Print response to stdout
        print(response)

    finally:
        await lms_client.close()
        await llm_client.close()


def get_inline_keyboard() -> list:
    """Get inline keyboard buttons for common actions.
    
    Returns:
        List of keyboard rows with inline buttons.
    """
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Available Labs", callback_data="labs"),
                InlineKeyboardButton("🏥 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton("📊 Scores Lab 4", callback_data="scores_lab-04"),
                InlineKeyboardButton("🏆 Top Students", callback_data="top_lab-04"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    except ImportError:
        return []


def run_telegram_mode() -> None:
    """Run the bot in Telegram mode.

    Connects to Telegram and handles real user messages.
    """
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    except ImportError as e:
        logger.error(f"python-telegram-bot not installed. Run: uv sync. Error: {e}")
        sys.exit(1)

    config = load_config()

    if not config["bot_token"]:
        logger.error("BOT_TOKEN not found in .env.bot.secret")
        sys.exit(1)

    # Create application
    app = Application.builder().token(config["bot_token"]).build()

    # Initialize services
    lms_client = LMSClient(config["lms_api_url"], config["lms_api_key"])
    llm_client = LLMClient(
        config["llm_api_base_url"],
        config["llm_api_key"],
        config["llm_api_model"],
    )

    # Set clients for handlers
    set_lms_client(lms_client)
    set_llm_client(llm_client)

    # Command handlers
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await handle_start()
        # Send with inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("📚 Available Labs", callback_data="labs"),
                InlineKeyboardButton("🏥 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton("📊 Scores Lab 4", callback_data="scores_lab-04"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await handle_help()
        await update.message.reply_text(response)

    async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await handle_health()
        await update.message.reply_text(response)

    async def cmd_labs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = await handle_labs()
        await update.message.reply_text(response)

    async def cmd_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = " ".join(context.args) if context.args else None
        response = await handle_scores(args)
        await update.message.reply_text(response)

    # Callback query handler for inline buttons
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "labs":
            response = await handle_labs()
        elif data == "health":
            response = await handle_health()
        elif data == "help":
            response = await handle_help()
        elif data.startswith("scores_"):
            lab_id = data.replace("scores_", "")
            response = await handle_scores(lab_id)
        elif data.startswith("top_"):
            lab_id = data.replace("top_", "")
            # Use intent router for top learners query
            response = await handle_general_query(f"top 5 students in {lab_id}")
        else:
            response = "Unknown action."
        
        await query.edit_message_text(response)

    # Message handler for general queries
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.message.text
        response = await handle_general_query(query)
        await update.message.reply_text(response)

    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CommandHandler("labs", cmd_labs))
    app.add_handler(CommandHandler("scores", cmd_scores))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    logger.info("Starting Telegram bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SE Toolkit Lab 7 Telegram Bot"
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="QUERY",
        help="Run in test mode with the specified query (e.g., '/start')",
    )

    args = parser.parse_args()

    if args.test:
        # Test mode - no Telegram connection needed
        asyncio.run(run_test_mode(args.test))
    else:
        # Telegram mode - run_polling manages its own event loop
        run_telegram_mode()


if __name__ == "__main__":
    main()
