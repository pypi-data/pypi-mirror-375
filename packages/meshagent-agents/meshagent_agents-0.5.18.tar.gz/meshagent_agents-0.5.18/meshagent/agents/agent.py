from typing import Optional

from meshagent.api.messaging import unpack_message, pack_message
from meshagent.api.room_server_client import (
    RoomException,
    RequiredToolkit,
    Requirement,
    RequiredSchema,
)
from meshagent.api import (
    ToolDescription,
    ToolkitDescription,
    Participant,
    RemoteParticipant,
    meshagent_base_url,
    StorageEntry,
)
from meshagent.api.protocol import Protocol
from meshagent.tools.toolkit import (
    Toolkit,
    Tool,
    ToolContext,
    toolkit_factory,
    register_toolkit_factory,
)
from meshagent.api.room_server_client import RoomClient
from jsonschema import validate
from .context import AgentCallContext, AgentChatContext
from meshagent.api.schema_util import no_arguments_schema
import logging
import asyncio

logger = logging.getLogger("agent")


class AgentException(RoomException):
    pass


class RoomTool(Tool):
    def __init__(
        self,
        *,
        toolkit_name: str,
        name,
        input_schema,
        title=None,
        description=None,
        rules=None,
        thumbnail_url=None,
        participant_id: Optional[str] = None,
        on_behalf_of_id: Optional[str] = None,
        defs: Optional[dict] = None,
    ):
        self._toolkit_name = toolkit_name
        self._participant_id = participant_id
        self._on_behalf_of_id = on_behalf_of_id

        super().__init__(
            name=name,
            input_schema=input_schema,
            title=title,
            description=description,
            rules=rules,
            thumbnail_url=thumbnail_url,
            defs=defs,
        )

    async def execute(self, context, **kwargs):
        return await context.room.agents.invoke_tool(
            toolkit=self._toolkit_name,
            tool=self.name,
            participant_id=self._participant_id,
            on_behalf_of_id=self._on_behalf_of_id,
            arguments=kwargs,
        )


class Agent:
    def __init__(
        self,
        *,
        name: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        requires: Optional[list[Requirement]] = None,
        labels: Optional[list[str]] = None,
    ):
        self._name = name
        if title is None:
            title = name
        self._title = title
        if description is None:
            description = ""

        self._description = description
        if requires is None:
            requires = []

        self.init_requirements(requires)
        self._requires = requires

        if labels is None:
            labels = []

        self._labels = labels

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def title(self):
        return self._title

    @property
    def requires(self):
        return self._requires

    @property
    def labels(self):
        return self._labels

    def init_requirements(self, requires): ...

    async def init_chat_context(self) -> AgentChatContext:
        return AgentChatContext()

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "requires": list(map(lambda x: x.to_json(), self.requires)),
            "labels": self.labels,
        }


