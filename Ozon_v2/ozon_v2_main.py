import time
import json

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from curl_cffi import requests


class Ozon_parser:
    def __init__(self, key_words: str, page_count=1, max_price=20000):
        self.url = "https://www.ozon.ru/"
        self.key_words = key_words
        self.max_price = max_price
        self.page_count = page_count
        self.data = []

    def set_up(self):
        """Инициализируем и настраиваем webdriver"""
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--headless")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=self.options)

    def get_url(self):
        self.driver.get(self.url)

    def search(self):
        """Осуществляем поиск по ключевым словам"""
        locator = (By.XPATH, '//input[@placeholder="Искать на Ozon"]')
        search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
        search_box.clear()
        search_box.send_keys(self.key_words)
        time.sleep(0.1)
        search_box.send_keys(Keys.ENTER)

    def paginator(self):
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
        s = requests.Session()
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
            except Exception as e:
                continue

    def save_data(self):
        """Сохраняем отобранную информацию"""
        with open('ozon_items.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def parse(self):
        self.set_up()
        self.get_url()
        self.search()
        self.paginator()
        self.get_products_urls()
        self.get_product_info()
        self.save_data()


if __name__ == "__main__":
    Ozon_parser(
        key_words='Nintendo switch',
        page_count=1,
        max_price=200000
    ).parse()
