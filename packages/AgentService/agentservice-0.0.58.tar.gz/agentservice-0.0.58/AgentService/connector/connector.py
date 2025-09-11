
import functools
import typing
import aiohttp

from loguru import logger

from .event import ToolEvent

from AgentService.types.response import AgentResponse, AgentResponseType
from AgentService.dtypes.message import SendMessageRequest, Tool, ToolAnswer


class AgentConnector:
    def __init__(
        self,
        endpoint: str,
        key: str = None
    ):

        self.log = logger.bind(classname=self.__class__.__name__)

        self.endpoint = endpoint[:-1] if endpoint.endswith("/") else endpoint
        self.key = key

        self.callbacks = {}
        self.bind_tool_output("file_search", self.search_in_files)

    def bind_tool_output(self, tool_name: str, function: typing.Callable):
        self.callbacks.update({tool_name: functools.partial(self.answer_tool, function=function)})
        self.log.debug(f"Binded callback -> {tool_name} -> {function}")

    async def search_in_files(self, data: str, chat_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"{self.endpoint}/storage/search",
                json={
                    "query": data
                },
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")

                return (await resp.json()).get("data")

    async def add_to_storage(self, key: str, data: list[dict] | dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.endpoint}/storage/add",
                json={
                    "key": key,
                    "data": data
                },
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")
                return await resp.json()

    async def remove_from_storage(self, key: str, data: list[dict] | dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.endpoint}/storage/remove",
                json={
                    "key": key,
                    "data": data
                },
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")
                return await resp.json()

    async def update_storage(self, key: str, data: dict, new_data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.endpoint}/storage/update",
                json={
                    "key": key,
                    "data": data,
                    "new_data": new_data
                },
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")
                return await resp.json()

    async def get_from_storage(self, key: str) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"{self.endpoint}/storage",
                json={
                    "key": key
                },
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")
                return await resp.json()

    async def answer_tool(self, event: ToolEvent, function: typing.Callable) -> ToolAnswer:
        try:
            response = await function(data=event.tool.arguments, chat_id=event.chat_id)

            if response in [None, ""]:
                response = "function returned nothing"

            elif not isinstance(response, str):
                response = str(response)

            return ToolAnswer(
                id=event.tool.id,
                name=event.tool.name,
                text=response
            )

        except Exception as err:
            self.log.exception(err)

            return ToolAnswer(
                id=event.tool.id,
                name=event.tool.name,
                text="function returned nothing"
            )

    async def dispatch_event(self, event: ToolEvent):
        callback = self.callbacks.get(event.tool.name)

        if not callback:
            self.log.warning(f"Can't find callback function \"{event.tool.name}\" in {self.callbacks}")

            return ToolAnswer(
                id=event.tool.id,
                name=event.tool.name,
                text="function not binded"
            )

        self.log.debug(f"Dispatching event -> {event} -> {callback}")
        return await callback(event=event)

    async def handle_tools(self, tools: list[Tool], chat_id) -> list[ToolAnswer]:
        tool_answers = [
            await self.dispatch_event(ToolEvent(tool_name=tool.name, tool=tool, chat_id=chat_id))
            for tool in tools
        ]

        return tool_answers

    async def request(self, request: SendMessageRequest) -> AgentResponse:
        self.log.debug(f"Sending request -> {request.to_dict()}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.endpoint}/chat",
                json=request.to_dict(),
                raise_for_status=False
            ) as resp:

                self.log.debug(f"Got response -> {await resp.text()}")

                response = await resp.json()
                agent_response = AgentResponse(**response["data"])

                return agent_response

    async def send(self, chat_id: str, text: str = None, context: dict = {}, tool_answers: list[ToolAnswer] = []) -> AgentResponse:
        agent_response = await self.request(SendMessageRequest(chat_id=chat_id, text=text, context=context, tool_answers=tool_answers))

        if agent_response.type == AgentResponseType.answer:
            return agent_response

        tool_answers = await self.handle_tools(agent_response.content, chat_id)

        return await self.send(chat_id, tool_answers=tool_answers)
