import pandas as pd
import requests
from bs4 import BeautifulSoup

# helper functions
flatten = lambda xs: [b for a in xs for b in a]
unique = lambda xs: list(set(xs))

def get_page(url):
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 '}
    # return BeautifulSoup(requests.get(url, headers=headers).text, 'lxml')
    return BeautifulSoup(requests.get(url).text, 'lxml')

# indeed
def indeed_url(job, loc, start):
    return f'https://www.indeed.ca/jobs?q={job}&l={loc}&start={start}&limit=50'

def company_names(soup):
    return [x.get_text(strip=True) for x in soup.select('.company')]

def job_count(soup):
    search_count = soup.select_one('#searchCount')
    return int(search_count.get_text(strip=True).split()[-1])

def page_numbers(soup):
    return range(0, job_count(soup), 50)

def get_all_companies(job, loc):
    search = get_page(indeed_url(job, loc, 0))
    pages = [get_page(indeed_url(job, loc, x)) for x in page_numbers(search)]
    return flatten([company_names(x) for x in pages])

# duckduckgo
def facebook_url(company):
    return f'https://duckduckgo.com/html/?q=facebook+{company}'

def get_facebook_link(company):
    soup = get_page(facebook_url(company))
    return soup.select('.web-result .result__a')[0].get('href')

# results
all_companies = get_all_companies('data+scientist', 'toronto,+on')
unique_companies = unique(all_companies)

# facebook
token = 'access_token={token goes here}'

def get_company_id(company):
    url = f'https://graph.facebook.com/v2.10/search?q={company}&type=page&{token}'
    req = requests.get(url)
    data = req.json()['data']
    return data[0]['id'] if data else None

def get_company_category(id):
    url = f'https://graph.facebook.com/v2.10/{id}?fields=category&{token}'
    req = requests.get(url)
    return req.json()['category'] if req else None

def get_company_categories(companies):
    ids = [get_company_id(x) for x in companies]
    return [get_company_category(x) if x else None for x in ids]

all_categories = get_company_categories(unique_companies)


df = pd.DataFrame({'company': unique_companies, 'category': all_categories})[['company', 'category']]
df.to_csv('data/companycategories.csv', index=False)
