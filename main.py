from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import sqlite3

# Appending the possibles routes of The Verge Website where articles can be found (I have listed the main categories just to showcase my skills, there are sub categories also which can be appended)
routes = ['https://www.theverge.com',
          'https://www.theverge.com/tech',
          'https://www.theverge.com/reviews',
          'https://www.theverge.com/science',
          'https://www.theverge.com/entertainment',
          'https://www.theverge.com/featured-video',
          'https://www.theverge.com/podcasts']

# Creating a list where I want to append all the articles found on all the routes of the websites in the routes list because there are some other comments' articles also
articles = []

# Creating a string containing the file_name with the date in front of it as per mentioned in the Problem Statement
# I am not mentioning the extension because I have used the file_name both with the .db and .csv files
file_name = f"{datetime.today().strftime('%d%m%Y')}_verge"
# Creating list of fields of the CSV file
fields = ['id', 'url', 'headline', 'author', 'date']
# Creating a rows list to store date both in the CSV and SQLite DB
rows = []

# Connecting to the SQLite Database (If it is not there, it will create one. I have created it in such way that it creates a separate database on every new day we execue the code.)
conn = sqlite3.connect(file_name+'.db')
# Creating a cursor for the connection to execute SQL Commands
crsr = conn.cursor()
# Creating a table to store the records if the table does not already exist
crsr.execute('''CREATE TABLE IF NOT EXISTS articles
                (id INTEGER PRIMARY KEY,
                 url TEXT,
                 headline TEXT,
                 author TEXT,
                 date TEXT);''')

# Iterating through each category route of The Verge Website
for url in routes:
    response = get(url)
    htmlContent = response.content

    soup = BeautifulSoup(htmlContent, 'html.parser')

    # Looking for all the anchor tags which contains the links to all the articles and the comment articles or sub articles on that particular page
    links = soup.find_all('a')

    # After getting all the links, I need to filter out only the links which head us to the articles and not to comment articles or sub articles
    def is_article(string):
        '''
        `is_article(string)` function takes a strins, checks whether the string which is actually the article ID on the website is a number or not and whether it is 8-digit number or not.
        Because the comments and sub-articles does not have the article ID on this website
        '''
        try:
            float(string)
            if len(string) == 8:
                return True
            else:
                return False
        except ValueError:
            return False
    
    # Formating the links' url in such way that they directly lead to the article page and appending them to the articles list if it not present in it so that we don't get duplicate links
    for i in links:
        for _ in i.get('href').split('/'):
            if is_article(_) and f"{routes[0]}{i.get('href')}" not in articles:
                articles.append(f"{routes[0]}{i.get('href')}")

# Declaring a variable to count the number of ids need to be stored in the csv and the db file
# Used the Index number of the article in the articles list before but some old sub-articles in the website had Article ID which made it recognize as an article in the `is_article` function
# But those sub-articles did not have Headlines, so the articles without the headlines are sub-articles and I'm ignoring them and continuing to the next iteration
# Initialized it to 0 as the Test Case in the Problem Statement Starts from 0
idc = 0

# Iterating through each filtered article url
for article in articles:
    # Assigning the ID Primary Key
    id = idc
    
    # Assigning the Article url to the url to be loaded  to the csv and the db
    url = article

    # Parsing the Article url and finding the first h1 because it contains the Headline
    # If it does not have a headline, that means its not an article webpage, its an sub-article webpage so continuing to the next iteration of the articalurl
    try:
        htmlContent = get(url).content
        soup = BeautifulSoup(htmlContent, 'html.parser')
        h = soup.find('h1')
        headline = h.contents[0]
    except:
        headline = ''
        articles.pop(articles.index(article))
        continue
    
    # Finding all the anchor tags and if its href has the 'authors' string, it has the Author Name in its contents. (For e.g., href='https://www.theverge.com/authors/chris-welch')
    # In some of the articles found which are of 2018, the anchor tags have a span which contains the name in its contents but the span tag is now a string so indexed it out to [36:-7]
    try:
        a = soup.find_all('a')
        for _ in a:
            if 'authors' in _.get('href'):
                author = _.contents[0]
                if (author['class']):
                    author = str(_.contents[0])[36:-7]
    except:
        pass

    # Finding the time tag because the date and time of articles post in this website are mentioned within `time` tags
    # But they show the time in Mar 27, 2023, 6:30 PM GMT+5:30 format, so need to convert them into 2023/3/27 format as per the Problem Statement
    # The articles of 2018 have '\n' in the front and back of the time string and also had unecessary spaces (for us) in between, so needed to strip them
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

    # After doing so, some dates were blank, so just sliced them out from the project url directly, which could have been done for all the articles to save time
    if len(date) == 0:
        date = '/'.join(url.split('/')[3:6])

    # Appending the record to the rows list
    rows.append([id, url, headline, author, date])

    # Increasing the count of ID Primary Key
    idc+=1

# Writing the rows to the CSV File
with open(file_name+'.csv', 'w', newline='') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

# Writing the rows to the Database Table
for row in rows:
    crsr.execute('''INSERT INTO articles (id, url, headline, author, date) VALUES (?, ?, ?, ?, ?)''', row)

# Closing the Database Connection 
conn.commit()
conn.close()