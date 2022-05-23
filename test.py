import requests

api_token = 'MY_TOKEN'

requests.get(
    'https://api.telegram.org/bot{5358840445:AAGWQmwIjKsFb3v5hhUUvemz0VK-bfzG4Jw}/sendMessage'.format(api_token),
    params=dict(
        chat_id='@Gosha_Spiridonov',
        text='Hello world!'
    ))
