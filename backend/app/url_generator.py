# url_generator.py
import urllib.parse

def generate_urls(query: str) -> list:
    """
    Generates a list of real and scrapable URLs based on the query.
    """
    encoded_query = urllib.parse.quote_plus(query)

    urls = [
        f"https://www.google.com/search?q={encoded_query}",
        f"https://news.google.com/search?q={encoded_query}",
        f"https://www.reddit.com/search/?q={encoded_query}",
        f"https://medium.com/search?q={encoded_query}",
        f"https://hn.algolia.com/?q={encoded_query}"
    ]

    print("\nURLs to be scraped:")
    for idx, u in enumerate(urls, start=1):
        print(f"{idx}. {u}")

    return urls
