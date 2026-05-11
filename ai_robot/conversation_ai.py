from typing import List

from groq import Groq


PREFERRED_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


class ConversationAI:
    """Small conversation client for Groq chat completions."""

    def __init__(self, api_key: str, system_prompt: str) -> None:
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Set it in your environment.")

        self._client = Groq(api_key=api_key)
        self._model = self._resolve_model()
        self._messages: List[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    @property
    def model(self) -> str:
        return self._model

    def _resolve_model(self) -> str:
        # API usage always needs a model; chat UIs simply hide this choice.
        try:
            available = {m.id for m in self._client.models.list().data}
            for candidate in PREFERRED_GROQ_MODELS:
                if candidate in available:
                    return candidate
        except Exception:
            pass

        return PREFERRED_GROQ_MODELS[0]

    def ask(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._messages,
            temperature=0.2,
            max_tokens=220,
        )

        ai_text = response.choices[0].message.content or "I am here with you."
        self._messages.append({"role": "assistant", "content": ai_text})
        return ai_text
