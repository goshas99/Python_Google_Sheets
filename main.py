import urllib
import pyodbc
import pandas as pd
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
from urllib.request import urlopen
from xml.etree import ElementTree as etree
import time

connect = psycopg2.connect(database='Python_DB', user='postgres', password='', host='localhost',
                           port='5432')  # Подключение к БД
print("Database opened successfully")
cursor = connect.cursor()

CREDENTIALS_FILE = 'my-project-2-350814-4336aa244179.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])


def create_gs():  # создание таблицы Google
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': 'Python_doc', 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист номер один',
                                   'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
    }).execute()
    spreadsheetId = spreadsheet['spreadsheetId']

    driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
    access = driveService.permissions().create(
        fileId=spreadsheetId,
        body={'type': 'user', 'role': 'writer', 'emailAddress': 'gosha583@gmail.com'},
        fields='id'
    ).execute()

    print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)


def extracted():  # Основная функция, обеспечивающая заполнение БД данными из GoogleSheets
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
    spreadsheetId = '1_KniAa0KhLRILavfAw7H8vDXeLUJM3FOLumLj3pGPb4'

    ranges = ["Лист номер один!A2:E200"]

    results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                       ranges=ranges,
                                                       valueRenderOption='FORMATTED_VALUE',
                                                       dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']

    # print(sheet_values)

    def convert_value(a):  # Конвертация долларов в рубли
        for i in sheet_values:
            price = int(i[2])
            date = i[3]
            with urlopen(
                    f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}",
                    timeout=10) as r:
                answer = etree.parse(r).findtext('.//Valute[@ID="R01235"]/Value')
                answer = answer.replace(",", ".")
                answer2 = float(answer)
                convert = price * answer2
                i.insert(3, convert)

    convert_value(sheet_values)

    cursor.execute("DELETE FROM python_google")
    for j in sheet_values:
        date = (j[4])
        date_sp = date.split('.')
        date_sp.reverse()
        answer = ".".join(date_sp)
        a = answer.replace('.', '-')

        cursor.execute(
            f"INSERT INTO python_google (№, заказ_№, стоимость_$, стоимость_руб, срок_поставки) VALUES (%s, %s, %s, %s, '%s')" % (
                j[0], j[1], j[2], j[3], a))
        connect.commit()


x = 1
while True:  # Обеспечение постоянного мониторинга обновлений в документе GoogleSheets
    try:
        cursor.execute("SELECT COUNT(*) FROM python_google")
        actual_records_count = cursor.fetchall()
        print(actual_records_count)
        extracted()
        print("Data has been successfully updated", x, "times")
        x += 1
        time.sleep(3)
        cursor.execute("SELECT COUNT(*) FROM python_google")
        new_records_count = cursor.fetchall()
        print(new_records_count)
        if actual_records_count == new_records_count:
            print("There's no new records here")
        else:
            if actual_records_count < new_records_count:
                print("New row added")
            else:
                print("Deleted row")
    except Exception as e:
        continue
