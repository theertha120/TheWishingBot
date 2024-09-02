import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store users' birthdays
birthdays = {}

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Use /setbirthday to set a birthday.')

# Function to set the birthday
async def set_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /setbirthday <DD-MM-YYYY> <User's Telegram ID> <Message>")
            return
        
        date_str, user_id, message = args
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        
        # Store the birthday in the dictionary
        birthdays[user_id] = {'date': date, 'message': message}
        
        await update.message.reply_text(f"Birthday set for user {user_id} on {date_str}.")
    except ValueError:
        await update.message.reply_text("Invalid date format. Use DD-MM-YYYY.")

# Function to send the birthday message
async def send_birthday_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    today = datetime.datetime.now().date()
    for user_id, info in birthdays.items():
        if info['date'] == today:
            await context.bot.send_message(chat_id=user_id, text=info['message'])

# Function to schedule birthday messages
def schedule_birthday_messages(application: Application) -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_birthday_message, CronTrigger(hour=0, minute=0), args=[application])
    scheduler.start()

# Function to handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function to start the bot
def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's token
    application = Application.builder().token("7427281140:AAHb2cEJNgulYKP7hh39GLACQhZgq4Y_o00").build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setbirthday", set_birthday))

    # Schedule birthday messages
    schedule_birthday_messages(application)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
