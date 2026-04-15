from typing import List

from groq import Groq


class ConversationAI:
    """Small conversation client for Groq chat completions."""

    def __init__(self, api_key: str, model: str, system_prompt: str) -> None:
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Set it in your environment.")

        self._client = Groq(api_key=api_key)
        self._model = model
        self._messages: List[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    def ask(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._messages,
            temperature=0.6,
            max_tokens=350,
        )

        ai_text = response.choices[0].message.content or "I am here with you."
        self._messages.append({"role": "assistant", "content": ai_text})
        return ai_text
