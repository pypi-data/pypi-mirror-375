import re
import typer
from pathlib import Path
from rich.panel import Panel

from blocks_cli.console import console
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.fs import find_dir
from blocks_cli.package import warn_current_package_version, get_latest_sdk_version

class InvalidAutomationNameError(Exception):
    pass

class NoBlocksDirError(Exception):
    pass

class AutomationAlreadyExistsError(Exception):
    pass

@blocks_cli.command()
def create(
    name: str = typer.Argument(..., help="Name of the automation to create."),
):
    """
    Create a new automation in the .blocks directory.
    The command will fail if .blocks directory doesn't exist.
    """
    try:
        warn_current_package_version()

        # Validate automation name (only allow alphanumeric, dash, and underscore)
        if not name or re.search(r'[^a-zA-Z0-9\_-]', name) or name[0].isdigit():
            raise InvalidAutomationNameError("Automation name cannot start with a number, and must contain only letters, numbers, dashes, and underscores")

        blocks_dir = find_dir(target=".blocks")

        if not blocks_dir:
            raise NoBlocksDirError("No .blocks directory found, have you run [white]blocks init[/white]?")

        # Create automation directory
        automation_dir = blocks_dir / name
        if automation_dir.exists():
            raise AutomationAlreadyExistsError(f"Automation [white]{name}[/white] already exists")

        try:
            # Create directory and files
            automation_dir.mkdir(parents=True)

            function_name = name.replace("-", "_")
            
            # Create main.py with basic template
            with open(automation_dir / 'main.py', 'w') as f:
                f.write('''import os
import slack_sdk
from enum import Enum
from blocks import agent, on
from smolagents import CodeAgent, WebSearchTool, LiteLLMModel
from pydantic import BaseModel

SLACK_TOKEN = os.getenv("SLACK_TOKEN")

class Models(str, Enum):
    gpt_5 = "gpt-5"
    claude4sonnet = "claude-sonnet-4-20250514"

class SmolAgentConfig(BaseModel):
    model: Models = Models.gpt_5

@agent(name="{name}")
@on("slack.mention")
def {function_name}(input, config: SmolAgentConfig):
    event = input.get("event")
    text = event.get("text", "")
    channel = event.get("channel", "")
    ts = event.get("ts", "")

    model = LiteLLMModel(
        model_id=config.model,
    )
    agent = CodeAgent(tools=[WebSearchTool()], model=model)
    agent.run(text)

    client = slack_sdk.WebClient(token=SLACK_TOKEN)
    client.chat_postMessage(channel=channel, text="Agent is thinking...", thread_ts=ts)

    for _, step in enumerate(agent.memory.steps):
        messages = step.to_messages()
        for message in messages:
            for content_message in message.content:
                final_message = content_message.get("text", "")
                if final_message and content_message.get("role") != "user":
                    client.chat_postMessage(channel=channel, text=final_message, thread_ts=ts)
'''.format(name=name, function_name=function_name))

            sdk_version = get_latest_sdk_version()
            latest_version = sdk_version.get("latest_version")

            with open(automation_dir / 'requirements.txt', 'w') as f:
                f.write('''blocks-sdk>={version}
smolagents[toolkit]
litellm>=1.61.16,<=1.74.8
slack-sdk>=3.19.2
'''.format(version=latest_version))

            console.print(f"Successfully created automation [green]{name}[/green] in [green]{automation_dir.absolute()}[/green]")
            console.print(f"[green]{name}/\n   main.py\n   requirements.txt[/green]")
            console.print(f"[blue]Choose an event from [white]https://docs.blocksorg.com/events[/white] and run [white]blocks test .blocks/{name}/main.py[/white] to test the automation[/blue]")

        except Exception as e:
            # Clean up if something goes wrong after directory creation
            if automation_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(automation_dir)
                except Exception:
                    pass
            raise
        
    except (InvalidAutomationNameError, NoBlocksDirError, AutomationAlreadyExistsError) as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error creating automation: {str(e)}[/red]")
        raise typer.Exit(1)