class SingleRoomAgent(Agent):
    def __init__(
        self,
        *,
        name,
        title=None,
        description=None,
        requires=None,
        labels: Optional[list[str]] = None,
    ):
        super().__init__(
            name=name,
            title=title,
            description=description,
            requires=requires,
            labels=labels,
        )
        self._room = None

    async def start(self, *, room: RoomClient) -> None:
        if self._room is not None:
            raise RoomException("room is already started")

        self._room = room

        await self.install_requirements()

    async def stop(self) -> None:
        self._room = None
        pass

    @property
    def room(self):
        return self._room

    async def install_requirements(self, participant_id: Optional[str] = None):
        schemas_by_name = dict[str, StorageEntry]()

        schemas = await self._room.storage.list(path=".schemas")

        for schema in schemas:
            schemas_by_name[schema.name] = schema

        toolkits_by_name = dict[str, ToolkitDescription]()

        visible_tools = await self._room.agents.list_toolkits(
            participant_id=participant_id
        )

        for toolkit_description in visible_tools:
            toolkits_by_name[toolkit_description.name] = toolkit_description

        installed = False

        for requirement in self.requires:
            if isinstance(requirement, RequiredToolkit):
                if toolkit_factory(requirement.name) is not None:
                    # no need to install something we can create from a factory
                    continue

                if requirement.name == "ui":
                    # TODO: maybe requirements can be marked as non installable?
                    continue

                if requirement.name not in toolkits_by_name:
                    installed = True

                    logger.info(f"Installing required tool {requirement.name}")

                    if requirement.name.startswith("https://"):
                        url = requirement.name
                    else:
                        url = f"{meshagent_base_url()}/toolkits/{requirement.name}"

                    await self._room.agents.make_call(
                        url=url, name=requirement.name, arguments={}
                    )

            elif isinstance(requirement, RequiredSchema):
                if requirement.name not in schemas_by_name:
                    installed = True

                    logger.info(f"Installing required schema {requirement.name}")

                    if requirement.name.startswith("https://"):
                        url = requirement.name
                    else:
                        url = f"{meshagent_base_url()}/schemas/{requirement.name}"

                    await self._room.agents.make_call(
                        url=url, name=requirement.name, arguments={}
                    )

            else:
                raise RoomException("unsupported requirement")

        if installed:
            await asyncio.sleep(5)

    async def get_required_toolkits(self, context: ToolContext) -> list[Toolkit]:
        tool_target = context.caller
        if context.on_behalf_of is not None:
            tool_target = context.on_behalf_of

        toolkits_by_name = dict[str, ToolkitDescription]()

        toolkits = list[Toolkit]()

        visible_tools = await self._room.agents.list_toolkits(
            participant_id=tool_target.id
        )

        for toolkit_description in visible_tools:
            toolkits_by_name[toolkit_description.name] = toolkit_description

        for required_toolkit in self.requires:
            if isinstance(required_toolkit, RequiredToolkit):
                if toolkit_factory(required_toolkit.name) is not None:
                    toolkit = await toolkit_factory(required_toolkit.name)(
                        context, required_toolkit
                    )
                    toolkits.append(toolkit)
                    continue

                toolkit = toolkits_by_name.get(required_toolkit.name, None)
                if toolkit is None:
                    raise RoomException(
                        f"unable to locate required toolkit {required_toolkit.name}"
                    )

                room_tools = list[RoomTool]()

                if required_toolkit.tools is None:
                    for tool_description in toolkit.tools:
                        tool = RoomTool(
                            on_behalf_of_id=tool_target.id,
                            toolkit_name=toolkit.name,
                            name=tool_description.name,
                            description=tool_description.description,
                            input_schema=tool_description.input_schema,
                            title=tool_description.title,
                            thumbnail_url=tool_description.thumbnail_url,
                            participant_id=tool_target.id,
                            defs=tool_description.defs,
                        )
                        room_tools.append(tool)

                else:
                    tools_by_name = dict[str, ToolDescription]()
                    for tool_description in toolkit.tools:
                        tools_by_name[tool_description.name] = tool_description

                    for required_tool in required_toolkit.tools:
                        tool_description = tools_by_name.get(required_tool, None)
                        if tool_description is None:
                            raise RoomException(
                                f"unable to locate required tool {required_tool}"
                            )

                        tool = RoomTool(
                            on_behalf_of_id=tool_target.id,
                            toolkit_name=toolkit.name,
                            name=tool_description.name,
                            description=tool_description.description,
                            input_schema=tool_description.input_schema,
                            title=tool_description.title,
                            thumbnail_url=tool_description.thumbnail_url,
                            participant_id=tool_target.id,
                            defs=tool_description.defs,
                        )
                        room_tools.append(tool)

                toolkits.append(
                    Toolkit(
                        name=toolkit.name,
                        title=toolkit.title,
                        description=toolkit.description,
                        thumbnail_url=toolkit.thumbnail_url,
                        tools=room_tools,
                    )
                )

        return toolkits


