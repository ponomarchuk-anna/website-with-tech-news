"""
    В этом файле реализован парсинг сайта https://telecomdaily.ru/
"""

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webapp import create_app
import locale
import os
import time
import utils

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Firefox(
        service=Service(os.path.join(os.getcwd(), 'geckodriver')),
        options=options,
    )
    return driver


def parse_telecom(url):
    print('Начал парсить...')
    driver = get_driver()
    driver.get(url)
    # даём сайту время прогрузиться - двух секунд будет достаточно
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.find_all('div', class_='news-teaser')
    for post in posts:
        title = post.find('a').text
        # заменяем относительную ссылку на новость на абсолютную
        url = 'https://telecomdaily.ru' + post.find('a')['href']
        # изменяем дату: по умолчанию год не указан и равен 1900
        date = post.find('div', class_='created-at').text
        if 'вчера' in date or 'сегодня' in date:
            day = datetime.now()
            new_day = day.day
            if 'вчера' in date:
                new_day = int(datetime.now().day) - 1
            time_n = date.split()[1]

            datetime_str = f'{day.year}-{day.month:02d}-{new_day:02d} {time_n}'
            parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H.%M')

        else:
            if 'назад' in date:
                if date.split()[0] == 'час':
                    day = datetime.now()
                    new_day = day.day
                    hours, minutes = day.hour, day.minute
                    hours = int(hours) - 1
                    time_n = str(hours) + ':' + str(minutes)

                    datetime_str = f'{day.year}-{day.month:02d}-{new_day:02d} {time_n}'
                    parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

                elif date.split()[1] == 'часа' or date.split()[1] == 'часов':
                    day = datetime.now()
                    new_day = day.day
                    hours, minutes = day.hour, day.minute
                    hours = int(datetime.now().hour) - int(date.split()[0])
                    time_n = str(hours) + ':' + str(minutes)

                    datetime_str = f'{day.year}-{day.month:02d}-{new_day:02d} {time_n}'
                    parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

                elif date.split()[0] == 'минуту':
                    day = datetime.now()
                    new_day = day.day
                    hours, minutes = day.hour, day.minute
                    minutes = int(minutes) - 1
                    time_n = str(hours) + ':' + str(minutes)

                    datetime_str = f'{day.year}-{day.month:02d}-{new_day:02d} {time_n}'
                    parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

                elif date.split()[1] == 'минуты' or date.split()[1] == 'минут' or date.split()[1] == 'минуту' or date.split()[1] == 'минуты':
                    day = datetime.now()
                    new_day = day.day
                    hours, minutes = day.hour, day.minute
                    minutes = int(datetime.now().minute) - int(date.split()[0])
                    time_n = str(hours) + ':' + str(minutes)

                    datetime_str = f'{day.year}-{day.month:02d}-{new_day:02d} {time_n}'
                    parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            else:
                parts = date.split(' ')
                day = int(parts[0])
                time_n = parts[2]

                month_str = parts[1]
                if month_str == 'января':
                    month = 1
                elif month_str == 'февраля':
                    month = 2
                elif month_str == 'марта':
                    month = 3
                elif month_str == 'апреля':
                    month = 4
                elif month_str == 'мая':
                    month = 5
                elif month_str == 'июня':
                    month = 6
                elif month_str == 'июля':
                    month = 7
                elif month_str == 'августа':
                    month = 8
                elif month_str == 'сентября':
                    month = 9
                elif month_str == 'октября':
                    month = 10
                elif month_str == 'ноября':
                    month = 11
                elif month_str == 'декабря':
                    month = 12

                year = 2023
                datetime_str = f'{year}-{month:02d}-{new_day:02d} {time_n}'
                parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H.%M')

        #       date = datetime.strptime(date, '%Y %d %B %H.%M')

        driver.get(url)
        # даём сайту время прогрузиться - двух секунд будет достаточно
        time.sleep(2)
        html = driver.page_source
        soup2 = BeautifulSoup(html, 'html.parser')
        text = soup2.find('div', class_='news-item')

        # избавляемся от ненужных частей html-документа: рекламных баннеров, кликабельных иконок социальных сетей и прочего
        soup = BeautifulSoup(text.decode_contents(), 'html.parser')
        div_tag = soup.find('div', class_='share-container-wrapper')
        if div_tag:
            div_tag.extract()
        div_tag = soup.find('div', class_='megabitus')
        if div_tag:
            div_tag.extract()
        div_tag = soup.find('div', class_='rubrics')
        if div_tag:
                div_tag.extract()
        div_tag = soup.find('div', class_='tags')
        if div_tag:
            div_tag.extract()
        div_tag = soup.find('div', class_='main-tag')
        if div_tag:
            div_tag.extract()
        div_tag = soup.find('div', class_='title')
        if div_tag:
            div_tag.extract()

        utils.save_news(url, title, text.text, parsed_datetime, soup)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        parse_telecom('https://telecomdaily.ru/rubric/science')
