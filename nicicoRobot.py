import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from botFatherToken import botFatherToken
update_id = None
admins_username = ['Saeb_m']
def main():
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(botFatherToken)
    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %``(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def echo(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
            msg_date = str(update.message.date).split()
            msg_date = msg_date[1].split(":")
            msg_time = int(msg_date[0])
            msg_from_id = update.message.from_user.id
            print("\n\n\n{}\n\n{}\n\n\n\n\n".format(msg_time, msg_from_id))
            print(update.message)  # your bot can receive updates without messages
            # Reply to the message
            #update.message.reply_text(update.message.text)
            if ((msg_time > 14) or ( msg_time < 8)) and \
            update.message.from_user.username not in admins_username :
                bot.deleteMessage(chat_id,msg_id)
                bot.kickChatMember(chat_id, msg_from_id)
if __name__ == '__main__':
    main()