class TaskRunner(SingleRoomAgent):
    def __init__(
        self,
        *,
        name,
        title=None,
        description=None,
        requires=None,
        supports_tools: Optional[bool] = None,
        input_schema: dict,
        output_schema: Optional[dict] = None,
        labels: Optional[list[str]] = None,
        toolkits: Optional[list[Toolkit]] = None,
    ):
        super().__init__(
            name=name,
            title=title,
            description=description,
            requires=requires,
            labels=labels,
        )

        if toolkits is None:
            toolkits = []

        self._toolkits = toolkits

        self._registration_id = None

        if input_schema is None:
            input_schema = no_arguments_schema(
                description="execute the agent",
            )

        if supports_tools is None:
            supports_tools = False

        self._supports_tools = supports_tools
        self._input_schema = input_schema
        self._output_schema = output_schema

    async def validate_arguments(self, arguments: dict):
        validate(arguments, self.input_schema)

    async def validate_response(self, response: dict):
        if self.output_schema is not None:
            validate(response, self.output_schema)

    async def ask(self, *, context: AgentCallContext, arguments: dict) -> dict:
        raise Exception("Not implemented")

    @property
    def supports_tools(self):
        return self._supports_tools

    @property
    def input_schema(self):
        return self._input_schema

    @property
    def output_schema(self):
        return self._output_schema

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "requires": list(map(lambda x: x.to_json(), self.requires)),
            "supports_tools": self.supports_tools,
            "labels": self.labels,
        }

    async def _register(self):
        self._registration_id = (
            await self._room.send_request(
                "agent.register_agent",
                {
                    "name": self.name,
                    "title": self.title,
                    "description": self.description,
                    "input_schema": self.input_schema,
                    "output_schema": self.output_schema,
                    "requires": list(map(lambda x: x.to_json(), self.requires)),
                    "supports_tools": self.supports_tools,
                    "labels": self.labels,
                },
            )
        )["id"]

    async def _unregister(self):
        await self._room.send_request(
            "agent.unregister_agent", {"id": self._registration_id}
        )
        self._registration_id = None

    async def start(self, *, room: RoomClient):
        await super().start(room=room)

        self._room.protocol.register_handler("agent.ask", self._ask)
        await self._register()

    async def stop(self):
        if self.room.protocol.is_open:
            await self._unregister()
        else:
            logger.info(
                f"disconnected '{self.name}' from room, this will automatically happen when all the users leave the room. agents will not keep the room open"
            )

        self._room.protocol.unregister_handler("agent.ask", self._ask)

        await super().stop()

    async def _ask(
        self, protocol: Protocol, message_id: int, msg_type: str, data: bytes
    ):
        async def worker():
            # Decode and parse the message
            message, _ = unpack_message(data)
            logger.info("agent got message %s", message)
            args = message["arguments"]
            task_id = message["task_id"]
            toolkits_json = message["toolkits"]

            # context_json = message["context"]

            chat_context = None

            try:
                chat_context = await self.init_chat_context()

                caller: Participant | None = None
                on_behalf_of: Participant | None = None
                on_behalf_of_id = message.get("on_behalf_of_id", None)

                for participant in self._room.messaging.get_participants():
                    if message["caller_id"] == participant.id:
                        caller = participant
                        break

                    if on_behalf_of_id == participant.id:
                        on_behalf_of = participant
                        break

                if caller is None:
                    caller = RemoteParticipant(
                        id=message["caller_id"], role="user", attributes={}
                    )

                if on_behalf_of_id is not None and on_behalf_of is None:
                    on_behalf_of = RemoteParticipant(
                        id=message["on_behalf_of_id"], role="user", attributes={}
                    )

                tool_target = caller
                if on_behalf_of is not None:
                    tool_target = on_behalf_of

                toolkits = [
                    *self._toolkits,
                    *await self.get_required_toolkits(
                        context=ToolContext(
                            room=self.room,
                            caller=caller,
                            on_behalf_of=on_behalf_of,
                            caller_context={"chat": chat_context.to_json()},
                        )
                    ),
                ]

                context = AgentCallContext(
                    chat=chat_context,
                    room=self.room,
                    caller=caller,
                    on_behalf_of=on_behalf_of,
                    toolkits=toolkits,
                )

                for toolkit_json in toolkits_json:
                    tools = []
                    for tool_json in toolkit_json["tools"]:
                        tools.append(
                            RoomTool(
                                on_behalf_of_id=on_behalf_of_id,
                                participant_id=tool_target.id,
                                toolkit_name=toolkit_json["name"],
                                name=tool_json["name"],
                                title=tool_json["title"],
                                description=tool_json["description"],
                                input_schema=tool_json["input_schema"],
                                thumbnail_url=toolkit_json["thumbnail_url"],
                                defs=tool_json.get("defs", None),
                            )
                        )

                    context.toolkits.append(
                        Toolkit(
                            name=toolkit_json["name"],
                            title=toolkit_json["title"],
                            description=toolkit_json["description"],
                            thumbnail_url=toolkit_json["thumbnail_url"],
                            tools=tools,
                        )
                    )

                response = await self.ask(context=context, arguments=args)

                await protocol.send(
                    type="agent.ask_response",
                    data=pack_message(
                        {
                            "task_id": task_id,
                            "answer": response,
                            "caller_context": {"chat": chat_context.to_json()},
                        }
                    ),
                )

            except Exception as e:
                logger.error("Task runner failed to complete task", exc_info=e)
                if chat_context is not None:
                    await protocol.send(
                        type="agent.ask_response",
                        data=pack_message(
                            {
                                "task_id": task_id,
                                "error": str(e),
                                "caller_context": {"chat": chat_context.to_json()},
                            }
                        ),
                    )
                else:
                    await protocol.send(
                        type="agent.ask_response",
                        data=pack_message(
                            {
                                "task_id": task_id,
                                "error": str(e),
                            }
                        ),
                    )

        def on_done(task: asyncio.Task):
            task.result()

        task = asyncio.create_task(worker())
        task.add_done_callback(on_done)


class RunTaskTool(Tool):
    def __init__(
        self,
        *,
        name: str,
        agent_name: str,
        input_schema: dict,
        rules=None,
        thumbnail_url=None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            input_schema=input_schema,
            rules=rules,
            thumbnail_url=thumbnail_url,
            title=title,
            description=description,
        )

        self._agent_name = agent_name

    async def execute(self, context: ToolContext, **kwargs):
        return await context.room.agents.ask(agent=self._agent_name, arguments=kwargs)


async def make_run_task_tool(context: ToolContext, toolkit: RequiredToolkit):
    agents = await context.room.agents.list_agents()
    tools = []
    for agent_name in toolkit.tools:
        agent = next((x for x in agents if x.name == agent_name), None)

        if agent is None:
            raise RoomException(f"agent was not found in the room {agent_name}")

        tools.append(
            RunTaskTool(
                agent_name=agent_name,
                name=f"run_{agent_name}",
                input_schema=agent.input_schema,
                title=agent.title,
                description=agent.description,
            )
        )

    return Toolkit(name="agents", tools=tools)


register_toolkit_factory("agents", make_run_task_tool)
