import os
import json

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, dispatch_tool


load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a Wikipedia research assistant. When given a topic, your job is to:

1. Use search_topic to find relevant articles.
2. Use get_summary on each article found.
3. Compile your findings and return them as a JSON object with the following structure:

{
    "topic": "the original search topic",
    "articles": [
        {
            "title": "Article Title",
            "summary": "A concise 2-3 sentence summary of the article."
        }
    ]
}

Return ONLY the JSON object, no additional text or explanation.
Be thorough — include all relevant articles found, not just the first one."""


def parse_agent_response(response_text):
    try:
        # Strip markdown code fences if present
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        print(f"Failed to parse agent response as JSON: {e}")
        return {}

def run_agent(user_query, max_iterations=10):
    messages = [{"role": "user", "content": user_query}]

    print(f"\n>>> Starting agent for query: '{user_query}'\n")

    for iteration in range(max_iterations):
        print(f"--- Iteration {iteration + 1} ---")

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    result = parse_agent_response(block.text)
                    if result:
                        save_articles(result)
                    return result
            return {}

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"Tool called: {block.name} | Input: {block.input}")
                    result = dispatch_tool(block.name, block.input)
                    print(f"Tool result preview: {str(result)[:120]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

    return {}


if __name__ == "__main__":
    query = input("What would you like to research? ")
    articles = run_agent(query)

    if articles:
        print("\n=== RESULTS ===")
        for article in articles.get("articles", []):
            print(f"\n• {article['title']}")
            print(f"  {article['summary']}")
