from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
#worked with Tessa Voytevich & Miles Sheffler


def get_titles_from_search_results():
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + 'search_results.html')
    text = f.read()
    f.close()
    books = []
    soup = BeautifulSoup(text, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        title = row.find('a', class_='bookTitle').text.strip()
        author = row.find('a', class_='authorName').text.strip()
        Ratings = row.find('span', class_='minirating').text.split(" ")
        rating = re.findall('[0-9]+', Ratings[-2])
        rating2 = ""
        for rate in rating:
            rating2 += rate
        info = title, author, int(rating2)
        books.append(info)
    return books

def get_links():
    links = []
    url = 'https://www.goodreads.com/search?q=david+sedaris&qid='
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tags = soup.find_all('a', class_ = 'bookTitle', href = True )
    for tag in tags[:5]:
        part1 = "https://www.goodreads.com"
        part2 = tag['href']
        links.append(part1 + part2)
    return links

def get_book_summary(book_html):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    with open(path + book_html, 'r') as file:
        r = file.read()
    soup = BeautifulSoup(r, "html.parser")
    auth_tag = soup.find('span', itemprop = 'name')
    author = auth_tag.text.rstrip().lstrip()
    title_tag = soup.find('h1', id = 'bookTitle')
    title = title_tag.text.rstrip().lstrip()
    page_tag = soup.find("span", itemprop = 'numberOfPages')
    page_list = page_tag.text.split(" ")
    pages = int(page_list[0])
    rating_tag = soup.find('span', itemprop = "ratingValue")
    rating = float(rating_tag.text)
    review_tag = soup.find("meta", itemprop = "reviewCount")
    reviews = int(review_tag.get('content'))
    return title, author, pages, rating, reviews

def summarize_best_books(filepath):
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/" + 'best_books_2021.html')
    text = f.read()
    f.close()
    best_books = []
    cat_tags = []
    title_tags = []
    link_tags = []
    soup = BeautifulSoup(text, 'html.parser')
    for cat_tag in soup.find_all('h4', class_ = "category__copy"):
        category = cat_tag.text.rstrip().lstrip()
        cat_tags.append(category)
    for title_tag in soup.find_all('img', alt = True, class_ = "category__winnerImage"):
        title = title_tag['alt']
        title_tags.append(title)
    for link_tag in soup.find_all('a', href = re.compile('\/choiceawards\/\S+2021$')):
        href = link_tag['href']
        link = "https://www.goodreads.com" + href
        if link not in link_tags:
            link_tags.append(link)
    for i in range(len(cat_tags)):
        Category = cat_tags[i]
        Title = title_tags[i]
        Link = link_tags[i]
        tup = Category, Title, Link
        best_books.append(tup)
    return best_books

def write_csv(data, filename):
    f = open(filename, 'w')
    writer = csv.writer(f)
    header = writer.writerow(["Book title","Author Name","Ratings"])
    data_sorted = sorted(data, key = lambda Tup: Tup[2])
    for item in data_sorted:
        row = writer.writerow(item)
    f.close()

class TestCases(unittest.TestCase):

    # call get_links() and save it to a static variable: search_urls

    def test_get_titles_from_search_results(self):
        # call get_titles_from_search_results() and save to a local variable
        titles = get_titles_from_search_results()
        # check that the number of titles extracted is correct (20 titles)
        self.assertEqual(len(titles), 20)
        # check that the variable you saved after calling the function is a list
        self.assertIsInstance(titles, list)
        # check that each item in the list is a tuple
        for i in titles:
            self.assertIsInstance(i, tuple, True)
        # check that the first book, author, and ratings tuple is correct (open search_results.html and find it)
        self.assertEqual(titles[0], ('Harry Potter and the Deathly Hallows (Harry Potter, #7)', 'J.K. Rowling', 2795923))
        # check that the last title is correct (open search_results.html and find it)
        self.assertEqual(titles[-1][0], 'Harry Potter: The Prequel (Harry Potter, #0.5)')
        
    def test_get_links(self):
        search_urls = get_links()
        # check that TestCases.search_urls is a list
        self.assertEqual(type(search_urls), list)
        # check that the length of TestCases.search_urls is correct (5 URLs)
        self.assertEqual(len(search_urls), 5)
        # check that each URL contains the correct url for Goodreads.com followed by /book/show/
        count = 0
        for link in search_urls:
            if "/book/show/" not in link:
                count += 1
        self.assertEqual(count, 0)

    def test_get_book_summary(self):
        # the list of webpages you want to pass in one by one into get_book_summary
        # all of these are stores in the book_summary_html_files folder
        html_list = ['book_summary_html_files/Me Talk Pretty One Day by David Sedaris.html',
                     'book_summary_html_files/David Sedaris - 14 CD Boxed Set by David Sedaris.html',
                     'book_summary_html_files/SantaLand Diaries by David Sedaris.html',
                     'book_summary_html_files/Dress Your Family in Corduroy and Denim by David Sedaris.html',
                     'book_summary_html_files/David Sedaris_ Live For Your Listening Pleasure by David Sedaris.html']
        # create an empty list
        list = []
        # for i in html_list:
        for i in html_list:
            x = get_book_summary(i)
            list.append(x)
        # check that the number of book summaries is correct (5)
        self.assertEqual(len(list), 5)
            # check that each item in the list is a tuple
        for item in list:
            self.assertIsInstance(item, tuple, True)
            # check that each tuple has 5 elements
            self.assertEqual(len(item), 5)
            # check that the first two elements in the tuple are string
            self.assertIsInstance(item[0], str, True)
            self.assertIsInstance(item[1], str, True)
            # check that the third and fifth element in the tuple, i.e. pages and review count are ints
            self.assertIsInstance(item[2], int, True)
            self.assertIsInstance(item[4], int, True)
            # check that the fourth element in the tuple, i.e. rating is a float
            self.assertIsInstance(item[3], float, True)
        # check that the first book in the search has 272 pages
        self.assertEqual(list[0][2], 272)
        # check that the last book has 4.35 rating
        self.assertEqual(list[4][3], 4.35)
        # check that the third book as a reviw count of 539
        self.assertEqual(list[2][4], 539)

    def test_summarize_best_books(self):
        # call summarize_best_books on best_books_2021.html and save it to a variable
        test1 = summarize_best_books('best_books_2021.html')
        # check that we have the right number of best books (17)
        len_check = []
        for tup in test1:
            len_check.append(tup[0])
        self.assertEqual(len(len_check), 17)
            # assert each item in the list of best books is a tuple
        for item in test1:
            self.assertIsInstance(item, tuple, True)
            # check that each tuple has a length of 3
            self.assertEqual(len(item), 3)
        # check that the first tuple is made up of the following 3 strings:'Fiction', "Beautiful World, Where Are You", 'https://www.goodreads.com/choiceawards/best-fiction-books-2021'
        self.assertEqual(test1[0], ('Fiction', "Beautiful World, Where Are You", 'https://www.goodreads.com/choiceawards/best-fiction-books-2021'))
        # check that the last tuple is made up of the following 3 strings: 'Middle Grade & Children's', 'Daughter of the Deep', 'https://www.goodreads.com/choiceawards/best-childrens-books-2021'
        self.assertEqual(test1[-1], ("Middle Grade & Children's", 'Daughter of the Deep', 'https://www.goodreads.com/choiceawards/best-childrens-books-2021'))

    def test_write_csv(self):
    #     # call get_titles_from_search_results on search_results.htm and save the result to a variable
        data = get_titles_from_search_results()
    #     # call write csv on the variable you saved
        write_csv(data, 'outfile')
    #     # read in the csv that you wrote
        file = open('outfile')
        f = file.readlines()
        file.close()
        l = []
        for line in f:
            l.append(line.rstrip())
        # check that there are 21 lines in the csv
        self.assertEqual(len(l), 21)
        # check that the header row is correct
        self.assertEqual(l[0],"Book title,Author Name,Ratings" )
        # # check that the next row is Harry Potter: A History of Magic,British Library,13153
        self.assertEqual(l[1],'Harry Potter: A History of Magic,British Library,13153')
        # # check that the last row is "Harry Potter and the Sorcerer's Stone (Harry Potter, #1)",J.K. Rowling,7003900
        self.assertEqual(l[-1],'"Harry Potter and the Sorcerer\'s Stone (Harry Potter, #1)",J.K. Rowling,7003900')
    

if __name__ == '__main__':
    unittest.main(verbosity=2)