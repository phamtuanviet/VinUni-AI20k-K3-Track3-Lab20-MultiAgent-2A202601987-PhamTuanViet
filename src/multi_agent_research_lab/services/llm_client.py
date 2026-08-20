"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def complete(
        self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini"
    ) -> LLMResponse:
        """Return a model completion using OpenAI API."""
        from openai import OpenAI
        from tenacity import retry, stop_after_attempt, wait_exponential

        from multi_agent_research_lab.core.config import get_settings
        
        settings = get_settings()
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env file")
            
        client = OpenAI(api_key=api_key)

        from typing import Any
        
        @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
        def _call_openai() -> Any:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
            )
            return response

        response = _call_openai()
        
        content = response.choices[0].message.content or ""
        input_tokens = response.usage.prompt_tokens if response.usage else None
        output_tokens = response.usage.completion_tokens if response.usage else None
        
        # Estimate cost (approximate for gpt-4o-mini)
        cost = 0.0
        if input_tokens and output_tokens:
            cost = (input_tokens / 1000000) * 0.15 + (output_tokens / 1000000) * 0.60
            
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost
        )
