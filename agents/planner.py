import json
import os
from groq import Groq


class PlannerAgent:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")

        self.client = Groq(api_key=api_key)

    def plan(self, user_query):

        prompt = f"""
You are the Planner Agent in an e-commerce multi-agent system.

Your task is to understand the user's product request and convert it
into structured requirements.

Extract the following fields:

- category
- max_price
- min_ram_gb
- min_storage_gb
- min_rating

If a value is not mentioned, use null.

Return ONLY valid JSON in exactly this format:

{{
    "category": "...",
    "max_price": null,
    "min_ram_gb": null,
    "min_storage_gb": null,
    "min_rating": null
}}

User query:
{user_query}
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code fences if the LLM returns them
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        requirements = json.loads(content)

        return requirements