from pocketflow import Node, Flow
from agentic_blocks.utils.tools_utils import (
    create_tool_registry,
    execute_pending_tool_calls,
)
from agentic_blocks import call_llm, Messages


from rich.console import Group, Console
from rich.json import JSON
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text
from rich.box import HEAVY
from rich.panel import Panel
from agentic_blocks.utils.rich_logger import print_response


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
                for tool_call in messages.get_pending_tool_calls():
                    tool_name = tool_call["tool_name"]
                    tool_arguments = tool_call["arguments"]

                    # Format arguments nicely
                    if isinstance(tool_arguments, dict):
                        args_str = ", ".join(
                            [f"{k}={v}" for k, v in tool_arguments.items()]
                        )
                        formatted_call = f"{tool_name}({args_str})"
                    else:
                        formatted_call = f"{tool_name}({tool_arguments})"

                    tool_panel = self.agent.create_panel(formatted_call, "Tool Request")
                    self.agent.panels.append(tool_panel)

                self.agent.live_log.update(Group(*self.agent.panels))
                self.agent.live_log.refresh()

                tool_responses = execute_pending_tool_calls(
                    messages, self.tool_registry
                )

                for tool_response in tool_responses:
                    tool_panel = self.agent.create_panel(
                        str(tool_response["tool_response"]), "Tool Response"
                    )
                    self.agent.panels.append(tool_panel)

                self.agent.live_log.update(Group(*self.agent.panels))
                self.agent.live_log.refresh()

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

    def create_panel(self, content, title, border_style="blue"):
        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=border_style,
            box=HEAVY,
            expand=True,
            padding=(1, 1),
        )

    def invoke(self, user_prompt: str):
        messages = Messages(user_prompt=user_prompt)
        if self.system_prompt:
            messages.add_system_message(self.system_prompt)

        shared = {"messages": messages}

        with Live(console=Console(), auto_refresh=False) as self.live_log:
            status = Status("Thinking...", spinner="aesthetic", speed=0.4)
            self.live_log.update(status)
            self.live_log.refresh()  # Explicit refresh for Jupyter

            self.panels = [status]

            message_panel = self.create_panel(
                content=Text(user_prompt, style="green"),
                title="Message",
                border_style="cyan",
            )

            self.panels.append(message_panel)
            self.live_log.update(Group(*self.panels))
            self.live_log.refresh()

            self.flow.run(shared)
            response = shared["answer"]

            response_panel = self.create_panel(
                content=Text(response, style="bold blue"),
                title="Final Response",
                border_style="green",
            )

            self.panels.append(response_panel)
            self.live_log.update(Group(*self.panels))
            self.live_log.refresh()
