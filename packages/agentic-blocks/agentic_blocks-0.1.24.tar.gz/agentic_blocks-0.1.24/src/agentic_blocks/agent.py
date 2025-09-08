from pocketflow import Node, Flow
from agentic_blocks.utils.tools_utils import (
    create_tool_registry,
    execute_pending_tool_calls,
)
from agentic_blocks import call_llm, Messages
from rich.panel import Panel
from rich.box import HEAVY
from rich.console import Console
from rich.console import Group

console = Console(
    style="black on bright_white",
    force_terminal=True,
    width=None,
    legacy_windows=False,
    color_system="truecolor",
)


class Agent:
    def __init__(self, system_prompt: str, tools: list):
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = create_tool_registry(tools)
        self.panels = []

        # Create nodes
        self.llm_node = self._create_llm_node()
        self.tool_node = self._create_tool_node()
        self.answer_node = self._create_answer_node()

        # Set up flow
        self.llm_node - "tool_node" >> self.tool_node
        self.tool_node - "llm_node" >> self.llm_node
        self.llm_node - "answer_node" >> self.answer_node

        self.flow = Flow(self.llm_node)

    def _create_llm_node(self):
        class LLMNode(Node):
            def __init__(self, system_prompt, tools):
                super().__init__()
                self.system_prompt = system_prompt
                self.tools = tools

            def prep(self, shared):
                messages = shared["messages"]
                return messages

            def exec(self, messages) -> Messages:
                response = call_llm(messages=messages, tools=self.tools)
                messages.add_response_message(response)
                return messages

            def post(self, shared, prep_res, messages):
                if messages.has_pending_tool_calls():
                    return "tool_node"
                else:
                    return "answer_node"

        return LLMNode(self.system_prompt, self.tools)

    def _create_tool_node(self):
        class ToolNode(Node):
            def __init__(self, tool_registry, agent):
                super().__init__()
                self.tool_registry = tool_registry
                self.agent = agent

            def prep(self, shared):
                return shared["messages"]

            def exec(self, messages) -> Messages:
                tool_calls = messages.get_pending_tool_calls()[0]
                tool_name = tool_calls["tool_name"]
                tool_arguments = tool_calls["arguments"]

                # Format arguments nicely
                if isinstance(tool_arguments, dict):
                    args_str = ", ".join(
                        [f"{k}={v}" for k, v in tool_arguments.items()]
                    )
                    formatted_call = f"{tool_name}({args_str})"
                else:
                    formatted_call = f"{tool_name}({tool_arguments})"

                tool_panel = self.agent.create_panel(formatted_call, "Tool Calls")
                self.agent.panels.append(tool_panel)

                tool_responses = execute_pending_tool_calls(
                    messages, self.tool_registry
                )
                messages.add_tool_responses(tool_responses)
                return messages

            def post(self, shared, prep_res, messages):
                return "llm_node"

        return ToolNode(self.tool_registry, self)

    def _create_answer_node(self):
        class AnswerNode(Node):
            def prep(self, shared):
                messages = shared["messages"]
                shared["answer"] = messages.get_messages()[-1]["content"]
                return messages

        return AnswerNode()

    def invoke(self, user_prompt: str) -> str:
        messages = Messages(user_prompt=user_prompt)
        if self.system_prompt:
            messages.add_system_message(self.system_prompt)

        shared = {"messages": messages}
        self.flow.run(shared)

        return shared["answer"]

    def print_response(self, user_prompt: str, stream: bool = False):
        # Reset panels and start with message
        self.panels = []
        message_panel = self.create_panel(user_prompt, "Message")
        self.panels.append(message_panel)

        # Always collect all panels first
        response = self.invoke(user_prompt)
        response_panel = self.create_panel(response, "Response")
        self.panels.append(response_panel)

        # Print all panels as a group (no gaps)
        panel_group = Group(*self.panel)
        console.print(panel_group)

    def create_panel(self, content, title, border_style="blue"):
        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=border_style,
            box=HEAVY,
            expand=True,  # Full terminal width
            padding=(1, 1),  # Internal padding
        )
