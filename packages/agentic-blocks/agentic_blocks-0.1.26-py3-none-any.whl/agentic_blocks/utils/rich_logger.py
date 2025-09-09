import time
from rich.console import Group, Console
from rich.json import JSON
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text
from rich.box import HEAVY
from rich.panel import Panel

# Create a console instance for Jupyter


def create_panel(content, title, border_style="blue"):
    return Panel(
        content,
        title=title,
        title_align="left",
        border_style=border_style,
        box=HEAVY,
        expand=True,
        padding=(1, 1),
    )


def print_response(user_prompt):
    with Live(console=Console(), auto_refresh=False) as live_log:
        status = Status("Thinking...", spinner="aesthetic", speed=0.4)
        live_log.update(status)
        live_log.refresh()  # Explicit refresh for Jupyter

        # Create panels
        panels = [status]

        message_panel = create_panel(
            content=Text(user_prompt, style="green"),
            title="Message",
            border_style="cyan",
        )

        panels.append(message_panel)
        live_log.update(Group(*panels))
        live_log.refresh()  # Explicit refresh for Jupyter

        # Add some delay to see the display

        for i in range(3):
            time.sleep(2)

            # Add a response panel
            response_panel = create_panel(
                content=Text("Response: " + str(i), style="bold blue"),
                title="Response",
                border_style="green",
            )

            panels.append(response_panel)
            live_log.update(Group(*panels))
            live_log.refresh()
