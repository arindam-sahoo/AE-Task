from requests import get
from bs4 import BeautifulSoup

routes = ['https://www.theverge.com',
          'https://www.theverge.com/tech',
          'https://www.theverge.com/reviews',
          'https://www.theverge.com/science',
          'https://www.theverge.com/entertainment',
          'https://www.theverge.com/featured-video',
          'https://www.theverge.com/podcasts']

articles = []

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
            if is_article(_) and f"{url}{i.get('href')}" not in articles:
                articles.append(f"{url}{i.get('href')}")

for article in articles:
    id = articles.index(article)
    
    url = article

    htmlContent = get(url).content
    soup = BeautifulSoup(htmlContent, 'html.parser')
    h = soup.find('h1')
    headline = h.contents[0]
    
    a = soup.find_all('a')
    for _ in a:
        if 'authors' in _.get('href'):
            author = _.contents[0]

    dt = soup.find('time')
    date = dt.contents[-1][:12]