import requests
from bs4 import BeautifulSoup
import time

SCRAPERAPI_KEY = "YOUR_API_KEY"  # Your ScraperAPI key
MAX_CHARS_PER_SOURCE = 2000  # Limit text to avoid LLM max token issues

def scrape_url(url: str, retries: int = 3, backoff: int = 5) -> str:
    """
    Scrapes a single URL using ScraperAPI and returns cleaned text.
    Removes headers, footers, navs, buttons, scripts.
    """
    api_url = f"https://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}&render=true"

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(api_url, timeout=60)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'button', 'form']):
                tag.decompose()

            text = ""

            # --- Site-specific parsing ---
            if "wikipedia.org" in url:
                content_div = soup.find("div", id="mw-content-text")
                if content_div:
                    paragraphs = content_div.find_all("p")
                    text = "\n".join(p.get_text(strip=True) for p in paragraphs[:10])

            elif "news.google.com" in url:
                headlines = soup.find_all("h3")
                text = "\n".join(h.get_text(strip=True) for h in headlines[:10])

            elif "reddit.com" in url:
                posts = soup.find_all("h3")
                if not posts:
                    posts = soup.find_all("p")
                text = "\n".join(p.get_text(strip=True) for p in posts[:15])

            elif "bbc.com" in url or "cnn.com" in url:
                paragraphs = soup.find_all("p")
                text = "\n".join(p.get_text(strip=True) for p in paragraphs[:15])

            elif "twitter.com" in url or "x.com" in url:
                tweets = soup.find_all("div", {"data-testid": "tweetText"})
                if tweets:
                    text = "\n".join(t.get_text(strip=True) for t in tweets[:10])
                else:
                    text = soup.get_text("\n", strip=True)

            # Generic fallback
            if not text:
                body = soup.body
                if body:
                    text = body.get_text("\n", strip=True)

            # Return limited length
            return text.strip()[:MAX_CHARS_PER_SOURCE]

        except requests.RequestException:
            if attempt < retries:
                time.sleep(backoff)
            else:
                return ""

def scrape_multiple_urls(urls: list, max_urls: int = 5) -> str:
    """
    Scrapes multiple URLs and concatenates cleaned content.
    """
    scraped_texts = []
    for idx, url in enumerate(urls):
        if idx >= max_urls:
            break
        text = scrape_url(url)
        if text:
            scraped_texts.append(f"--- Content from {url} ---\n{text}")
    return "\n\n---\n\n".join(scraped_texts)

