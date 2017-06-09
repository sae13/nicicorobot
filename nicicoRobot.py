#!/usr/bin/env python3
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from botFatherToken import botFatherToken
from requests import get
from khayyam import JalaliDatetime
import sqlite3
import datetime
upppdate = None
update_id = None
admins_username = {}#'Saeb_m': '09133917225',
                  #'Hojati':'0'}  # admins user names stand here
start_deleting_hour = 16  # the hour when posting is illegal
finish_deleting_time = 15  # the hour ppl can post msgs again
spammers = {}  # list of spammers
reports_dict = {}
group_administrators=group_administrators_list = {}
unverified = {}
if (finish_deleting_time - start_deleting_hour > 0):
    activate_deleting_hour = list(
        range(start_deleting_hour, finish_deleting_time))
else:
    activate_deleting_hour = list(range(start_deleting_hour, 24)) + \
                             list(range(0, finish_deleting_time))


def main():
    global update_id
    global upppdate
    # Telegram Bot Authorization Token
    bot = telegram.Bot(botFatherToken)
    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.

    try:
        update_id = bot.get_updates()[0].update_id
        upppdate = bot.get_updates()[0]

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
        uppdate = bot.get_updates(offset=2,timeout=10)
        if update.message:
            print("\n{}\n".format(update.message))
            bot_info = bot.get_me()
            chat_id = update.message.chat.id
            msg_id = update.message.message_id
            msg_date = str(update.message.date).split()
            msg_jalali_date = JalaliDatetime(update.message.date)
            msg_jalali_date_str = "{}{:02d}{}".format(msg_jalali_date.year,
                                                  msg_jalali_date.month,
                                                  msg_jalali_date.day)
            print("message date:{}\n".format(msg_jalali_date_str))
            msg_date = msg_date[1].split(":")
            msg_time = int(msg_date[0])
            msg_from_user_id = update.message.from_user.id
            msg_from_user_username = update.message.from_user.username
            msg_text = update.message.text
            group_administrators = bot.get_chat_administrators(chat_id)
            group_administrators_list = {}
            for key in group_administrators:
                group_administrators_list[key.user.id] =\
                    str(key.user.username)
            group_administrators_list.pop(bot_info.id)
            text_database_file = open('/home/saeb/log/text_database_file.txt', \
                                      "a+")
            text_database_file.write("\n\n\n{}\n\n\n".format(update.message))
            text_database_file.close;
            have_spammer = False
            #####DB
            conn = sqlite3.connect("file:nicico.sqlite",uri = True)
            verified_user = conn.execute("SELECT user_id from verified where (user_id =="
                                 " (?));",(msg_from_user_id,)).fetchone()
            if verified_user == None and msg_from_user_id not in \
                    group_administrators_list.keys():
                if msg_jalali_date_str not in unverified.keys():
                    tmp_user_msg_count = {}
                    tmp_user_msg_count[msg_from_user_id] = 0
                    unverified[msg_jalali_date_str] = \
                    tmp_user_msg_count
                    print("unverified mssg list first update",unverified)
                if msg_from_user_id not in\
                        unverified[msg_jalali_date_str].keys():
                    tmp_user_msg_count = {}
                    tmp_user_msg_count[msg_from_user_id] = 0
                    unverified[msg_jalali_date_str].update(tmp_user_msg_count)
                unverified[msg_jalali_date_str][msg_from_user_id] = \
                    unverified[msg_jalali_date_str][msg_from_user_id]+1
                if unverified[msg_jalali_date_str][msg_from_user_id] > 5 :
                   bot.delete_message(chat_id,msg_id)

            print("tayid nashode ha:{}".format(unverified))
            conn.close()
            if msg_text != None:
                if (msg_text == 'مدیران'):
                    admins_username_for_print = "لیست مدیران:\n"
                    for i in group_administrators_list.keys():
                        admins_username_for_print = admins_username_for_print +\
                            ("@{}\n".format(str(group_administrators_list[i])))
                    bot.send_message(chat_id,admins_username_for_print)
                    bot.delete_message(chat_id,msg_id)

                if (msg_text == 'نامناسب'):
                    manageReports(update, bot, chat_id, msg_from_user_id)

                if (msg_text.lower() == 'reports') and \
                        (msg_from_user_id in group_administrators_list.keys()):
                    bot.delete_message(chat_id, msg_id)
                    for keys in reports_dict:
                        bot.send_message(chat_id=chat_id,
                                         text="این پیام گزارش شده",
                                         reply_to_message_id=keys)
            if (msg_time in activate_deleting_hour) and \
                    (msg_from_user_id not in\
                             group_administrators_list.keys()):
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
    bot.deleteMessage(chat_id, msg_id)
def unbanAgain(chat_id, msg_from_user_id, bot):
    for key in spammers:
        bot.unbanChatMember(chat_id, key)
        spammers[key] = 0
def manageReports(update, bot, chat_id, msg_from_user_id):
    global reports_dict
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
                from botFatherToken import sms_panel_data
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
                    sms_panel_data['sms_panel_url'],
                    sms_panel_data['from'],
                    sms_panel_data['to'],
                    msg,
                    sms_panel_data['uname'],
                    sms_panel_data['pass']
                ))
if __name__ == '__main__':
    main()
