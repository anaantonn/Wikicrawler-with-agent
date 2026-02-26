from wikipedia import search, page, summary
from wikipedia.exceptions import DisambiguationError, PageError
from fastapi_utilities import ttl_lru_cache

# Function to crawl Wikipedia for a given topic
def search_topic(query):
    try:
        results = [result for result in search(query) if result]

        if not results:
            print(f"No articles found for '{query}'.")
            return []

        return results

    except DisambiguationError as e:
        print(f"Disambiguation error: {e}")
        return []
    except PageError as e:
        print(f"Page error: {e}")
        return []

# Function to get the summary of the crawled articles
@ttl_lru_cache(ttl=3600, max_size=128)
def get_summary(title):
    try:
        return summary(title)

    except DisambiguationError as e:
        print(f"Disambiguation error for '{title}': {e}")
        return "Disambiguation error — try a more specific title."
    except PageError:
        return "Page not found."
    except Exception as e:
        print(f"Unexpected error for '{title}': {e}")
        return "Summary not available."

# Base function to get page object
def get_page(title):
    try:
        return page(title)

    except Exception as e:
        print(f"Error fetching full page for '{title}': {e}")
        return None

# Function to get full content of the crawled articles
@ttl_lru_cache(ttl=3600, max_size=128)
def get_page_content(title):
    p = get_page(title)
    if p is None:
        return "Full page not available."
    try:
        return p.content
    except Exception as e:
        print(f"Error fetching content for '{title}': {e}")
        return "Full page not available."

# Function to get links from the crawled articles
@ttl_lru_cache(ttl=3600, max_size=128)
def get_links(title):
    p = get_page(title)
    if p is None:
        return []
    try:
        return p.links
    except Exception as e:
        print(f"Error fetching links for '{title}': {e}")
        return []