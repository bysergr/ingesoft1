import requests
import os


def detect_language(user_text: str):
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
                            "text": "Tell me if the text language is in English or in Spanish, if it is in English, please write 'en', if it is in Spanish, please write 'es'.",
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
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

    
    data = response.json()

    return data['choices'][0]['message']['content']