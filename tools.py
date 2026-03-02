from crawler import (search_topic, get_summary, get_page_content, get_links,
                     get_page_url)


def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for a given topic.
    Return a list of related article titles.
    Use this first to discover what articles exist on a subject.

    Args:
        query: The search term or topic to look up on Wikipedia.

    Returns:
        A list of related Wikipedia article titles as a string.
    """
    return str(search_topic(query))

def get_article_summary(title: str) -> str:
    """
    Get a short summary of a Wikipedia article by its title.
    Use this to quickly assess whether an article is relevant.

    Args:
        title: The exact Wikipedia article title to summarize.

    Returns:
        A short summary of the article as a string.
    """
    return get_summary(title)

def get_article_content(title: str) -> str:
    """
    Get the full text content of a Wikipedia article by its title.
    Use this when the summary is relevant and you need deeper information.

    Args:
        title: The exact Wikipedia article title to retrieve in full.

    Returns:
        The full article text as a string.
    """
    return get_page_content(title)

def get_article_links(title: str) -> str:
    """
    Get all internal Wikipedia links found within an article.
    Use this to discover related topics worth exploring.

    Args:
        title: The exact Wikipedia article title to retrieve links from.

    Returns:
        A list of linked Wikipedia article titles as a string.
    """
    return str(get_links(title))

def get_article_url(title: str) -> str:
    """
    Get the URL of the Wikipedia article.
    Use this to extract the page's URL when a relevant article is found.

    Args:
        title: The exact Wikipedia article title to retrieve URL from.

    Returns:
        Article's URL as a string.
    """
    return get_page_url(title)

# List of tools for Ollama
TOOLS = [
    search_wikipedia,
    get_article_summary,
    get_article_content,
    get_article_links,
    get_article_url
    ]

# Map tool name to function definition
available_functions = {
    "search_wikipedia": search_wikipedia,
    "get_article_summary": get_article_summary,
    "get_article_content": get_article_content,
    "get_article_links": get_article_links,
    "get_article_url": get_article_url
}
