from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
import csv

routes = ['https://www.theverge.com',
          'https://www.theverge.com/tech',
          'https://www.theverge.com/reviews',
          'https://www.theverge.com/science',
          'https://www.theverge.com/entertainment',
          'https://www.theverge.com/featured-video',
          'https://www.theverge.com/podcasts']

articles = []
csv_data = ''

csv_file = f"{datetime.today().strftime('%d%m%Y')}_verge.csv"
fields = ['id', 'url', 'headline', 'author', 'date']
rows = []

for url in routes:
    response = get(url)
    htmlContent = response.content

    soup = BeautifulSoup(htmlContent, 'html.parser')

    links = soup.find_all('a')

    def is_article(string):
        try:
            float(string)
            if len(string) == 8:
                return True
            else:
                return False
        except ValueError:
            return False
    
    for i in links:
        for _ in i.get('href').split('/'):
            if is_article(_) and f"{routes[0]}{i.get('href')}" not in articles:
                articles.append(f"{routes[0]}{i.get('href')}")

idc = 0

for article in articles:
    id = idc
    
    url = article

    try:
        htmlContent = get(url).content
        soup = BeautifulSoup(htmlContent, 'html.parser')
        h = soup.find('h1')
        headline = h.contents[0]
    except:
        headline = ''
        articles.pop(articles.index(article))
        continue
    
    try:
        a = soup.find_all('a')
        for _ in a:
            if 'authors' in _.get('href'):
                author = _.contents[0]
                if (author['class']):
                    author = str(_.contents[0])[36:-7]
    except:
        pass

    try:
        dt = soup.find('time')
        date = dt.contents[-1].strip()
        dt_object = datetime.strptime(date, '%b %d, %Y, %I:%M %p %Z')
        year = dt_object.year
        month = dt_object.month
        day = dt_object.day
        date = f"{year}/{month:d}/{day:d}"
    except:
        date = ''

    if len(date) == 0:
        date = '/'.join(url.split('/')[3:6])

    rows.append([id, url, headline, author, date])

    idc+=1

with open(csv_file, 'w', newline='') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)