"""
Language detection module for the Naurat Importation Bot API.

This module provides functionality to detect whether a given text is in English or Spanish
using OpenAI's GPT-4o-mini model.

Features:
- Sends a request to OpenAI's API to determine the language of a given text.
- Returns 'en' for English and 'es' for Spanish.
- Utilizes environment variables for API authentication.

Environment Variables:
- `OPENAI_API_KEY`: The API key required to authenticate requests to OpenAI.
"""

import os
import requests


def detect_language(user_text: str) -> str:
    """
    Detects the language of the given text using OpenAI's GPT-4o-mini model.

    The function queries the OpenAI API to determine whether the provided text is in English ('en')
    or Spanish ('es').

    Args:
        user_text (str): The text whose language needs to be identified.

    Returns:
        str: 'en' if the text is in English, 'es' if the text is in Spanish.

    Raises:
        requests.RequestException: If there is an error in the API request.
        KeyError: If the API response structure is unexpected.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Tell me if the text language is in English or in Spanish, "
                                "if it is in English, please write 'en', if it is in Spanish, please write 'es'.",
                    },
                    {
                        "type": "text",
                        "text": user_text,
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20
    )

    data = response.json()
    return data['choices'][0]['message']['content']
