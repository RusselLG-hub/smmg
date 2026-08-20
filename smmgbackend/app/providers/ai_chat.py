from collections.abc import Sequence
import re

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class AiProviderError(Exception):
    def __init__(self, message: str, *, code: str = "provider_error"):
        self.code = code
        super().__init__(message)


def _content_as_text(message: AIMessage) -> str:
    if isinstance(message.content, str):
        return message.content.strip()
    return "\n".join(
        str(block.get("text", "")) if isinstance(block, dict) else str(block)
        for block in message.content
    ).strip()


def _normalize_plain_text(content: str) -> str:
    content = content.replace("**", "").replace("__", "")
    content = re.sub(r"(?m)^\s*#{1,6}\s+", "", content)
    content = re.sub(r"(?m)^\s*[*+]\s+", "- ", content)
    content = content.replace("```", "").replace("`", "")
    return content.strip()


async def generate_chat_response(
    *,
    system_prompt: str,
    history: Sequence[tuple[str, str]],
    user_message: str,
) -> str:
    """Generate a chat response through the configured LangChain provider."""
    if not settings.AI_GOOGLE_API_KEY or settings.AI_GOOGLE_API_KEY.startswith("mock"):
        raise AiProviderError(
            "AI chat is not configured", code="provider_not_configured"
        )

    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    for role, content in history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_message))

    try:
        model = ChatGoogleGenerativeAI(
            google_api_key=settings.AI_GOOGLE_API_KEY,
            model=settings.AI_MODEL,
            temperature=settings.AI_TEMPERATURE,
            max_output_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            request_timeout=settings.AI_REQUEST_TIMEOUT_SECONDS,
        )
        response = await model.ainvoke(messages)
    except Exception as exc:
        raise AiProviderError("The AI assistant is temporarily unavailable") from exc

    if not isinstance(response, AIMessage):
        raise AiProviderError("AI provider returned an invalid response")

    content = _normalize_plain_text(_content_as_text(response))
    if not content:
        raise AiProviderError("AI provider returned an empty response")
    return content
