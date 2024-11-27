import xlsxwriter


def create_book(data_ozon, data_wb):
    book = xlsxwriter.Workbook('multi_parser.xlsx')
    page = book.add_worksheet('Общий список')

    page.set_column('A:A', 50)
    page.set_column('B:B', 20)
    page.set_column('C:C', 20)
    page.set_column('D:D', 20)
    page.set_column('E:E', 50)
    page.set_column('F:F', 20)

    header = book.add_format({'bold': True})

    page.write('A1', 'Название', header)
    page.write('B1', 'Цена', header)
    page.write('C1', 'Количество оценок', header)
    page.write('D1', 'Рейтинг', header)
    page.write('E1', 'Ссылка', header)
    page.write('E1', 'Площадка', header)

    row = 1
    column = 0

    for product in data_ozon:
        page.write(row, column, product['title'])
        page.write(row, column+1, product['price'])
        page.write(row, column+2, product['number_of_reviews'])
        page.write(row, column+3, product['rating'])
        page.write(row, column+4, product['url'])
        page.write(row, column + 4, 'Ozon')
        row += 1

    for product in data_wb:
        page.write(row, column, product['title'])
        page.write(row, column+1, product['price'])
        page.write(row, column+2, product['number_of_reviews'])
        page.write(row, column+3, product['rating'])
        page.write(row, column+4, product['url'])
        page.write(row, column + 4, 'Wildberries')
        row += 1

    book.close()
