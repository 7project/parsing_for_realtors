import logging
import random
import time
from decimal import Decimal
import json
from pprint import pprint

import bs4
import requests


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PARSING')


class DecimalEncoder(json.JSONEncoder):
   def default(self, o):
       if isinstance(o, Decimal):
           return float(o)
       return super(DecimalEncoder, self).default(o)


class Parser:
    """
    initialization
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',

        }
        self.domain = 'https://jk-festivalpark.ru'
        self.data_for_record = []

    def loading(self):
        while True:
            url = f'{self.domain}/kvartiry/?page=3'
            try:
                time.sleep(random.randint(1, 3))
                result = self.session.get(url=url, timeout=(15, 5))
                return result.text
            except Exception as exp:
                logger.info(exp)

    def parser_page(self, text):
        soup = bs4.BeautifulSoup(text, 'lxml')
        data = soup.select('tr.j-building-tr-link')
        logger.info(f'Длинна списка - {len(data)}')
        for block in data:
            self.parse_block(block=block)

    def parse_block(self, block):
        img_block = block.select_one('img.b-search-results-table__img-big')
        if not img_block:
            logger.error('Not url_block')
            return

        url = img_block.get('src')
        if not url:
            logger.error('Not src')
            return

        data_link = block.get('data-link')
        if not data_link:
            logger.error('Not data_link')
            return

        name_block = block.select_one('div.b-search-results-table__name')
        if not name_block:
            logger.error('Not name_block')
            return

        location_block = block.select_one('div.b-search-results-table__info')
        if not location_block:
            logger.error('Not location_block')
            return

        td_four_block = block.select_one('td:nth-of-type(4)')
        if not td_four_block:
            logger.error('Not td_four_block')
            return

        td_five_block = block.select_one('td:nth-of-type(5)')
        if not td_five_block:
            logger.error('Not td_five_block')
            return
        td_five_block = td_five_block.text[:-3]

        td_six_block = block.select_one('td:nth-of-type(6)')
        if not td_six_block:
            logger.error('Not td_six_block')
            return

        price_td_seven_block = block.select_one('td:nth-of-type(7)')
        if not price_td_seven_block:
            logger.error('Not price_td_seven_block')
            return

        living_area = self._living_area(data_link)

        logger.info(f'{self.domain}%s, {self.domain}%s, %s, %s, %s, %s, %s, %s, %s', data_link, url,
                    name_block.text.strip(), location_block.text, td_four_block.text,
                    td_five_block, td_six_block.text, living_area, price_td_seven_block.text)

        price_td_seven_block = price_td_seven_block.text[:-4]
        price_td_seven_block = price_td_seven_block.split()
        price_td_seven_block = ''.join(price_td_seven_block)

        if living_area:
            living_area = float(living_area)

        self.data_for_record.append(
            {
                'complex': 'Фестиваль Парк',
                'type': 'flat',
                'phase': None,
                'building': int(location_block.text.split(',')[0].split()[1]),
                'section': location_block.text.split(',')[1].split()[1],
                'price_base': Decimal(price_td_seven_block),
                'price_sale': None,
                'price_finished_sale': None,
                'area': float(td_five_block),
                'living_area': living_area,
                'number': None,
                'number_on_site': None,
                'rooms': None,
                'floor': int(td_six_block.text.split('/')[0]),
                'in_sale': 1,
                'sale_status': 'в продаже',
                'finished': 'optional',
                'ceil': Decimal(3.1),
                'article': None,
                'finishing_name': 'White box',
                'furniture': None,
                'furniture_price': None,
                'plan': 'https://jk-festivalpark.ru' + url,
                'feature': None,
                'view': ['на Москву', 'на реку'],
                'euro_planning': 1,
                'sale': None,
                'discount_percent': None,
                'discount': None,
            }
        )

    def _living_area(self, url):
        url_living_area = f'{self.domain}{url}'
        text_living_area = None
        try:
            time.sleep(random.randint(2, 5))
            with requests.Session() as session1:
                session1.headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                }
                text_living_area = session1.get(url=url_living_area, timeout=(15, 5))
                text_living_area = text_living_area.text

        except Exception as exp:
            logger.info(f'Первая ошибка - {exp}')
            time.sleep(random.randint(2, 5))
            with requests.Session() as session2:
                session2.headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                }
                try:
                    text_living_area = session2.get(url=url_living_area, timeout=(25, 10))
                    text_living_area = text_living_area.text
                except Exception as exp2:
                    logger.info(f'Повторная ошибка - {exp2}')

        if text_living_area:
            soup_living_area = bs4.BeautifulSoup(text_living_area, 'lxml')
            data = soup_living_area.select('li.b-param-list__item')
            living_area = data[1].select_one('div.b-param-list__data')
            living_area = living_area.text[:-3]
        else:
            living_area = None
        return living_area

    def run(self):
        text = self.loading()
        self.parser_page(text=text)
        logger.info(f'Длинна списка - {len(self.data_for_record)}')
        pprint(self.data_for_record)
        data_file = json.dumps(self.data_for_record, cls=DecimalEncoder, indent=1, sort_keys=False,
                               ensure_ascii=False).encode('utf-8').decode('windows-1251')
        with open('date_json.json', 'w') as file_data:
            file_data.write(data_file)


if __name__ == '__main__':
    parser = Parser()
    parser.run()
