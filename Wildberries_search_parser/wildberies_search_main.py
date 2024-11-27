import requests
import json


class WildberriesParser:
    def __init__(self, key_words: str, page_count=1, max_price=20000):
        self.url = 'https://search.wb.ru/exactmatch/ru/common/v7/search'
        self.key_words = key_words
        self.page_count = page_count
        self.max_price = max_price
        self.data = []

    def set_params(self, page=1):
        self.params = {
            'ab_testing': 'false',
            'appType': '1',
            'page': str(page),
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
            self.set_params(int(self.params['page'])+1)
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
        self.save_data()

    def save_data(self):
        """Сохраняем отобранную информацию"""
        with open('items.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def parse(self):
        self.set_params()
        self.get_page()
        self.paginate()


if __name__ == '__main__':
    WildberriesParser(
        key_words='nintendo switch',
        page_count=1,
        max_price=22000
    ).parse()
