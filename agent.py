import inspect
import json
import os

from ollama import chat, ChatResponse

from tools import TOOLS, available_functions


SYSTEM_PROMPT = """
You are a Wikipedia research assistant.
You MUST use tools to answer.
NEVER respond without first calling search_wikipedia.

When given a topic:
1. ALWAYS start by calling search_wikipedia with the topic.
2. Call get_article_summary for EACH article title returned.
3. Call get_article_url for EACH article title to get the real URL.
4. Only after completing steps 2 and 3 for ALL articles, return the final JSON.
5. Once you have summaries, return ONLY this JSON structure:

{
    "topic": "the original search topic",
    "articles": [
        {
            "title": "Article Title",
            "url": "URL returned by get_article_url",
            "summary": "A concise 2-3 sentence summary."
        }
    ]
}

Return ONLY the JSON. No extra text. Only call one tool at a time.
Never invent summaries or URLs — only use what the tools return.
"""


# Function to sanitize the response
def parse_json_response(response_text: str) -> dict:
    try:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        print(f"Failed to parse response as JSON: {e}")
        return {}

# Function to save result in file
def save_result(user_query, result):
    parent_dir = os.getcwd()
    dir_name = "results"
    path = os.path.join(parent_dir, dir_name)
    os.makedirs(path, exist_ok=True)

    safe_name = user_query.replace(" ", "_").lower()
    file_path = os.path.join(path, f"{safe_name}.json")

    with open(file_path, "w", encoding="UTF-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# Prevents hallucinated argument errors
def call_tool_safely(tool_name: str, tool_args: dict) -> str:
    if tool_name not in available_functions:
        return f"Unknown tool: {tool_name}"

    func = available_functions[tool_name]
    valid_params = inspect.signature(func).parameters
    filtered_args = {k: v for k, v in tool_args.items() if k in valid_params}

    if filtered_args != tool_args:
        hallucinated = set(tool_args) - set(filtered_args)
        print(f"Warning: filtered out hallucinated arguments: {hallucinated}")

    # Check all required arguments are present after filtering
    required_params = [
        name for name, param in valid_params.items()
        if param.default is inspect.Parameter.empty
    ]
    missing_required = [p for p in required_params if p not in filtered_args]
    if missing_required:
        print(f"Warning: missing required arguments {missing_required} for {tool_name}")
        return f"Error: {tool_name} requires {missing_required}. Please call it with the correct arguments."

    return str(func(**filtered_args))

# Main function to feed the model
def run_agent(user_query: str, max_iterations: int = 10) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    print(f"\n>>> Starting agent for query: '{user_query}'\n")

    tools_used = set()

    for iteration in range(max_iterations):
        print(f"--- Iteration {iteration + 1} ---")

        response: ChatResponse = chat(
            model="qwen3:4b",
            messages=messages,
            tools=TOOLS
        )
        messages.append(response.message)

        if response.message.tool_calls:
            for tc in response.message.tool_calls:
                tool_name = tc.function.name
                tool_args = tc.function.arguments

                tools_used.add(tool_name)

                if tool_name in available_functions:
                    result = call_tool_safely(tool_name, tool_args)
                    messages.append(
                        {
                            'role': 'tool',
                            'tool_name': tc.function.name,
                            'content': str(result)
                        }
                    )
        else:
            content = response.message.content.strip()

            if not content:
                print("Model returned empty response — nudging...")
                messages.append({
                    "role": "user",
                    "content": "Please use the search_wikipedia tool to search for the topic first."
                })
                continue

            missing = [
                t for t in ["get_article_summary", "get_article_url"]
                if t not in tools_used
            ]
            if missing:
                print(f"Missing tool calls: {missing} — nudging...")
                messages.append({
                    "role": "user",
                    "content": (
                        f"You have not called {' and '.join(missing)} yet. "
                        "You MUST call get_article_summary ONE AT A TIME, passing a single 'title' string for each article. "
                        "Do not pass lists or multiple titles. Start with the first article title now."
                    )
                })
                continue

            result = parse_json_response(content)
            if result:
                print("Agent finished — valid JSON received.")
                save_result(user_query, result)
                print (result)
                return result

            print("Model responded with text but not JSON — nudging...")
            messages.append({
                "role": "user",
                "content": "You have gathered enough information. Now return the final JSON object as instructed."
            })
            continue

    print("Max iterations reached.")
    return {}

if __name__ == "__main__":
    query = input("What would you like to research? ")
    articles = run_agent(query)
