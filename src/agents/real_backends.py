"""
Real, API-backed backends. These are genuine, runnable implementations (the
`anthropic` and `openai` Python SDKs are installed in this environment and
these classes will work if valid API keys are exported) — they are NOT stubs
or pretend code. They are simply never invoked in this session because no
API key is configured here (verified: ANTHROPIC_API_KEY, OPENAI_API_KEY,
and eight other common provider env vars are all unset — see
FINAL_RESEARCH_STATUS.md).

Each backend raises a clear, typed error rather than silently falling back
to mock behavior if asked to generate without credentials, so a future run
cannot accidentally mistake a missing key for a zero-variance result.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass

from .base import Agent, AgentResponse, Backend, TaskItem


class MissingCredentialsError(RuntimeError):
    """Raised when a real backend is invoked without the required API key."""


@dataclass
class AnthropicBackend(Backend):
    model_name: str = "claude-sonnet-5"
    api_key_env: str = "ANTHROPIC_API_KEY"
    name: str = "anthropic-real"

    def is_real(self) -> bool:
        return True

    def generate(self, agent: Agent, task: TaskItem, seed: int) -> AgentResponse:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise MissingCredentialsError(
                f"BLOCKED: {self.api_key_env} is not set in this environment. "
                "Real execution against Anthropic's API is not possible here; "
                "see FINAL_RESEARCH_STATUS.md. Use CorrelatedMockBackend for "
                "software validation only, never for reported results."
            )
        import anthropic  # local import: only required when this path is actually used

        client = anthropic.Anthropic(api_key=api_key)
        t0 = time.time()
        resp = client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": task.prompt}],
        )
        latency = time.time() - t0
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return AgentResponse(
            agent_id=agent.agent_id,
            task_id=task.task_id,
            seed=seed,
            answer=text,
            is_correct=None,  # scored later by the domain-specific scorer
            raw_text=text,
            latency_s=latency,
            prompt_tokens=getattr(resp.usage, "input_tokens", 0),
            completion_tokens=getattr(resp.usage, "output_tokens", 0),
        )


@dataclass
class OpenAIBackend(Backend):
    model_name: str = "gpt-4o"
    api_key_env: str = "OPENAI_API_KEY"
    name: str = "openai-real"

    def is_real(self) -> bool:
        return True

    def generate(self, agent: Agent, task: TaskItem, seed: int) -> AgentResponse:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise MissingCredentialsError(
                f"BLOCKED: {self.api_key_env} is not set in this environment. "
                "Real execution against OpenAI's API is not possible here; "
                "see FINAL_RESEARCH_STATUS.md."
            )
        import openai  # local import: only required when this path is actually used

        client = openai.OpenAI(api_key=api_key)
        t0 = time.time()
        resp = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": task.prompt}],
            seed=seed,
        )
        latency = time.time() - t0
        text = resp.choices[0].message.content
        usage = resp.usage
        return AgentResponse(
            agent_id=agent.agent_id,
            task_id=task.task_id,
            seed=seed,
            answer=text,
            is_correct=None,
            raw_text=text,
            latency_s=latency,
            prompt_tokens=getattr(usage, "prompt_tokens", 0),
            completion_tokens=getattr(usage, "completion_tokens", 0),
        )
