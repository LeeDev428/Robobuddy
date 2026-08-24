import random
import time
from collections.abc import Callable, Sequence
from typing import Any, Protocol


DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_OPENAI_MODEL = "gpt-5.6-terra"

# Only known conversational models belong here. Safety, transcription, TTS, and
# classification models must never be selected just because their names contain
# words such as "llama" or "openai".
GROQ_CHAT_FALLBACKS = (
    DEFAULT_GROQ_MODEL,
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
)

_NON_CHAT_MODEL_MARKERS = (
    "guard",
    "safeguard",
    "moderation",
    "prompt-guard",
    "whisper",
    "transcription",
    "speech",
    "tts",
    "orpheus",
    "image",
)

_CORE_BEHAVIOR = """
Conversation rules:
- Answer the user's actual question directly and use recent turns for context.
- Sound warm and natural, not robotic or overly excited.
- Keep spoken replies concise, usually two to four sentences, while preserving essential facts.
- Repair obvious speech-transcription mistakes when the intended question is clear.
- If ambiguity could materially change the answer, ask one short clarification question instead of guessing.
- Avoid canned filler or ending every answer with an offer to provide more details.
- Correct false premises politely. Do not invent live or current facts that were not provided.
""".strip()

_CREATOR_CONTEXT = """
Creator information (these facts are authoritative):
- Creator name to say publicly: Lee Torres
- Full name: Lee Rafael Torres
- Title: Software Engineer
- Age: 23
- Location: Calauan, Laguna, Philippines
- Education: PUP Calauan Campus, Laguna
- Facebook: https://www.facebook.com/lee.torres.5496683/
- GitHub: https://github.com/LeeDev428
- LinkedIn: https://www.linkedin.com/in/lee-torres-361168333/
- Website: https://leedev.vercel.app/
- Professional background: A full-stack software engineer with experience across companies and freelance
  projects. He designs, builds, maintains, scales, and improves enterprise applications, systems, mobile apps,
  and websites. His work also includes DevOps, AI, machine learning, and deep learning, delivering real-world
  solutions that are actively used and continuously evolving.

When asked who created, developed, built, made, or programmed RoboBuddy, always identify Lee Torres first.
Only provide the additional profile details relevant to what the user asks.
""".strip()

_CREATOR_IDENTITY_RESPONSE = (
    "I was created and developed by Lee Torres, whose full name is Lee Rafael Torres. "
    "He is a 23-year-old Software Engineer based in Calauan, Laguna, Philippines, and studied at "
    "PUP Calauan Campus. He builds and improves enterprise applications, systems, mobile apps, websites, "
    "and AI and machine-learning solutions."
)

_CREATOR_PROFILE_RESPONSE = (
    "Lee Torres, whose full name is Lee Rafael Torres, is a 23-year-old Software Engineer based in Calauan, "
    "Laguna, Philippines. He studied at PUP Calauan Campus and has experience across companies and freelance "
    "projects. He designs, builds, maintains, scales, and improves enterprise applications, systems, mobile "
    "apps, and websites, with hands-on work in DevOps, AI, machine learning, and deep learning."
)

_CREATOR_SOCIAL_RESPONSE = (
    "You can find Lee Torres on Facebook at https://www.facebook.com/lee.torres.5496683/, on GitHub at "
    "https://github.com/LeeDev428, and on LinkedIn at "
    "https://www.linkedin.com/in/lee-torres-361168333/. His website is https://leedev.vercel.app/."
)


def creator_response(user_text: str) -> str | None:
    """Return authoritative local creator details for clear creator questions."""
    normalized = " ".join(user_text.lower().replace("'", " ").split())
    creator_reference = any(
        marker in normalized
        for marker in (
            "your creator",
            "your developer",
            "your programmer",
            "lee torres",
            "lee rafael torres",
            "creator of robobuddy",
            "developer of robobuddy",
        )
    )
    identity_question = any(
        phrase in normalized
        for phrase in (
            "who created you",
            "who developed you",
            "who built you",
            "who made you",
            "who programmed you",
            "who created robobuddy",
            "who developed robobuddy",
            "who built robobuddy",
            "who made robobuddy",
            "who programmed robobuddy",
        )
    )

    if creator_reference and any(
        social in normalized for social in ("facebook", "github", "linkedin", "website", "social")
    ):
        return _CREATOR_SOCIAL_RESPONSE
    if identity_question:
        return _CREATOR_IDENTITY_RESPONSE
    if creator_reference and any(
        phrase in normalized
        for phrase in ("who is", "tell me about", "information", "background", "what does")
    ):
        return _CREATOR_PROFILE_RESPONSE
    return None


class ConversationAIError(RuntimeError):
    """Raised when no configured conversational provider can answer."""


