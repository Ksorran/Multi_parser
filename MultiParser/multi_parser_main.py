from work_with_book import create_book
from Classes import OzonParser, WildberriesParser
import tkinter as tk
from tkinter import messagebox


def multi_parser_main(key_words: str, page_count=1, max_price=20000):
    ozon_data = OzonParser(key_words=key_words, page_count=page_count, max_price=max_price).start()
    wb_data = WildberriesParser(key_words=key_words, page_count=page_count, max_price=max_price).start()
    create_book(ozon_data, wb_data)

def start_parser():
    """Собирает информацию, поступившую от пользователя через графический интерфейс и запускает на ее основе парсер"""
    key_words = key_words_entry.get()
    page_count = int(pages_entry.get())
    max_price = int(max_price_entry.get())
    multi_parser_main(key_words=key_words, page_count=page_count, max_price=max_price)
    messagebox.showinfo("Информация", "Парсинг завершен. Результаты сохранены в multi_parser.xlsx")


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Marketplaces Parser")

    tk.Label(root, text="Введите элементы для поиска (через пробел):").grid(row=0, column=0, padx=10, pady=10)
    key_words_entry = tk.Entry(root, width=50)
    key_words_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Введите количество страниц:").grid(row=1, column=0, padx=10, pady=10)
    pages_entry = tk.Entry(root, width=10)
    pages_entry.grid(row=1, column=1, padx=10, pady=10)
    pages_entry.insert(0, '1')

    tk.Label(root, text="Введите максимально допустимую стоимость:").grid(row=2, column=0, padx=10, pady=10)
    max_price_entry = tk.Entry(root, width=10)
    max_price_entry.grid(row=2, column=1, padx=10, pady=10)
    max_price_entry.insert(0, '20000')

    tk.Button(root, text="Запуск парсера", command=start_parser).grid(row=3, column=0, columnspan=2, padx=10, pady=20)

    root.mainloop()