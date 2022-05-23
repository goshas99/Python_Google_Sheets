import telebot
import psycopg2
import datetime
import time

bot = telebot.TeleBot('') #Уникальный токен Бота

connect = psycopg2.connect(database='Python_DB', user='postgres', password='', host='localhost', port='5432') #Подключение к БД
print("Database opened successfully")
cursor = connect.cursor()


@bot.message_handler(commands=["start"]) #Декоратор для команды /start(начало работы бота)
def hello(m, res=False):
    user_id = m.from_user.id
    username = m.from_user.username
    bot.send_message(m.chat.id,
                     f'\nЗдравствуйте, {username}! Бот предназначен для отслеживания актуальности срока поставки.')

    while True:
        try:
            cursor.execute("SELECT COUNT(*) FROM python_google")
            actual_records_count = cursor.fetchall()
            time.sleep(5)
            cursor.execute("SELECT COUNT(*) FROM python_google")
            new_records_count = cursor.fetchall()
            if actual_records_count == new_records_count:
                print("There's no new records here")
            else:
                if actual_records_count < new_records_count:
                    print("New row added")
                    notif(m, res)
                else:
                    print("Deleted row")
        except Exception as e:
            continue


def notif(m, res=False): #Функция, позволяющая уведомить пользователя о прошедшем сроке поставки
    cursor.execute("SELECT срок_поставки FROM python_google ORDER BY № DESC LIMIT 1;")
    period = cursor.fetchall()
    cursor.execute("SELECT заказ_№ FROM python_google ORDER BY № DESC LIMIT 1;")
    order = cursor.fetchall()
    cursor.execute("SELECT заказ_№ FROM python_google WHERE срок_поставки < current_date;")
    all_period = cursor.fetchall()
    my_list = []
    for x in all_period:
        my_list.append(' | '.join(x))
        my_str = '\n'.join(my_list)

    test1 = datetime.date.today()
    if period[0][0] < test1:
        bot.send_message(m.chat.id, "Внимание! Срок поставки истек! Последний истекший заказ:")
        bot.send_message(m.chat.id, order)
        bot.send_message(m.chat.id, period)
        bot.send_message(m.chat.id, my_str)
            # bot.send_message(m.chat.id, test1)
            # time.sleep(20)


# @bot.message_handler(content_types=['text'])
# def handle_text(m):
#     if m.text.strip() == 'overdue':
#         cursor.execute("SELECT заказ_№ FROM python_google WHERE срок_поставки < current_date;")
#         actual_records = cursor.fetchall()
#         my_list = []
#         for x in actual_records:
#             my_list.append(' | '.join(x))
#         my_str = '\n'.join(my_list)
#         bot.send_message(m.chat.id, my_str)
#
#     if m.text.strip() == 'notification':
#         cursor.execute("SELECT срок_поставки FROM python_google ORDER BY № DESC LIMIT 1;")
#         test = cursor.fetchall()
#         test1 = datetime.date.today()
#         if test[0][0] < test1:
#             bot.send_message(m.chat.id, "Внимание! Срок поставки истек!")
#             bot.send_message(m.chat.id, test)
#             bot.send_message(m.chat.id, test1)


bot.polling(none_stop=True, interval=0)
