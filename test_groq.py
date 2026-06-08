import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY", "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")
print(f"Testing Key: {key[:10]}...{key[-5:]}")

try:
    client = Groq(api_key=key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say hello in 3 words.",
            }
        ],
        model="llama-3.1-8b-instant",
    )
    print("RESPONSE:", chat_completion.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
