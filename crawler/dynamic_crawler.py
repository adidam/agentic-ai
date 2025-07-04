import requests
from bs4 import BeautifulSoup

def extract_content(urls: list) -> str:
    pass
    
def extract_content_static(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
def extract_content_dynamic(url: str) -> str:
    pass
    
def extract_links(content: str) -> list:
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a')
    return [link.get('href') for link in links]

def extract_text(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.body
        if body:
            noscript_tags = body.find_all('noscript')
            if noscript_tags:
                return extract_content_dynamic(url)
            else:
                return extract_content_static(url)
    else:
        return extract_content_static(url)


    