class ChatProvider(Protocol):
    """Minimal provider contract used by the conversation coordinator."""

    name: str
    model: str

    def generate(
        self,
        system_prompt: str,
        messages: Sequence[dict[str, str]],
        max_output_tokens: int,
    ) -> str:
        """Return a text response for the supplied conversation."""


def is_chat_model(model_id: str) -> bool:
    """Reject model IDs that are clearly specialized non-chat models."""
    normalized = model_id.strip().lower()
    return bool(normalized) and not any(marker in normalized for marker in _NON_CHAT_MODEL_MARKERS)


def _unique_chat_models(primary_model: str) -> list[str]:
    candidates = (primary_model, *GROQ_CHAT_FALLBACKS)
    return list(dict.fromkeys(model.strip() for model in candidates if is_chat_model(model)))


def _status_code(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status

    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


def _is_transient_error(exc: Exception) -> bool:
    status = _status_code(exc)
    if status in {408, 409, 429} or (status is not None and status >= 500):
        return True

    error_text = str(exc).lower()
    return any(
        marker in error_text
        for marker in ("timed out", "timeout", "connection error", "connection reset", "temporarily unavailable")
    )


def _can_try_another_model(exc: Exception) -> bool:
    status = _status_code(exc)
    if status in {400, 403, 404, 408, 409, 429} or (status is not None and status >= 500):
        return True

    error_text = str(exc).lower()
    return any(
        marker in error_text
        for marker in (
            "model",
            "permission",
            "decommission",
            "single user message",
            "text classification",
            "temporarily unavailable",
        )
    )


def _call_with_retries(
    operation: Callable[[], Any],
    retries: int,
    base_delay_sec: float = 0.25,
) -> Any:
    """Retry only transient failures, with a short jittered backoff."""
    retries = max(0, retries)
    for attempt in range(retries + 1):
        try:
            return operation()
        except Exception as exc:
            if attempt >= retries or not _is_transient_error(exc):
                raise
            delay = base_delay_sec * (2**attempt) + random.uniform(0.0, 0.1)
            time.sleep(delay)

    raise RuntimeError("Retry loop ended unexpectedly.")


class GroqChatProvider:
    """Groq Chat Completions provider with chat-only model failover."""

    name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_GROQ_MODEL,
        timeout_sec: float = 20.0,
        retries: int = 2,
        client: Any | None = None,
    ) -> None:
        if not api_key and client is None:
            raise ValueError("GROQ_API_KEY is missing.")

        if client is None:
            from groq import Groq

            client = Groq(
                api_key=api_key,
                timeout=max(1.0, timeout_sec),
                max_retries=0,
            )

        self._client = client
        self._models = _unique_chat_models(model)
        if not self._models:
            raise ValueError("GROQ_MODEL must identify a conversational text model.")
        self._retries = max(0, retries)
        self.model = self._models[0]

    def generate(
        self,
        system_prompt: str,
        messages: Sequence[dict[str, str]],
        max_output_tokens: int,
    ) -> str:
        request_messages = [{"role": "system", "content": system_prompt}, *messages]
        failures: list[str] = []

        for model in self._models:
            try:
                response = _call_with_retries(
                    lambda: self._client.chat.completions.create(
                        model=model,
                        messages=request_messages,
                        temperature=0.2,
                        max_tokens=max_output_tokens,
                    ),
                    retries=self._retries,
                )
                text = (response.choices[0].message.content or "").strip()
                if not text:
                    raise RuntimeError("The model returned an empty response.")
                self.model = model
                if self._models[0] != model:
                    self._models.remove(model)
                    self._models.insert(0, model)
                return text
            except Exception as exc:
                failures.append(f"{model}: {exc}")
                if not _can_try_another_model(exc):
                    break

        raise ConversationAIError("Groq could not answer. " + " | ".join(failures))


