from crawler import search_topic, get_summary, get_page_content, get_links

# Tools definition according to Anthropic's documentation in JSON format
TOOLS = [
    {
        "name": "search_topic",
        "description": (
            "Search Wikipedia for a given query and return a list of related article titles. "
            "Use this first to discover what articles exist on a subject before fetching content. "
            "Returns: a list of strings, each being a Wikipedia article title."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search term or topic to look up on Wikipedia."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_summary",
        "description": (
            "Fetch a short summary of a Wikipedia article by its exact title. "
            "Use this to quickly assess whether an article is relevant before fetching the full page. "
            "Returns: a string containing the article summary, or an error message if unavailable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact Wikipedia article title to summarize."
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_page_content",
        "description": (
            "Fetch the full text content of a Wikipedia article by its exact title. "
            "Use this when the summary is relevant and you need deeper information. "
            "Returns: a string containing the full article text, or an error message if unavailable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact Wikipedia article title to retrieve in full."
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_links",
        "description": (
            "Fetch all internal Wikipedia links found within an article by its exact title. "
            "Use this to discover related topics and decide where to explore next. "
            "Returns: a list of strings, each being a linked Wikipedia article title."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact Wikipedia article title to retrieve links from."
                }
            },
            "required": ["title"]
        }
    }
]

# Function to map tools with corresponding crawler function
def dispatch_tool(tool_name, tool_input):
    if tool_name == "search_topic":
        result = search_topic(tool_input["query"])
        return str(result)

    elif tool_name == "get_summary":
        result = get_summary(tool_input["title"])
        return str(result)

    elif tool_name == "get_page_content":
        result = get_page_content(tool_input["title"])
        return str(result)

    elif tool_name == "get_links":
        result = get_links(tool_input["title"])
        return str(result)

    else:
        return f"Unknown tool: {tool_name}"
