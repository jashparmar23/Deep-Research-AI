import requests
from typing import Dict, Any, List

class RapidAIAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://social-media-master.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-host": "social-media-master.p.rapidapi.com",
            "x-rapidapi-key": self.api_key,
        }

    def get_post_details(self, user_id: str, post_id: str, include_profile: bool = False) -> Dict[str, Any]:
        """
        Call /universal-post-details for a single post
        Returns the JSON data from the API
        """
        url = f"{self.base_url}/universal-post-details"
        params = {
            "id": user_id,
            "postID": post_id,
            "includeProfile": str(include_profile).lower(),
        }

        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def fetch_data(self, query: str, date_range: Dict[str, str] = None, max_results: int = 5) -> Dict[str, Any]:
        """
        Fixed: Handle both post pairs AND regular queries
        For post pairs: "user_id1:post_id1,user_id2:post_id2,..."
        For regular queries: fallback to empty results (since no search endpoint exists)
        """
        urls: List[str] = []
        aggregated_content: List[str] = []

        # Check if query contains post pairs (user_id:post_id format)
        if ":" in query and any("," in query or len(query.split(":")) == 2):
            # Handle post pairs format
            pairs = [q.strip() for q in query.split(",") if ":" in q]

            for pair in pairs[:max_results]:
                try:
                    user_id, post_id = pair.split(":", 1)
                    data = self.get_post_details(user_id.strip(), post_id.strip())

                    # Extract link and content from post details
                    if "post" in data and len(data["post"]) > 0:
                        post_data = data["post"][0]["postDetails"]

                        # Get URL
                        post_url = post_data.get("postUrl")
                        if post_url:
                            urls.append(post_url)

                        # Get content
                        text_content = post_data.get("text", "")
                        if text_content:
                            aggregated_content.append(text_content)

                except Exception as e:
                    print(f"Failed fetching post {pair}: {e}")
        else:
            # For regular queries, return empty since no search endpoint exists
            print(f"Warning: No search endpoint available for query: {query}")
            print("To use social media data, provide post pairs in format: user_id:post_id,user_id2:post_id2")

        return {
            "urls": urls,
            "content": "\n\n".join(aggregated_content),
        }

if __name__ == "__main__":
    api_key = "YOUR_API_KEY"
    agent = RapidAIAgent(api_key)

    # Example usage:
    print("Examples:")
    print("1. Post pairs: '1756191247484x952736576247618300:1951787277069258956'")
    print("2. Regular query: 'AI trends' (will return empty - no search endpoint)")

    query = input("Enter query: ").strip()

    try:
        result = agent.fetch_data(query, max_results=5)
        print("Fetched Data:")
        print(result)
    except Exception as e:
        print(f"Error fetching data: {e}")

