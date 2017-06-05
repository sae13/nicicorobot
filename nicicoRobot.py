#!/usr/bin/env python3
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from botFatherToken import botFatherToken
from requests import get

update_id = None
admins_username = {'Saeb_m': '09133917225'}  # admins user names stand here
start_deleting_hour = 22  # the hour when posting is illegal
finish_deleting_time = 7  # the hour ppl can post msgs again
spammers = {}  # list of spammers
reports_dict = {}
if (finish_deleting_time - start_deleting_hour > 0):
    activate_deleting_hour = list(
        range(start_deleting_hour, finish_deleting_time))
else:
    activate_deleting_hour = list(range(start_deleting_hour, 24)) + \
                             list(range(0, finish_deleting_time))


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

    logging.basicConfig(format='%(asctime)s - %``(name)s - %(levelname)s -\
     %(message)s')

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
            #####VARIABlES:##############
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
            msg_date = str(update.message.date).split()
            msg_date = msg_date[1].split(":")
            msg_time = int(msg_date[0])
            msg_from_user_id = update.message.from_user.id
            msg_from_user_username = update.message.from_user.username
            msg_text = update.message.text
            group_administrators = bot.get_chat_administrators(chat_id)
            text_database_file = open('/home/saeb/log/text_database_file.txt', \
                                      "a+")
            text_database_file.write("\n\n\n{}\n\n\n".format(update.message))
            text_database_file.close;
            have_spammer = False  # did any one spam today? not yet
            did_we_sent_rules = False
            # bot.send_message(chat_id=245549956,text="selam")
            # update.message.reply_text("replay id is : {} ".format(msg_text))
            print("\n{}\n".format(update.message))
            for i in group_administrators:
                 print(i)
            if msg_text != None:
                if (msg_text == 'نامناسب'):
                    manageReports(update, bot, chat_id, msg_from_user_id)

                if (msg_text.lower() == 'reports') and \
                        (msg_from_user_username in admins_username.keys()):
                    # update.message.reply_text("تابع ارسال گزارشات")
                    for keys in reports_dict:
                        bot.send_message(chat_id=chat_id,
                                         text="پیام‌های گزارش شده",
                                         reply_to_message_id=keys)
            if (msg_time in activate_deleting_hour) and \
                    (msg_from_user_username not in admins_username.keys()):
                delete_spams(msg_from_user_id, chat_id, msg_id, \
                             have_spammer, bot)


def delete_spams(msg_from_user_id, chat_id, msg_id, have_spammer, bot):
    if not have_spammer:
        have_spammer = True
        spam_times = 0
    if msg_from_user_id not in spammers:
        spammers[msg_from_user_id] = 1
    else:
        spam_times = int(spammers[msg_from_user_id])
        if spam_times > 10:
            bot.kickChatMember(chat_id, msg_from_user_id)
            spammers[msg_from_user_id] = 0
        else:
            spammers[msg_from_user_id] = int(spam_times + 1)
    print('\nfunction delete_spamer is working\nspammer: {}\
     \n\n\nspamtime : {}\n\n'.format(msg_from_user_id, spam_times))
    bot.deleteMessage(chat_id, msg_id)

    # bot.send_message(chat_id,"hi")


def unbanAgain(chat_id, msg_from_user_id, bot):
    for key in spammers:
        print("\n\n\nspammers: \n\n\n\n{}".format(spammers))
        bot.unbanChatMember(chat_id, key)
        spammers[key] = 0
    print("spammers are : \n{}\n".format(spammers))
    have_spammer = False
    print("\nspammer  if : {}\n".format(spammers))
    print("\nhave spammers : {}\n".format(have_spammer))


def manageReports(update, bot, chat_id, msg_from_user_id):
    global reports_dict
    print(reports_dict)
    # bot.get_chat_administrators()
    if (update.message.reply_to_message != None):
        bot.delete_message(chat_id=chat_id, \
                           message_id=update.message.message_id)
        tmp_text = update.message.reply_to_message
        original_reported_id = tmp_text['message_id']
        if original_reported_id not in reports_dict.keys():
            reports_dict[original_reported_id] = [msg_from_user_id]

        if original_reported_id in reports_dict:
            if msg_from_user_id not in reports_dict[original_reported_id]:
                reports_dict[original_reported_id].append(msg_from_user_id)
        for keys in reports_dict:
            if (len(reports_dict[keys]) > 1):
                from botFatherToken import sms_panel_data, sms_panel_url
                msg = 'باسلام واحترام\n' \
                      'تعدادی از کاربران معتقدند پیام نامناسبی' \
                      ' در گروه هست.لطفا تلگرام را چک کنید'
                sms_panel_data['to'] = '9132933702'
                text = get("{}?"
                           "from={}&"
                           "to={}&"
                           "msg={}&"
                           "uname={}&"
                           "pass={}".format(
                    sms_panel_url,
                    sms_panel_data['from'],
                    sms_panel_data['to'],
                    msg,
                    sms_panel_data['uname'],
                    sms_panel_data['pass']
                ))
                print('smsreport:{}\n'.format(text.text))
                reports_dict[keys] = []



                # update.message.reply_text("replay id is : {} "\
                #                          .format(original_reported_id))
                # bot.sendMessage(chat_id, "replay id is : {} "\
                #                .format(original_reported_id))


if __name__ == '__main__':
    main()
