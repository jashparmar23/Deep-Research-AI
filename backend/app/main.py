from model import GGUFModel
from scrapper import scrape_multiple_urls
from social_media import RapidAIAgent
from url_generator import generate_urls
import contextlib
import sys

def categorize_scraped_data(urls, scraped_texts, rapidai_content=""):
    """
    Categorize content by source (Google, Wikipedia, News, RapidAI, etc.)
    Returns a dict: {source: [texts]}
    """
    categorized = {}

    if rapidai_content.strip():
        categorized["RapidAI"] = [rapidai_content]

    for url, text in zip(urls, scraped_texts):
        if not text.strip():  # skip empty content
            continue
        if "google.com/search" in url:
            source = "Google Search"
        elif "news.google.com" in url:
            source = "Google News"
        elif "wikipedia.org" in url:
            source = "Wikipedia"
        elif "reddit.com" in url:
            source = "Reddit"
        elif "medium.com" in url:
            source = "Medium"
        elif "bbc.com" in url or "cnn.com" in url:
            source = "News Site"
        else:
            source = "Other"

        categorized.setdefault(source, []).append(text)

    return categorized


if __name__ == "__main__":
    user_query = input("Enter your query: ").strip()
    if not user_query:
        exit(1)

    start_date = input("Start date (YYYY-MM-DD) or leave blank: ").strip()
    end_date = input("End date (YYYY-MM-DD) or leave blank: ").strip()
    date_filter = {}
    if start_date:
        date_filter["start"] = start_date + "T00:00:00Z"
    if end_date:
        date_filter["end"] = end_date + "T23:59:59Z"

    # Initialize LLM
    model_path = r"C:\Users\jashp\Downloads\Deep Research Agent\mistral-7b-instruct-v0.2.Q4_K_S.gguf"
    llama_cli_bin = r"C:\Users\jashp\Downloads\Deep Research Agent\llama.cpp\build\bin\Release\llama-cli.exe"
    model = GGUFModel(
        model_path=model_path,
        llama_cli_path=llama_cli_bin,
        threads=6,
        max_tokens=256,
        temperature=0.7,
        timeout=600,
    )

    # Suppress intermediate prints
    with contextlib.redirect_stdout(sys.stderr):  # redirect to stderr to hide
        initial_output = model.generate_text(user_query)

        rapidai_api_key = "56dcf10ca7msh37d661ee8670ac4p1fa914jsnd4e0fc5c3eef"
        rapid_agent = RapidAIAgent(rapidai_api_key)
        urls, aggregated_content = [], ""

        try:
            rapidai_data = rapid_agent.fetch_data(user_query, max_results=5)
            urls = rapidai_data.get("urls", [])
            aggregated_content = rapidai_data.get("content", "")
        except:
            urls, aggregated_content = [], ""

        if not urls:
            urls = generate_urls(user_query)

        scraped_texts = []
        for url in urls[:5]:
            scraped_texts.append(scrape_multiple_urls([url], max_urls=1))

        categorized_data = categorize_scraped_data(urls, scraped_texts, aggregated_content)

        final_sections = []
        for source, texts in categorized_data.items():
            combined_text = "\n\n".join(texts)
            summary = model.enhanced_generation(
                f"Summarize the following information from {source} for the query: {user_query}. "
                f"Be concise, structured, and ignore navigation/UI content.",
                initial_output,
                combined_text,
                max_total_tokens=400,
                chunk_size=200,
                timeout=600,
            )
            final_sections.append(f"### {source} Summary\n{summary}")

    # Only show final summary in CMD
    final_output = "\n\n".join(final_sections)
    print("\n================ FINAL CATEGORIZED SUMMARY ================\n")
    print(final_output)
