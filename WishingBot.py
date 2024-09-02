import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

birthdays = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "Hey, welcome to the Birthday Wishing Bot! 🎉\n\n"
        "This bot allows you to wish your close ones without needing to remember or stay up! 😄\n\n"
        "Here's what you need to do to set a birthday wish:\n"
        "1. Use the /setbirthday command.\n"
        "2. Format: /setbirthday <DD-MM-YYYY> <User's Telegram ID> <Your Message>.\n\n"
        "Example: /setbirthday 25-12-2024 1234567890 Happy Birthday! 🎂\n"
        "The bot will automatically send your message at midnight on their birthday!"
    )
    await update.message.reply_text(welcome_message)


async def set_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /setbirthday <DD-MM-YYYY> <User's Telegram ID> <Message>")
            return
        
        date_str, user_id, message = args
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        
        birthdays[user_id] = {'date': date, 'message': message}
        
        await update.message.reply_text(f"Birthday set for user {user_id} on {date_str}.")
    except ValueError:
        await update.message.reply_text("Invalid date format. Use DD-MM-YYYY.")

async def send_birthday_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    today = datetime.datetime.now().date()
    for user_id, info in birthdays.items():
        if info['date'] == today:
            await context.bot.send_message(chat_id=user_id, text=info['message'])

def schedule_birthday_messages(application: Application) -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_birthday_message, CronTrigger(hour=0, minute=0), args=[application])
    scheduler.start()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    application = Application.builder().token("7427281140:AAHb2cEJNgulYKP7hh39GLACQhZgq4Y_o00").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setbirthday", set_birthday))
    schedule_birthday_messages(application)
    application.run_polling()

if __name__ == '__main__':
    main()
