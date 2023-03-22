import logging
from tele import *
from telegram.ext import Updater, MessageHandler, Filters


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    TOKEN = os.environ.get('TOKEN') # you can get the token from BotFather
    PORT = int(os.environ.get('PORT', '8443'))

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    print("Bot is running...")
    
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook(url=f"https://learn-gpt.herokuapp.com/{TOKEN}")
    updater.idle() 

if __name__ == '__main__':
    print("Starting bot...")
    main()
