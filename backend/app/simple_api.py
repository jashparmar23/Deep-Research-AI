from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from model import GGUFModel
    from scrapper import scrape_multiple_urls
    from social_media import RapidAIAgent
    from url_generator import generate_urls
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-api")

MODEL_PATH = r"C:\Users\jashp\Downloads\Deep Research Agent\mistral-7b-instruct-v0.2.Q4_K_S.gguf"
LLAMA_CLI_BIN = r"C:\Users\jashp\Downloads\Deep Research Agent\llama.cpp\build\bin\Release\llama-cli.exe"
RAPIDAI_API_KEY = "YOUR API KEY"

model = None
rapid_agent = None

def categorize_scraped_data(urls, scraped_texts, rapidai_content=""):
    categorized = {}
    if rapidai_content.strip():
        categorized["RapidAI"] = [rapidai_content]
    for url, text in zip(urls, scraped_texts):
        if not text.strip():
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

def initialize_components():
    global model, rapid_agent
    try:
        model = GGUFModel(
            model_path=MODEL_PATH,
            llama_cli_path=LLAMA_CLI_BIN,
            threads=6,
            max_tokens=256,
            temperature=0.7,
            timeout=600,
        )
        rapid_agent = RapidAIAgent(RAPIDAI_API_KEY)
        logger.info("Components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

@app.route('/api/research', methods=['POST'])
def research_query():
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        max_sources = data.get('max_sources', 5)

        logger.info(f"Received research request: '{user_query}'")

        if not user_query:
            return jsonify({'error': 'Query cannot be empty'}), 400

        global model, rapid_agent
        if model is None or rapid_agent is None:
            initialize_components()

        date_filter = {}
        if start_date:
            date_filter["start"] = start_date + "T00:00:00Z"
        if end_date:
            date_filter["end"] = end_date + "T23:59:59Z"

        logger.info("Starting initial LLM generation...")
        initial_output = model.generate_text(user_query)

        logger.info("Fetching RapidAI data...")
        urls, aggregated_content = [], ""
        try:
            rapidai_data = rapid_agent.fetch_data(user_query, max_results=max_sources)
            urls = rapidai_data.get("urls", [])
            aggregated_content = rapidai_data.get("content", "")
            logger.info(f"Retrieved {len(urls)} URLs from RapidAI")
        except Exception as e:
            logger.warning(f"RapidAI fetch failed: {e}")

        if not urls:
            logger.info("Generating URLs using url_generator...")
            urls = generate_urls(user_query)

        logger.info("Scraping URLs...")
        scraped_texts = []
        for url in urls[:max_sources]:
            scraped_text = scrape_multiple_urls([url], max_urls=1)
            scraped_texts.append(scraped_text)

        logger.info("Categorizing scraped data...")
        categorized_data = categorize_scraped_data(urls, scraped_texts, aggregated_content)

        logger.info("Generating category summaries with fact check prompt...")
        final_sections = []
        for source, texts in categorized_data.items():
            combined_text = "\n\n".join(texts)
            summary = model.enhanced_generation(
                f"Summarize ONLY facts present in the following text from {source} for the query: {user_query}. "
                f"Do not invent or hallucinate. Return only structured headlines or facts that exactly appear in the input text. "
                f"If there is not enough relevant information, say \"Not enough explicit information found.\"",
                initial_output,
                combined_text,
                max_total_tokens=400,
                chunk_size=200,
                timeout=600,
            )
            final_sections.append(f"### {source} Summary\n{summary}")

        final_output = "\n\n".join(final_sections)
        logger.info("Research completed successfully")

        return jsonify({
            'success': True,
            'final_summary': final_output,
            'query': user_query,
            'sources_processed': len(categorized_data),
            'urls_scraped': len(urls)
        })

    except Exception as e:
        logger.error(f"Research failed with exception: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Deep Research Agent API is running (Main.py Logic)',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting Deep Research Agent API (Main.py Logic)...")
    print("🌐 API running on http://localhost:5000")
    print("📊 Frontend should connect to http://localhost:3000")
    print("📝 Using categorized summary format from main.py")

    try:
        initialize_components()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("Make sure your model files and paths are correct")
        sys.exit(1)

    app.run(debug=True, host='0.0.0.0', port=5000)
