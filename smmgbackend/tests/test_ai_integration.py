import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.features.v1.ai_integration import prompts, schema as ai_schema, service as ai_service
from app.providers import ai_chat


class AiIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def test_placeholder_key_detection(self):
        self.assertTrue(ai_chat._is_placeholder_api_key(None))
        self.assertTrue(ai_chat._is_placeholder_api_key(""))
        self.assertTrue(ai_chat._is_placeholder_api_key("mock_key"))
        self.assertTrue(ai_chat._is_placeholder_api_key("your_api_key"))
        self.assertTrue(ai_chat._is_placeholder_api_key("placeholder_key"))
        self.assertTrue(ai_chat._is_placeholder_api_key("dummy"))
        self.assertFalse(ai_chat._is_placeholder_api_key("AIzaSyD-validKey1234567890abcdefghijklm"))
        self.assertFalse(ai_chat._is_placeholder_api_key("AQ.validKey1234567890abcdefghijklm"))

    async def test_generate_chat_response_placeholder_raises_provider_not_configured(self):
        with patch.object(ai_chat.settings, "AI_GOOGLE_API_KEY", "mock_placeholder_key"):
            with self.assertRaises(ai_chat.AiProviderError) as ctx:
                await ai_chat.generate_chat_response(
                    system_prompt="Test",
                    history=[],
                    user_message="Hello",
                )
            self.assertEqual(ctx.exception.code, "provider_not_configured")

    async def test_generate_chat_response_dev_fallback_on_api_error(self):
        with (
            patch.object(ai_chat.settings, "AI_GOOGLE_API_KEY", "AIzaSyD_fake_key"),
            patch.object(ai_chat.settings, "ENVIRONMENT", "development"),
            patch("app.providers.ai_chat.ChatGoogleGenerativeAI.ainvoke", side_effect=Exception("401 Unauthorized")),
        ):
            with self.assertRaises(ai_chat.AiProviderError) as ctx:
                await ai_chat.generate_chat_response(
                    system_prompt="Test",
                    history=[],
                    user_message="Hello",
                )
            self.assertEqual(ctx.exception.code, "provider_not_configured")

    async def test_send_user_message_uses_unconfigured_response_in_dev(self):
        db = AsyncMock()
        user = SimpleNamespace(id="user-1", name="Test User")
        session = SimpleNamespace(id="sess-1", user_id="user-1", title="Test Chat")
        user_msg = SimpleNamespace(id="msg-1", session_id="sess-1", role="user", content="What to do for a minor burn?")
        assistant_msg = SimpleNamespace(
            id="msg-2",
            session_id="sess-1",
            role="assistant",
            content="First-Aid Guidance for Minor (First-Degree) Burns",
            created_at="2026-09-03T08:00:00Z",
        )

        with (
            patch.object(ai_service.ai_repository, "get_session_by_id", AsyncMock(return_value=session)),
            patch.object(ai_service.ai_repository, "create_message", AsyncMock(side_effect=[user_msg, assistant_msg])) as create_msg,
            patch.object(ai_service.ai_repository, "touch_session_title", AsyncMock()),
            patch.object(ai_service.ai_repository, "get_recent_messages", AsyncMock(return_value=[])),
            patch.object(
                ai_service,
                "generate_chat_response",
                AsyncMock(side_effect=ai_chat.AiProviderError("Unconfigured", code="provider_not_configured")),
            ),
        ):
            result = await ai_service.send_user_message(
                db, user, "sess-1", ai_schema.AIChatMessageCreate(content="What to do for a minor burn?")
            )

        self.assertEqual(result.id, "msg-2")
        self.assertEqual(create_msg.await_count, 2)
        # Verify second call is assistant message with first aid content
        second_call_kwargs = create_msg.await_args_list[1].kwargs
        self.assertEqual(second_call_kwargs["role"], "assistant")
        self.assertIn("First-Aid Guidance for Minor", second_call_kwargs["content"])

    def test_unconfigured_response_guidance(self):
        emergency_reply = prompts.get_unconfigured_response("I have severe chest pain")
        self.assertIn("911", emergency_reply)

        burn_reply = prompts.get_unconfigured_response("I got a hot water burn on my finger")
        self.assertIn("running water", burn_reply)

        fever_reply = prompts.get_unconfigured_response("My temperature is high and I have a fever")
        self.assertIn("fluids", fever_reply)

        headache_reply = prompts.get_unconfigured_response("I have a throbbing headache")
        self.assertIn("darkened", headache_reply)

        sprain_reply = prompts.get_unconfigured_response("I twisted my ankle and have a sprain")
        self.assertIn("R.I.C.E.", sprain_reply)

        unknown_reply = prompts.get_unconfigured_response("Can you write a python script for a game?")
        self.assertIn("I'm sorry, I don't have knowledge about that", unknown_reply)


if __name__ == "__main__":
    unittest.main()
