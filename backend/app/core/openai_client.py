import os
from openai import OpenAI, OpenAIError # Import OpenAIError for explicit error handling
from dotenv import load_dotenv
from typing import List, Dict, Union, Any # For message typing

# Load environment variables from .env file in the project root
# This path needs to be correct relative to where the application is run from,
# or an absolute path should be used if discoverability is an issue.
# For tests, this might be mocked or the .env file placed appropriately.
# Assuming the .env is at /home/ubuntu/NowGo-LLM/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path=dotenv_path)

def get_openai_client() -> OpenAI | None:
    """Creates and returns an OpenAI client instance if API key is available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables. Please set it in .env file in the project root.")
        return None
    return OpenAI(api_key=api_key)

async def get_chat_completion(prompt: Union[str, List[Dict[str, str]]], model: str = "gpt-4-turbo") -> str | None:
    """Get a chat completion from OpenAI API."""
    client = get_openai_client()
    if not client:
        print("Error: OpenAI client could not be initialized. API key missing or invalid.")
        return None

    messages: List[Dict[str, str]]
    if isinstance(prompt, str):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    elif isinstance(prompt, list):
        messages = prompt # Assume it's already a list of message dicts
    else:
        print("Error: Invalid prompt type. Must be a string or a list of message dictionaries.")
        return None

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages # type: ignore <- OpenAI SDK expects List[ChatCompletionMessageParam]
        )
        return response.choices[0].message.content
    except OpenAIError as e: # Catch specific OpenAI errors
        print(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while calling OpenAI API: {e}")
        return None

async def test_openai_connection() -> bool:
    """Test the connection to OpenAI API with a simple prompt."""
    print("Testing OpenAI API connection...")
    # Use a very simple prompt for testing connection
    response_content = await get_chat_completion("Hello, OpenAI! This is a connection test.")
    if response_content:
        print(f"OpenAI Test Response: {response_content[:100]}...") # Print a snippet
        return True
    else:
        print("Failed to get response from OpenAI during connection test.")
        return False

# Example of how to run the test (you would typically call this from another part of your app)
# if __name__ == "__main__":
#     import asyncio
#     # Ensure .env is in the root of NowGo-LLM for this to work directly
#     # Example: /home/ubuntu/NowGo-LLM/.env
#     asyncio.run(test_openai_connection())

