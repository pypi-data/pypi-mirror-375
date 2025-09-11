from meshagent.agents.mail import MailWorker

import typer
from meshagent.api import ParticipantToken
from rich import print
from typing import Annotated, Optional
from meshagent.cli.common_options import (
    ProjectIdOption,
    ApiKeyIdOption,
    RoomOption,
)
from meshagent.tools import Toolkit
from meshagent.api import RoomClient, WebSocketClientProtocol
from meshagent.api.helpers import meshagent_base_url, websocket_room_url
from meshagent.cli import async_typer
from meshagent.cli.helper import (
    get_client,
    resolve_project_id,
    resolve_api_key,
    resolve_token_jwt,
    resolve_room,
)
from meshagent.openai import OpenAIResponsesAdapter
from meshagent.openai.tools.responses_adapter import ImageGenerationTool, LocalShellTool
from meshagent.api.services import ServiceHost

from meshagent.agents.mail import room_address
from typing import List
from pathlib import Path

from meshagent.api import RequiredToolkit, RequiredSchema
from meshagent.openai.tools.responses_adapter import WebSearchTool

app = async_typer.AsyncTyper(help="Join a mailbot to a room")


def build_mailbot(
    *,
    model: str,
    agent_name: str,
    rule: List[str],
    toolkit: List[str],
    schema: List[str],
    image_generation: Optional[str] = None,
    local_shell: bool,
    computer_use: bool,
    rules_file: Optional[str] = None,
    web_search: Annotated[
        Optional[bool], typer.Option(..., help="Enable web search tool calling")
    ] = False,
):
    requirements = []

    toolkits = []

    for t in toolkit:
        requirements.append(RequiredToolkit(name=t))

    for t in schema:
        requirements.append(RequiredSchema(name=t))

    if rules_file is not None:
        try:
            with open(Path(rules_file).resolve(), "r") as f:
                rule.extend(f.read().splitlines())
        except FileNotFoundError:
            print(f"[yellow]rules file not found at {rules_file}[/yellow]")

    BaseClass = MailWorker
    if computer_use:
        raise ValueError("computer use is not yet supported for the mail agent")
    else:
        llm_adapter = OpenAIResponsesAdapter(model=model)

    class CustomMailbot(BaseClass):
        def __init__(self):
            super().__init__(
                llm_adapter=llm_adapter,
                name=agent_name,
                requires=requirements,
                toolkits=toolkits,
                rules=rule if len(rule) > 0 else None,
            )

        async def start(self, *, room: RoomClient):
            parsed_token = ParticipantToken.from_jwt(
                room.protocol.token, validate=False
            )
            print(
                f"[bold green]Send an email interact with your mailbot: {room_address(project_id=parsed_token.project_id, room_name=room.room_name)}[/bold green]"
            )
            return await super().start(room=room)

        async def get_thread_toolkits(self, *, thread_context):
            toolkits = await super().get_thread_toolkits(thread_context=thread_context)

            thread_toolkit = Toolkit(name="thread_toolkit", tools=[])

            if local_shell:
                thread_toolkit.tools.append(
                    LocalShellTool(thread_context=thread_context)
                )

            if image_generation is not None:
                print("adding openai image gen to thread", flush=True)
                thread_toolkit.tools.append(
                    ImageGenerationTool(
                        model=image_generation,
                        thread_context=thread_context,
                        partial_images=3,
                    )
                )

            if web_search:
                thread_toolkit.tools.append(WebSearchTool())

            toolkits.append(thread_toolkit)
            return toolkits

    return CustomMailbot


@app.async_command("join")
async def make_call(
    *,
    project_id: ProjectIdOption = None,
    room: RoomOption = None,
    api_key_id: ApiKeyIdOption = None,
    role: str = "agent",
    agent_name: Annotated[str, typer.Option(..., help="Name of the agent to call")],
    token_path: Annotated[Optional[str], typer.Option()] = None,
    rule: Annotated[List[str], typer.Option("--rule", "-r", help="a system rule")] = [],
    rules_file: Optional[str] = None,
    toolkit: Annotated[
        List[str],
        typer.Option("--toolkit", "-t", help="the name or url of a required toolkit"),
    ] = [],
    schema: Annotated[
        List[str],
        typer.Option("--schema", "-s", help="the name or url of a required schema"),
    ] = [],
    model: Annotated[
        str, typer.Option(..., help="Name of the LLM model to use for the chatbot")
    ] = "gpt-4o",
    local_shell: Annotated[
        Optional[bool], typer.Option(..., help="Enable local shell tool calling")
    ] = False,
    web_search: Annotated[
        Optional[bool], typer.Option(..., help="Enable web search tool calling")
    ] = False,
):
    account_client = await get_client()
    try:
        project_id = await resolve_project_id(project_id=project_id)
        api_key_id = await resolve_api_key(project_id, api_key_id)

        room = resolve_room(room)
        jwt = await resolve_token_jwt(
            project_id=project_id,
            api_key_id=api_key_id,
            token_path=token_path,
            name=agent_name,
            role=role,
            room=room,
        )

        print("[bold green]Connecting to room...[/bold green]", flush=True)
        async with RoomClient(
            protocol=WebSocketClientProtocol(
                url=websocket_room_url(room_name=room, base_url=meshagent_base_url()),
                token=jwt,
            )
        ) as client:
            requirements = []

            for t in toolkit:
                requirements.append(RequiredToolkit(name=t))

            for t in schema:
                requirements.append(RequiredSchema(name=t))

            CustomMailbot = build_mailbot(
                computer_use=None,
                model=model,
                local_shell=local_shell,
                agent_name=agent_name,
                rule=rule,
                toolkit=toolkit,
                schema=schema,
                image_generation=None,
                web_search=web_search,
                rules_file=rules_file,
            )

            bot = CustomMailbot()

            await bot.start(room=client)
            try:
                print(
                    flush=True,
                )
                await client.protocol.wait_for_close()
            except KeyboardInterrupt:
                await bot.stop()

    finally:
        await account_client.close()


@app.async_command("service")
async def service(
    *,
    room: RoomOption = None,
    agent_name: Annotated[str, typer.Option(..., help="Name of the agent to call")],
    rule: Annotated[List[str], typer.Option("--rule", "-r", help="a system rule")] = [],
    rules_file: Optional[str] = None,
    toolkit: Annotated[
        List[str],
        typer.Option("--toolkit", "-t", help="the name or url of a required toolkit"),
    ] = [],
    schema: Annotated[
        List[str],
        typer.Option("--schema", "-s", help="the name or url of a required schema"),
    ] = [],
    model: Annotated[
        str, typer.Option(..., help="Name of the LLM model to use for the chatbot")
    ] = "gpt-4o",
    local_shell: Annotated[
        Optional[bool], typer.Option(..., help="Enable local shell tool calling")
    ] = False,
    host: Annotated[Optional[str], typer.Option()] = None,
    port: Annotated[Optional[int], typer.Option()] = None,
    path: Annotated[str, typer.Option()] = "/agent",
):
    room = resolve_room(room)

    print("[bold green]Connecting to room...[/bold green]", flush=True)

    service = ServiceHost(host=host, port=port)
    service.add_path(
        path=path,
        cls=build_mailbot(
            computer_use=None,
            model=model,
            local_shell=local_shell,
            agent_name=agent_name,
            rule=rule,
            toolkit=toolkit,
            schema=schema,
            image_generation=None,
            rules_file=rules_file,
        ),
    )

    await service.run()
