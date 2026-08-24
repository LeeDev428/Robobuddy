import unittest
from types import SimpleNamespace

from ai_robot.conversation_ai import (
    DEFAULT_GROQ_MODEL,
    ConversationAI,
    ConversationAIError,
    GroqChatProvider,
    OpenAIChatProvider,
    _unique_chat_models,
)


class FakeProvider:
    def __init__(self, name: str, response: str | None = None, error: Exception | None = None) -> None:
        self.name = name
        self.model = f"{name}-model"
        self.response = response
        self.error = error
        self.calls: list[list[dict[str, str]]] = []
        self.system_prompts: list[str] = []

    def generate(self, system_prompt, messages, max_output_tokens):
        self.system_prompts.append(system_prompt)
        self.calls.append([message.copy() for message in messages])
        if self.error is not None:
            raise self.error
        return self.response or ""


class FakeBadRequest(RuntimeError):
    status_code = 400


class ConversationAITests(unittest.TestCase):
    def test_direct_creator_question_is_answered_locally_and_authoritatively(self) -> None:
        provider = FakeProvider("fake", error=RuntimeError("must not be called"))
        ai = ConversationAI(system_prompt="Test", providers=[provider])

        answer = ai.ask("Who created and developed you?")

        self.assertTrue(answer.startswith("I was created and developed by Lee Torres"))
        self.assertIn("Lee Rafael Torres", answer)
        self.assertEqual(provider.calls, [])
        self.assertEqual(len(ai.history), 2)

    def test_creator_social_links_are_answered_locally(self) -> None:
        provider = FakeProvider("fake", error=RuntimeError("must not be called"))
        ai = ConversationAI(system_prompt="Test", providers=[provider])

        answer = ai.ask("What is your creator's GitHub and website?")

        self.assertIn("https://github.com/LeeDev428", answer)
        self.assertIn("https://leedev.vercel.app/", answer)
        self.assertEqual(provider.calls, [])

    def test_provider_always_receives_creator_context(self) -> None:
        provider = FakeProvider("fake", response="Hello")
        ai = ConversationAI(system_prompt="Test", providers=[provider])

        ai.ask("Hello")

        self.assertIn("Lee Rafael Torres", provider.system_prompts[0])
        self.assertIn("https://github.com/LeeDev428", provider.system_prompts[0])

    def test_classifier_models_are_never_candidates(self) -> None:
        candidates = _unique_chat_models("meta-llama/llama-prompt-guard-2-22m")

        self.assertEqual(candidates[0], DEFAULT_GROQ_MODEL)
        self.assertFalse(any("guard" in model for model in candidates))

    def test_failed_turn_does_not_pollute_history(self) -> None:
        provider = FakeProvider("broken", error=RuntimeError("offline"))
        ai = ConversationAI(system_prompt="Test", providers=[provider])

        with self.assertRaises(ConversationAIError):
            ai.ask("Will this be stored?")

        self.assertEqual(ai.history, ())

    def test_provider_failover_commits_only_successful_turn(self) -> None:
        primary = FakeProvider("primary", error=RuntimeError("unavailable"))
        fallback = FakeProvider("fallback", response="  Jupiter is the largest planet.  ")
        ai = ConversationAI(system_prompt="Test", providers=[primary, fallback])

        answer = ai.ask("Which planet is largest?")

        self.assertEqual(answer, "Jupiter is the largest planet.")
        self.assertEqual(ai.provider, "fallback")
        self.assertEqual(len(ai.history), 2)

        ai.ask("And what is it made of?")
        self.assertEqual(len(primary.calls), 1)
        self.assertEqual(len(fallback.calls), 2)

    def test_history_is_bounded_to_recent_turns(self) -> None:
        provider = FakeProvider("fake", response="Answer")
        ai = ConversationAI(system_prompt="Test", history_turns=2, providers=[provider])

        ai.ask("First")
        ai.ask("Second")
        ai.ask("Third")

        self.assertEqual(len(ai.history), 4)
        self.assertNotIn("First", [message["content"] for message in ai.history])
        self.assertEqual(provider.calls[-1][-1]["content"], "Third")

    def test_groq_falls_back_after_model_specific_400(self) -> None:
        calls: list[str] = []

        def create(**kwargs):
            calls.append(kwargs["model"])
            if kwargs["model"] == "custom/chat-model":
                raise FakeBadRequest("model is unavailable")
            message = SimpleNamespace(content="Fallback worked")
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        provider = GroqChatProvider(
            api_key="",
            model="custom/chat-model",
            retries=0,
            client=client,
        )

        answer = provider.generate("Test", [{"role": "user", "content": "Hello"}], 100)

        self.assertEqual(answer, "Fallback worked")
        self.assertEqual(calls[:2], ["custom/chat-model", DEFAULT_GROQ_MODEL])

        provider.generate("Test", [{"role": "user", "content": "Again"}], 100)
        self.assertEqual(calls[-1], DEFAULT_GROQ_MODEL)

    def test_openai_provider_uses_responses_api(self) -> None:
        captured = {}

        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text="OpenAI worked")

        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        provider = OpenAIChatProvider(api_key="", model="test-chat", retries=0, client=client)

        answer = provider.generate("Be helpful", [{"role": "user", "content": "Hello"}], 120)

        self.assertEqual(answer, "OpenAI worked")
        self.assertEqual(captured["instructions"], "Be helpful")
        self.assertEqual(captured["max_output_tokens"], 120)


if __name__ == "__main__":
    unittest.main()
