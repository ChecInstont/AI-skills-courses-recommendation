import os
import logging
import json
import httpx
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.ERROR)

# Load environment variables
load_dotenv()


# Initialize LangChain with the custom Gemini LLM
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key for Gemini is missing.")

# Google Custom Search API setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
if not GOOGLE_API_KEY or not GOOGLE_CX:
    raise ValueError("Google API Key or CX (Search Engine ID) is missing.")


async def google_search_results(query):
    """Fetch results from Google Custom Search and extract relevant snippets."""
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
    }
    try:
        search_results = {}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise an exception for non-2xx responses
            search_results = response.json()
        items = search_results.get("items", [])
        # logging.warning(f"items : {items} query : {query} search_results : {search_results}")
        # snippet = item.get("snippet", "could not find any information in web")
        # logging.info(f"query ; {query} result : {snippet}")
        search_results_limit = os.getenv("SEARCH_RESULTS_LIMIT",3)
        search_results_limit = int(search_results_limit)
        final_result = items[:search_results_limit]
        return final_result

        # Extract snippets from results
        # snippets = [item.get("snippet", "") for item in items]
        # logging.info(snippets)

        # # Return all snippets combined for now
        # return "\n".join(snippets) if snippets else "No relevant information found."
    except Exception as e:
        # return f"Error fetching Google search results: {e}"
        return None