class OpenAIChatProvider:
    """OpenAI Responses API provider."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_OPENAI_MODEL,
        timeout_sec: float = 20.0,
        retries: int = 2,
        client: Any | None = None,
    ) -> None:
        if not api_key and client is None:
            raise ValueError("OPENAI_API_KEY is missing.")
        if not is_chat_model(model):
            raise ValueError("OPENAI_MODEL must identify a conversational text model.")

        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise ValueError(
                    "The OpenAI provider needs the 'openai' package. Run: pip install -r requirements.txt"
                ) from exc

            client = OpenAI(
                api_key=api_key,
                timeout=max(1.0, timeout_sec),
                max_retries=0,
            )

        self._client = client
        self._retries = max(0, retries)
        self.model = model.strip()

    def generate(
        self,
        system_prompt: str,
        messages: Sequence[dict[str, str]],
        max_output_tokens: int,
    ) -> str:
        response = _call_with_retries(
            lambda: self._client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=list(messages),
                max_output_tokens=max_output_tokens,
            ),
            retries=self._retries,
        )
        text = (response.output_text or "").strip()
        if not text:
            raise ConversationAIError("OpenAI returned an empty response.")
        return text


class ConversationAI:
    """Provider-neutral, bounded, failure-safe conversation coordinator."""

    def __init__(
        self,
        api_key: str = "",
        system_prompt: str = "You are RoboBuddy, a friendly educational AI companion robot.",
        *,
        provider: str = "auto",
        groq_model: str = DEFAULT_GROQ_MODEL,
        openai_api_key: str = "",
        openai_model: str = DEFAULT_OPENAI_MODEL,
        timeout_sec: float = 20.0,
        retries: int = 2,
        max_output_tokens: int = 240,
        history_turns: int = 8,
        providers: Sequence[ChatProvider] | None = None,
    ) -> None:
        base_prompt = system_prompt.strip() or "You are RoboBuddy, a friendly educational AI companion robot."
        self._system_prompt = f"{base_prompt}\n\n{_CORE_BEHAVIOR}\n\n{_CREATOR_CONTEXT}"
        self._max_output_tokens = max(64, max_output_tokens)
        self._history_turns = max(1, history_turns)
        self._messages: list[dict[str, str]] = []

        if providers is None:
            self._providers = self._build_providers(
                provider=provider,
                groq_api_key=api_key,
                groq_model=groq_model,
                openai_api_key=openai_api_key,
                openai_model=openai_model,
                timeout_sec=timeout_sec,
                retries=retries,
            )
        else:
            self._providers = list(providers)

        if not self._providers:
            raise ValueError(
                "No AI provider is configured. Set GROQ_API_KEY or OPENAI_API_KEY in .env."
            )
        self._active_provider = self._providers[0]

    @staticmethod
    def _build_providers(
        *,
        provider: str,
        groq_api_key: str,
        groq_model: str,
        openai_api_key: str,
        openai_model: str,
        timeout_sec: float,
        retries: int,
    ) -> list[ChatProvider]:
        selected = provider.strip().lower() or "auto"
        if selected not in {"auto", "groq", "openai"}:
            raise ValueError("AI_PROVIDER must be one of: auto, groq, openai.")

        providers: list[ChatProvider] = []
        if selected in {"auto", "openai"} and openai_api_key:
            providers.append(
                OpenAIChatProvider(
                    api_key=openai_api_key,
                    model=openai_model,
                    timeout_sec=timeout_sec,
                    retries=retries,
                )
            )
        if selected in {"auto", "groq"} and groq_api_key:
            providers.append(
                GroqChatProvider(
                    api_key=groq_api_key,
                    model=groq_model,
                    timeout_sec=timeout_sec,
                    retries=retries,
                )
            )

        if selected == "openai" and not openai_api_key:
            raise ValueError("AI_PROVIDER=openai requires OPENAI_API_KEY.")
        if selected == "groq" and not groq_api_key:
            raise ValueError("AI_PROVIDER=groq requires GROQ_API_KEY.")
        return providers

    @property
    def provider(self) -> str:
        return self._active_provider.name

    @property
    def model(self) -> str:
        return self._active_provider.model

    @property
    def label(self) -> str:
        return f"{self.provider}:{self.model}"

    @property
    def history(self) -> tuple[dict[str, str], ...]:
        """Return a defensive copy for diagnostics and tests."""
        return tuple(message.copy() for message in self._messages)

    def reset(self) -> None:
        """Start a fresh conversation without recreating API clients."""
        self._messages.clear()

    def ask(self, user_text: str) -> str:
        cleaned_user_text = user_text.strip()
        if not cleaned_user_text:
            raise ValueError("The user message is empty.")

        local_response = creator_response(cleaned_user_text)
        if local_response is not None:
            self._commit_turn(cleaned_user_text, local_response)
            return local_response

        # Do not mutate stored history until a provider returns successfully.
        request_messages = [*self._messages, {"role": "user", "content": cleaned_user_text}]
        failures: list[str] = []

        for provider in self._providers:
            try:
                response_text = provider.generate(
                    system_prompt=self._system_prompt,
                    messages=request_messages,
                    max_output_tokens=self._max_output_tokens,
                )
            except Exception as exc:
                failures.append(f"{provider.name}: {exc}")
                continue

            normalized = " ".join(response_text.split())
            if not normalized:
                failures.append(f"{provider.name}: empty response")
                continue

            self._active_provider = provider
            if self._providers[0] is not provider:
                self._providers.remove(provider)
                self._providers.insert(0, provider)
            self._commit_turn(cleaned_user_text, normalized)
            return normalized

        raise ConversationAIError("All AI providers failed. " + " | ".join(failures))

    def _commit_turn(self, user_text: str, response_text: str) -> None:
        self._messages.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": response_text},
            ]
        )
        self._trim_history()

    def _trim_history(self) -> None:
        max_messages = self._history_turns * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]
