import requests
from bs4 import BeautifulSoup
from newspaper import Article
from playwr_crawler import get_rendered_html

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Referer": "https://duckduckgo.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def needs_browser(url: str) -> bool:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Couldn't fetch the page: {e}")
        return True

    # Heuristic 1: Check content length
    if len(r.content) < 1000:
        return True

    soup = BeautifulSoup(r.text, "html.parser")

    # Heuristic 2: Check for article or text content
    has_text = bool(soup.find_all(["p", "article", "h1", "h2", "h3"]))
    if not has_text:
        return True

    # Heuristic 3: Look for common JS-heavy placeholders
    suspicious_markers = [
        "id=\"__NEXT_DATA__\"", "id=\"root\"", "window.__INITIAL_STATE__",
        "data-reactroot", "ng-version", "id=\"app\""
    ]
    for marker in suspicious_markers:
        if marker in r.text:
            return True

    return False


def fetch_article(url: str) -> str:
    if not needs_browser(url):
        print(f"****** {url} processing with requests")
        return fetch_content(url)
    else:
        print(f"###### {url} processing with playwright")
        html_text = get_rendered_html(url)
        return fetch_content(url, html_text)


def get_html(url: str) -> str:
    if not needs_browser(url):
        article = Article(url)
        article.download()
        article.parse()
        return article.article_html
    else:
        whole_html = get_rendered_html(url)
        article = Article(url)
        article.set_html(whole_html)
        article.parse()
        return article.article_html


def fetch_content(url: str, html_content: str = None):
    try:
        article = Article(url)
        if html_content:
            article.set_html(html_content)
        else:
            article.download()
        article.parse()
        article.nlp()

        return {
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "text": article.text,
            "top_image": article.top_image,
            "summary": article.summary,
        }
    except Exception as e:
        print(f"Unable to fetch the url: {e}")
        return ""


def fetch_links(html_text: str, filter: list[str] = None) -> list[str]:
    soup = BeautifulSoup(html_text, "lxml")
    links = [a.get('href') for a in soup.find_all("a", href=True)]
    print(f"found {len(links)} links")
    filtered = links
    if filter is not None:
        filtered = [item for item in links if item not in filter]
    return filtered
