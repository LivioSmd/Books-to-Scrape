import csv
import requests
from bs4 import BeautifulSoup
import os


def RetrieveAllBookInformation(linkTarget):
    response_url = requests.get(linkTarget)
    soup = BeautifulSoup(response_url.text, "html.parser")
    book_info = {'title': soup.find('h1').text, 'universal_product_code': soup.find_all('tr')[0].findNext('td').text,
                 'price_including_tax': soup.find_all('tr')[2].findNext('td').text,
                 'price_excluding_tax': soup.find_all('tr')[3].findNext('td').text,
                 'number_available': soup.find_all('tr')[5].find('td').text,
                 'category': soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip(),
                 'product_descriptions': soup.find('article', class_='product_page').find_all('p')[3].text,
                 'image_url': soup.find('img').get('src').replace("../../", "https://books.toscrape.com/"),
                 'review_rating': soup.find('p', class_='star-rating').get('class')[1]}

    return book_info


def ScrapeEveryBookPages(url):
    response_url = requests.get(url)
    if response_url.ok:
        soup = BeautifulSoup(response_url.text, "html.parser")
        get_h3_list = soup.find('ol', 'row').find_all('h3')
        link_get = []

        for h3 in get_h3_list:
            book_url = h3.find('a', href=True)
            if book_url is not None:
                new_book_url = book_url['href'].replace("../../../", "https://books.toscrape.com/catalogue/")
                link_get.append(new_book_url)

        while True:
            next_button = soup.find('li', class_='next')
            if next_button is not None:
                button_href = next_button.find('a')['href']
                if button_href is not None:
                    next_page_url = url.replace("index.html", button_href)
                    response_next_page_url = requests.get(next_page_url)
                    if response_next_page_url.ok:
                        soup = BeautifulSoup(response_next_page_url.text, "html.parser")
                        get_h3_list = soup.find('ol', 'row').find_all('h3')
                        for h3 in get_h3_list:
                            book_url = h3.find('a', href=True)
                            if book_url is not None:
                                new_book_url = book_url['href'].replace("../../../",
                                                                        "https://books.toscrape.com/catalogue/")
                                link_get.append(new_book_url)
                    else:
                        break  # Sortir du while si il n'y a pas de page suivante (ok = no)
                else:
                    break  # Sortir du while si le bouton 'next' n'a pas d'attribut 'href' (button_href = is none)
            else:
                break  # Sortir du while si le bouton 'next' n'est pas trouvé (next_button = is none)
        all_books_info = []

        for link in link_get:
            if response_url.ok:
                all_books_info.append(RetrieveAllBookInformation(link))

        return all_books_info


def clean_filename(filename):
    special_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in special_chars:
        filename = filename.replace(char, '_')  # Remplacer les caractères spéciaux par des underscores
    return filename


def RetrieveAllBooksInfo(homeUrl):
    response_url_home = requests.get(homeUrl)
    if response_url_home.ok:
        soup = BeautifulSoup(response_url_home.text, "html.parser")
        category_list = soup.find('ul', class_='nav nav-list').find('li').find('ul').find_all('li')
        image_folder = 'Images'
        csv_folder = 'Csv'
        os.makedirs(image_folder)
        os.makedirs(csv_folder)

        for category in category_list:
            category_link = category.find('a')['href'].replace("catalogue/", "https://books.toscrape.com/catalogue/")
            category_name = category.find('a').text.strip().replace(' ', '_')  # récup nom de la catégorie
            books_in_category = ScrapeEveryBookPages(category_link)
            csv_file_category = f'{category_name}_books.csv'  # recup nom de la catégorie pour le CSV
            columns = ['title', 'universal_product_code', 'price_including_tax', 'price_excluding_tax',
                       'number_available', 'category', 'product_descriptions', 'image_url', 'review_rating']
            csv_path = os.path.join(csv_folder, csv_file_category)

            with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                for book in books_in_category:
                    writer.writerow(book)
                    image_url = book['image_url']
                    image_name = clean_filename(
                        book['title']) + '.jpg'  # Utiliser une fonction pour nettoyer le nom du fichier
                    image_path = os.path.join(image_folder, image_name)  # Créer le chemin d'accès du fichier image
                    response = requests.get(image_url)
                    if response.ok:
                        with open(image_path, 'wb') as i:
                            i.write(response.content)


def main():
    url_home = 'https://books.toscrape.com/index.html'
    RetrieveAllBooksInfo(url_home)


if __name__ == "__main__":
    main()
