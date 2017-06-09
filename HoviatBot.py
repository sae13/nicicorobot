#!/usr/bin/env python3
##########packages
from botFatherToken import hoviatBotToken
from telegram.ext import CommandHandler
import telegram
from telegram.error import NetworkError, Unauthorized
import logging
from time import sleep
from random import randint
from requests import get
import sqlite3
from khayyam import JalaliDate
from datetime import datetime
#########VAriables
update_id = None
user_info_dict = {}
#####Database
db = sqlite3.connect('nicico.sqlite')
db.execute('''CREATE TABLE IF NOT EXISTS verified (
           user_id VARCHAR(30) NOT NULL,
           code_melli VARCHAR(20) ,
           shomare_personeli VARCHAR(20) ,
           mobile INT NOT NULL,
           verified_date CHARACTER(8) ,
           verified_jdate CHARACTER(8) );''')
db.close()
#########functions
def main():
    global update_id
    bot = telegram.Bot(hoviatBotToken)
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
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            print("\n pending list:\n{}\nmessage:{}\n".format(user_info_dict,
                                                              update.message))
            date_today =datetime.today()
            jdate_today = JalaliDate.today()
            date_today = "{:02d}{:02d}{}".format(date_today.day,
                                                 date_today.month,
                                                 date_today.year)
            jdate_today = "{:02d}{:02d}{}".format(jdate_today.day,
                                                 jdate_today.month, jdate_today.year)
            print("\ntoday:{}\njtoday:{}\n".format(date_today,jdate_today))
            msg_id = update.message.message_id
            user_id = update.message.from_user.id
            chat_id = update.message.chat.id
            conn = sqlite3.connect('file:nicico.sqlite', uri=True)
            db_user_id = conn.execute("SELECT user_id from verified \
                                         where user_id == (?)", (user_id,))


            if db_user_id.fetchone():
                bot.send_message(chat_id, "حساب شما قبلا ثبت و تایید شده"
                                          "\n"
                                          "درصورت مشاهده هرگونه اشکال با یکی از"
                                          "مدیران گروه صحبت نمایید"
                                          " با ارسال واژه "
                                          "\n"
                                          "مدیران"
                                          "\n"
                                          "درگروه لیست مدیران به شما نمایش داده"
                                          " می‌شود.")
                break
            conn.close()
            if update.message.text:
                msg_text = update.message.text.split('+')
                if user_id in user_info_dict.keys():
                    code_melli = user_info_dict[user_id]['code_melli']
                    mobile = user_info_dict[user_id]['mobile']
                    shomare_personeli = user_info_dict[user_id]['shomare_personeli']
                    if int(msg_text[0]) == \
                                user_info_dict[user_id]['sms_verification_code']:

                        conn = sqlite3.connect('nicico.sqlite')
                        tmp_data =conn.execute("INSERT INTO  verified "
                                                   "(user_id,"
                                                   "code_melli,"
                                                   "shomare_personeli,"
                                                   "mobile,"
                                                   "verified_date,"
                                                   "verified_jdate) VALUES "
                                                   "((?),(?),(?),(?),(?),(?))",(user_id,
                                                        code_melli,
                                                        shomare_personeli,
                                                        mobile,
                                                        date_today,
                                                        jdate_today))
                        conn.commit()
                        bot.send_message(chat_id,"اطلاعات شما ثبت شد")
                        user_info_dict.pop(user_id)
                        conn.close()
                        break
                if (len(msg_text) == 3 and msg_text[0].isnumeric()\
                            and len(msg_text[0]) == 10 \
                            and len(msg_text[1]) == 6 \
                            and len(msg_text[2]) == 11) :
                    social_id = (msg_text[0])
                    personal_id = int(msg_text[1])
                    mobile_number = str(msg_text[2])
                    verify_sms = randint(123456,456789)

                    from botFatherToken import sms_panel_data
                    sms_panel_data['to'] = mobile_number
                    text = get("{}?"
                               "from={}&"
                               "to={}&"
                               "msg={}&"
                               "uname={}&"
                               "pass={}".format(
                       sms_panel_data['sms_panel_url'] ,
                        sms_panel_data['from'],
                        sms_panel_data['to'],
                        verify_sms,
                        sms_panel_data['uname'],
                        sms_panel_data['pass']
                    ))
                    user_info_dict[user_id]={'code_melli':social_id,
                                        'shomare_personeli':personal_id,
                                        'mobile':mobile_number,
                                        'sms_verification_code':int(verify_sms)}
                    bot.send_message(chat_id,"تالحظاتی دیگه عددی شش رقمی به شما"
                                             " پیامک می‌شود.عددراواردنمایید:")

                    print("اطلاعات صحیح بود:\n{}".format(msg_text))
                    print(user_info_dict)
                    break

                else:
                    bot.send_message(chat_id=chat_id,
                                             text="اطلاعات نادرست بود.لطفا مشابه"
                                                  " مثال اطلاعات را وارد نمایید."
                                                  "توجه داشته باشید شماره همراه با"
                                                  " صفر شروع می‌شود و کدملی ده رقم است"
                                             )
                    askPhoneNumber(chat_id,bot)
                    break

                # print(msg_text)
            # askPhoneNumber(chat_id,bot)

def askPhoneNumber(chat_id, bot):
    bot.send_message(chat_id=chat_id, text="باسلام و احترام"
                                           "\n"
                                           "لطفاکدملی+شماره پرسنلی+شماره همراه"
                                           "\n"
                                           "خودرامشابه فرم ذیل پر کنید:"
                                           "\n"
                                           "3149922507+730654+09133917225"
                                           "\n"
                                           "دقت نمایید اول کد ملی"
                                           "\n"
                                           "بعد یک علامت"
                                           "\n"
                                           "+"
                                           "\n"
                                           "بعد شماره پرسنلی"
                                           "\n"
                                           "مجدد یک "
                                           "\n"
                                           "+"
                                           "\n"
                                           "و در آخر شماره همراه"
                                           "\n"
                                           "در هیچ یک از مراحل نیاز به زدن کلید "
                                           "فاصله"
                                           "\" \""
                                           "نیست:"
                                           ""
                                           "")
# def insert_into_db(dict):



if __name__ == '__main__':
    main()
