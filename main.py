import requests
from bs4 import BeautifulSoup
import csv


def get_data(url):
    headers = {
        'Accept': 'image/webp,image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/15.0 Safari/605.1.15',
    }
    # url = 'https://snabtechmet.ru/catalog/setka-nerzhaveyushchaya/'
    file_name = url.split('/')[-2].strip()

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # пагинация, собираем все ссылки и забираем номер последней.
    pages_count = int(soup.find("ul", class_="pagination").find_all('li')[-2].text)

    # в цикле пробегаемся по всем страницам с товаром
    flag = 1
    for page in range(1, pages_count + 1):
        try:
            url = f'{url}f/page/{page}/'

            response = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            # Собираем все карточки в список
            product_cards = soup.find("div", class_="col-md-9 content").find('div', class_="product-table").find_all('tr')

            # проходим по всем карточкам и из каждой карточки собираем необходимую информацию.
            for i in product_cards:
                try:
                    product_data = i.find_all('td')

                    product_name = product_data[1].find('a').text.strip()
                    product_price = product_data[2].text.strip()

                    inside_product_link = f"https://snabtechmet.ru{product_data[1].find('a').get('href')}"

                    response = requests.get(url=inside_product_link, headers=headers)
                    soup = BeautifulSoup(response.text, 'lxml')
                    description_product = soup.find('div', itemprop="description").text.strip().replace('Снабтехмет',
                                                                                                        'МетТоргУрал')
                    product_features = soup.find('div', class_="parameter").find('ul').find_all('li')
                    product_features_dic = {
                        'Наименование': product_name,
                        'Цена': product_price,
                        'Описание': description_product,
                    }
                    temp = {}
                    for y in product_features:
                        key = y.find_all('span')[0].text
                        value = y.find_all('span')[1].text
                        temp[key] = value

                    product_features_dic = {**product_features_dic, **temp}

                    if flag == 1:
                        with open(f'{file_name}.csv', 'w', encoding='utf8', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(list(product_features_dic.keys()))
                        flag = 0

                    with open(f'{file_name}.csv', 'a', encoding='utf8', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(list(product_features_dic.values()))
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)

        print(f'Обработано {page}/{pages_count} страниц.')


def main():
    urls = [
        'https://snabtechmet.ru/catalog/klapan-otsechnoj/',
        'https://snabtechmet.ru/catalog/obratnyj-klapan/',
        'https://snabtechmet.ru/catalog/reguliruyushchij-klapan/',
        'https://snabtechmet.ru/catalog/klapan-zapornyj/',
        'https://snabtechmet.ru/catalog/oporno-napravlyayushchee-kolco/',
    ]
    for i in urls:
        get_data(i)


if __name__ == '__main__':
    main()
