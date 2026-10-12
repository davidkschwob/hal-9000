import contextlib
import copy
import io
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from harness import agent


class FakeCompletions:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        return next(self.responses)


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(
                [SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])
                 for text in responses]
            )
        )


class AgentResponseTests(unittest.TestCase):
    def test_splits_explicit_sections_and_preserves_unwrapped_text(self):
        segments = list(
            agent._parse_response(
                "prefix<thinking>reason</thinking>"
                "<hal>answer</hal><output>table</output>suffix"
            )
        )
        self.assertEqual(
            segments,
            [
                ("hal", "prefix", None),
                ("thinking", "reason", None),
                ("hal", "answer", None),
                ("output", "table", None),
                ("hal", "suffix", None),
            ],
        )

    def test_parses_tagged_tool_call(self):
        self.assertEqual(
            list(agent._parse_response('<tool name="git_list_files">{"repo_path":"."}</tool>')),
            [("tool", '{"repo_path":"."}', "git_list_files")],
        )

    def test_one_shot_turn_executes_tool_then_returns_final_answer(self):
        client = FakeClient(
            [
                '<thinking>Inspecting.</thinking><tool name="lookup">'
                '{"query":"target"}</tool>',
                "<hal>Done.</hal>",
            ]
        )
        observed_queries = []

        def lookup(query):
            observed_queries.append(query)
            return "Found target."

        output = io.StringIO()
        with (
            patch.object(agent, "get_llm_client", return_value=client),
            patch.object(agent, "_load_system_prompt", return_value="prompt"),
            patch.object(agent, "TOOL_REGISTRY", {"lookup": lookup}),
            patch.object(agent, "ALL_GROQ_TOOLS", []),
            patch.dict(os.environ, {"GROQ_MODEL": "test-model"}),
            patch("builtins.input", return_value=""),
            contextlib.redirect_stdout(output),
        ):
            agent.agent_loop("/workspace", "inspect")

        requests = client.chat.completions.requests
        self.assertEqual(len(requests), 2)
        self.assertNotIn("stream", requests[0])
        self.assertNotIn("tools", requests[0])
        self.assertIn("Available tools", requests[0]["messages"][0]["content"])
        self.assertEqual(observed_queries, ["target"])
        second_turn_messages = requests[1]["messages"]
        self.assertEqual(second_turn_messages[-2]["role"], "assistant")
        self.assertEqual(
            second_turn_messages[-1]["content"],
            "Tool 'lookup' result:\nFound target.",
        )
        self.assertIn("Inspecting.", output.getvalue())
        self.assertIn("Done.", output.getvalue())

    def test_rejects_invalid_or_unknown_tool_calls_without_execution(self):
        with patch.object(agent, "TOOL_REGISTRY", {}):
            self.assertIn("invalid JSON", agent._execute_tool("x", "{"))
            self.assertIn("unknown tool", agent._execute_tool("missing", "{}"))


if __name__ == "__main__":
    unittest.main()
