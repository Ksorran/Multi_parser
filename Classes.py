import time
import json
from abc import ABC, abstractmethod

import requests

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from curl_cffi import requests as cffi_requests


class Parser(ABC):
    def __init__(self, key_words: str, page_count: int, max_price: int, url: str):
        self.key_words = key_words
        self.max_price = max_price
        self.page_count = page_count
        self.data = []
        self.url = url

    @abstractmethod
    def set_up(self):
        pass

    @abstractmethod
    def get_page(self):
        pass

    @abstractmethod
    def paginate(self):
        pass

    @abstractmethod
    def start(self):
        pass


class OzonParser(Parser):
    def __init__(self, key_words: str, page_count: int, max_price: int, url="https://www.ozon.ru/"):
        super().__init__(key_words, page_count, max_price, url)
        self.driver = None
        self.products_urls = None

    def set_up(self):
        """Инициализируем и настраиваем webdriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)

    def get_page(self):
        self.driver.get(self.url)

    def search(self):
        """Осуществляем поиск по ключевым словам"""
        locator = (By.XPATH, '//input[@placeholder="Искать на Ozon"]')
        search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        search_box.clear()
        search_box.send_keys(self.key_words)
        time.sleep(0.1)
        search_box.send_keys(Keys.ENTER)

    def paginate(self):
        current_url = f'{self.driver.current_url}&sorting=rating'
        self.driver.get(url=current_url)
        if self.page_count > 1:
            while True:
                ActionChains(self.driver).scroll_by_amount(1, 500).perform()
                time.sleep(0.5)
                if len(self.driver.find_elements(By.XPATH, "//div[@id='paginatorContent']/div")) == self.page_count:
                    break

    def get_products_urls(self):
        find_links = self.driver.find_elements(By.XPATH, "//a[contains(@class,'tile-hover-target')]")
        self.products_urls = list(set([f'{link.get_attribute("href")}' for link in find_links]))

    def get_product_info(self):
        s = cffi_requests.Session()
        s.get("https://www.ozon.ru")
        for link in self.products_urls:
            api_link = f'https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={link.split('ozon.ru')[1]}'
            product_info = s.get(api_link)
            json_data = json.loads(product_info.content.decode())
            try:
                product_data = {
                    'title': json_data["seo"]["title"],
                    'price': json.loads(json_data["seo"]["script"][0]["innerHTML"])["offers"]["price"],
                    'number_of_reviews': json.loads(json_data["seo"]["script"][0]["innerHTML"])
                    ["aggregateRating"]["reviewCount"],
                    'rating': json.loads(json_data["seo"]["script"][0]["innerHTML"])["aggregateRating"]["ratingValue"],
                    'url': link
                }
                if float(product_data['price']) < self.max_price:
                    self.data.append(product_data)
            except Exception:
                continue

    def start(self):
        self.set_up()
        self.get_page()
        self.search()
        self.paginate()
        self.get_products_urls()
        self.get_product_info()
        return self.data


class WildberriesParser(Parser):
    def __init__(self, key_words: str, page_count: int, max_price: int,
                 url="https://search.wb.ru/exactmatch/ru/common/v7/search"):
        super().__init__(key_words, page_count, max_price, url)
        self.params = None
        self.response = None

    def set_up(self):
        self.params = {
            'ab_testing': 'false',
            'appType': '1',
            'page': '1',
            'curr': 'rub',
            'dest': '-1649215',
            'query': self.key_words,
            'resultset': 'catalog',
            'sort': 'popular',
            'spp': '30',
            'suppressSpellcheck': 'false',
        }

    def get_page(self):
        self.response = requests.get('https://search.wb.ru/exactmatch/ru/common/v7/search', params=self.params).json()

    def paginate(self):
        """Осуществляет перемещение по страницам и запускает парсинг"""
        while self.page_count > 0 and self.response['data']['products']:
            self.parse_page()
            self.page_count -= 1
            self.params['page'] = str(int(self.params['page'])+1)
            self.get_page()

    def parse_page(self):
        """Парсинг страницы"""
        products = self.response['data']['products']
        for product in products:
            title = product['name']
            price = product['sizes'][0]['price']['total']/100
            number_of_reviews = product['feedbacks']
            rating = product['reviewRating']
            url = f'https://www.wildberries.ru/catalog/{product['id']}/detail.aspx'
            data = {
                'title': title,
                'price': price,
                'number_of_reviews': number_of_reviews,
                'rating': rating,
                'url': url,
            }
            if price <= self.max_price:
                self.data.append(data)

    def start(self):
        self.set_up()
        self.get_page()
        self.paginate()
        return self.data
