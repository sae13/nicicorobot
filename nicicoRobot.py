#!/usr/bin/env python3
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from botFatherToken import botFatherToken
from urllib.request import urlopen
update_id = None
admins_username = ['Saeb_m']  # admins user names stand here
start_deleting_hour = 18  # the hour when posting is illegal
finish_deleting_time = 16 # the hour ppl can post msgs again
spammers = {'111048031':'4'}  # list of spammers
night_deleting = True
if (finish_deleting_time - start_deleting_hour > 0):
    night_deleting = False

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
            text_database_file = open('/home/saeb/log/text_database_file.txt', "a+")
            text_database_file.write("\n\n\n{}\n\n\n\n".format(update.message))
            text_database_file.close;
            have_spammer = False  # did any one spam today? not yet
            did_we_sent_rules = False
            print("\n\n\n{}\n\n{}\n\n\n\n\n".format(msg_time, msg_from_id))
            print(update.message)  # your bot can receive updates without messages
            print("\n\n\n\nreplay to message: {}\n\n\n\n".format(update.message.reply_to_message))
            ###################debug log
            try:
                tmp_text = update.message.reply_to_message
                tmp_text_id = tmp_text['message_id']
            except:
                tmp_text_id = 'nothing'
            #bot.sendMessage(chat_id,"replay id is : {} ".format(tmp_text_id))
            update.message.reply_text("replay id is : {} ".format(tmp_text_id))
            ##############debug part finished#################

            if night_deleting:
                if ((msg_time > start_deleting_hour) or (msg_time < finish_deleting_time)) \
                        and msg_from_id not in admins_username:
                    deleteSpams(msg_from_id, chat_id, msg_id,have_spammer,bot)
                if ((update.message.text == 'now' and msg_from_id in admins_username) or (((finish_deleting_time <= msg_time) \
                        and (msg_time <= start_deleting_hour)) and have_spammer)):
                    unbanAgain(chat_id, bot)
            if not night_deleting:
                if ( start_deleting_hour < msg_time < finish_deleting_time )\
                        and msg_from_id not in admins_username:
                    deleteSpams(msg_from_id, chat_id, msg_id, have_spammer, bot)
                if ( msg_time >= finish_deleting_time) and have_spammer:
                    unbanAgain(chat_id, bot)


def deleteSpams(msg_from_id, chat_id, msg_id, have_spammer,bot):
    if not have_spammer:
        have_spammer = True
    spam_times = 0
    if msg_from_id not in spammers:
        spammers[msg_from_id] = 1
    else:
        spam_times = int(spammers[msg_from_id])
        if spam_times > 10:
            bot.kickChatMember(chat_id, msg_from_id)
            spammers[msg_from_id] = 0
        else:
            spammers[msg_from_id] = int(spam_times + 1)
    print('\n\nspammer: {} \n\n\nspamtime : {}\n\n'.format(msg_from_id, spam_times))
    bot.deleteMessage(chat_id, msg_id)

def unbanAgain(chat_id,bot):
    for key in spammers:
        bot.unbanChatMember(chat_id, key)
        spammers[key] = 0
        print("spammers are : \n{}\n".format(spammers))
    have_spammer = False
    print("\nspammer  if : {}\n".format(spammers))
    print("\nhave spammers : {}\n".format(have_spammer))

if __name__ == '__main__':
    main()
