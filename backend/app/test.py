from social_media import RapidAIAgent

if __name__ == "__main__":
    rapidai_api_key = "YOUR API KEY"
    agent = RapidAIAgent(rapidai_api_key)

    query = input("Enter a query to test RapidAI: ").strip()
    if not query:
        print("Query cannot be empty. Exiting.")
        exit(1)

    try:
        # Only query and max_results; remove date_filter
        data = agent.fetch_data(query, max_results=5)
        urls = data.get("urls", [])
        content = data.get("content", "")

        print("\nRapidAI returned URLs:")
        if urls:
            for i, url in enumerate(urls, 1):
                print(f"{i}. {url}")
        else:
            print("No URLs returned by RapidAI.")

        print("\nAggregated Content:")
        print(content[:500] + "..." if len(content) > 500 else content)

    except Exception as e:
        print(f"Error fetching data from RapidAI: {e}")

