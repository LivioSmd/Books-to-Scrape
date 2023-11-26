import requests
from bs4 import BeautifulSoup

url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
url_category_travel = 'https://books.toscrape.com/catalogue/category/books/travel_2/index.html'
url_historical_fiction = 'https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html'

response_url = requests.get(url)
response_url_category_travel = requests.get(url_category_travel)
response_url_historical_fiction = requests.get(url_historical_fiction)

print(response_url)
print(response_url_category_travel)
print(response_url_historical_fiction)


def RetrieveAllBookInformation():
    book_info = {}
    book_info['title'] = soup.find('h1').text
    book_info['universal_product_code'] = soup.find_all('tr')[0].findNext('td').text
    book_info['price_including_tax'] = soup.find_all('tr')[2].findNext('td').text
    book_info['price_excluding_tax'] = soup.find_all('tr')[3].findNext('td').text
    book_info['number_available'] = soup.find_all('tr')[5].find('td').text
    book_info['category'] = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
    book_info['product_descriptions'] = soup.find('article', class_='product_page').find_all('p')[3].text
    book_info['image_url'] = soup.find('img').get('src').replace("../../", "https://books.toscrape.com/")
    book_info['review_rating'] = soup.find('p', class_='star-rating').get('class')[1]
    return book_info


if response_url_historical_fiction.ok:
    soup = BeautifulSoup(response_url_historical_fiction.text, "html.parser")
    get_h3_list = soup.find('ol', 'row').find_all('h3')
    link_get = []

    for h3 in get_h3_list:
        book_url = h3.find('a', href=True)
        if book_url is not None:
            new_book_url = book_url['href'].replace("../../../", "https://books.toscrape.com/catalogue/")
            link_get.append(new_book_url)

    print(link_get)
    print(len(link_get))

    if soup.find('li', class_='next').find('a').text is not None:
        button_next = soup.find('li', class_='next').find('a')['href']
        next_page_url = url_historical_fiction.replace("index.html", button_next)
        response_next_page_url = requests.get(next_page_url)
        if response_next_page_url.ok:
            soup = BeautifulSoup(response_next_page_url.text, "html.parser")
            get_h3_list = soup.find('ol', 'row').find_all('h3')
            for h3 in get_h3_list:
                book_url = h3.find('a', href=True)
                if book_url is not None:
                    new_book_url = book_url['href'].replace("../../../", "https://books.toscrape.com/catalogue/")
                    link_get.append(new_book_url)

    print(link_get)
    print(len(link_get))

    all_books_info = []

    for link in link_get:
        response_url = requests.get(link)
        if response_url.ok:
            soup = BeautifulSoup(response_url.text, "html.parser")
            all_books_info.append(RetrieveAllBookInformation())

    print(all_books_info)
    print(len(all_books_info))

