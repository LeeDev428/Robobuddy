from typing import List

from groq import Groq


PREFERRED_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-4-maverick-17b-128e-instruct",
    "llama-4-scout-17b-16e-instruct",
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
            model_ids = [m.id for m in self._client.models.list().data]

            # 1) Prefer hand-picked strong models if available.
            for candidate in PREFERRED_GROQ_MODELS:
                if candidate in model_ids:
                    return candidate

            # 2) Otherwise score available text models and pick the best one.
            def is_text_model(model_id: str) -> bool:
                lower = model_id.lower()
                if any(x in lower for x in ["whisper", "tts", "speech", "vision", "image", "sdxl"]):
                    return False
                return any(
                    x in lower
                    for x in ["llama", "deepseek", "qwen", "mistral", "mixtral", "gemma"]
                )

            def score(model_id: str) -> int:
                lower = model_id.lower()
                value = 0
                if "r1" in lower or "reason" in lower:
                    value += 150
                if "405b" in lower:
                    value += 450
                if "70b" in lower:
                    value += 350
                if "llama-4" in lower:
                    value += 300
                if "llama-3.3" in lower:
                    value += 220
                if "versatile" in lower:
                    value += 120
                if "instant" in lower:
                    value -= 180
                return value

            text_models = [mid for mid in model_ids if is_text_model(mid)]
            if text_models:
                return max(text_models, key=score)
        except Exception:
            pass

        return PREFERRED_GROQ_MODELS[0]

    def ask(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._messages,
            temperature=0.0,
            max_tokens=140,
        )

        ai_text = response.choices[0].message.content or "I am here with you."
        self._messages.append({"role": "assistant", "content": ai_text})
        return ai_text
