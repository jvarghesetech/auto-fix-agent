"""Agentic bug-fix loop: point Claude at a repo with failing tests and let it fix them."""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

from agent.validate import run_tests

FIX_PROMPT = """\
You are working in a Python repository that has failing pytest tests due to real bugs
in the source code (not the tests).

Your job:
1. Run `pytest -q` to see which tests fail and why.
2. Read the relevant source file(s) and figure out the root cause of each failure.
3. Fix the bugs in the source code. Do NOT modify any test files (test_*.py) — the
   tests define the correct expected behavior.
4. Re-run `pytest -q` after each change and keep iterating until all tests pass.
5. Once all tests pass, stop. Do not run any git commands — that is handled separately.

Be surgical: only change what's needed to make the existing tests pass correctly.
"""


async def _run_fix(repo_path: str, prompt: str) -> str:
    options = ClaudeAgentOptions(
        cwd=repo_path,
        tools=["Read", "Edit", "Write", "Bash", "Grep", "Glob"],
        permission_mode="acceptEdits",
        max_turns=30,
    )

    transcript: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[agent] {block.text}")
                    transcript.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"[agent:tool] {block.name} {block.input}")
        elif isinstance(message, ResultMessage):
            print(f"[agent:done] turns={message.num_turns} cost=${message.total_cost_usd}")
            if message.result:
                transcript.append(message.result)

    return "\n".join(transcript)


def fix_bugs(repo_path: str, prompt: str = FIX_PROMPT) -> str:
    """Run the agent against repo_path until it believes the tests pass. Returns transcript."""
    return asyncio.run(_run_fix(repo_path, prompt))


def fix_until_passing(repo_path: str, max_attempts: int = 3) -> bool:
    """Run the agent, then independently verify with pytest. Retry with the failure
    output fed back in if tests still fail. Returns True once tests genuinely pass."""
    prompt = FIX_PROMPT

    for attempt in range(1, max_attempts + 1):
        print(f"[orchestrator] attempt {attempt}/{max_attempts}")
        fix_bugs(repo_path, prompt)

        result = run_tests(repo_path)
        if result.passed:
            print("[orchestrator] tests pass — verified independently")
            return True

        print(f"[orchestrator] tests still failing:\n{result.output}")
        prompt = (
            FIX_PROMPT
            + "\n\nA previous attempt left tests still failing. Here is the actual "
            + f"pytest output from an independent run just now:\n\n{result.output}\n\n"
            + "Diagnose why your previous fix didn't fully work and correct it."
        )

    return False
