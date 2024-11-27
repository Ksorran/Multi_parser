from work_with_book import create_book

from Classes import Ozon_parser, WildberriesParser


ozon_data = None
wb_data = None


class multi_ozon_parser(Ozon_parser):
    def save_data(self):
        global ozon_data
        ozon_data = self.data


class multi_wb_parser(WildberriesParser):
    def save_data(self):
        global wb_data
        wb_data = self.data


def multi_parser_main(key_words: str, page_count=1, max_price=20000):
    multi_ozon_parser(key_words, page_count=page_count, max_price=max_price).parse()
    multi_wb_parser(key_words, page_count=page_count, max_price=max_price).parse()
    global ozon_data
    global wb_data
    create_book(ozon_data, wb_data)


if __name__ == '__main__':
    multi_parser_main(key_words='nintendo switch', max_price=200000, page_count=2)
# Создать интерфейс
