
import enum

from AgentService.utils import now
from AgentService.dtypes.db import DatabaseItem

from AgentService.utils.jsonify import Jsonified


class MessageType(enum.Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    assistant_skip = "assistant_skip"
    tools = "tools"
    tool_answer = "tool_answer"


class Tool(Jsonified):
    def __init__(
        self,
        id: str,
        name: str,
        arguments: str
    ):

        self.id = id
        self.name = name
        self.arguments = arguments

        self.fields = ["id", "name", "arguments"]


class ToolAnswer(Jsonified):
    def __init__(
        self,
        id: str,
        name: str,
        text: str
    ):

        self.id = id
        self.name = name
        self.text = text

        self.fields = ["id", "name", "text"]


class SendMessageRequest(Jsonified):
    def __init__(
        self,
        chat_id: str,
        text: str = None,
        context: dict = {},
        tool_answers: list[ToolAnswer] = []
    ):

        self.chat_id = chat_id
        self.text = text
        self.context = context
        self.tool_answers = tool_answers

        self.fields = ["chat_id", "text", "context", "tool_answers"]


class Message(DatabaseItem):
    def __init__(
        self,
        id: str,
        chat_id: str,
        type: MessageType | str,
        text: str = None,
        tools: list[Tool] = None,
        tool_answer: ToolAnswer = None,
        created: int = None,
    ):

        if isinstance(tool_answer, dict):
            tool_answer = ToolAnswer(**tool_answer)

        self.id = id
        self.chat_id = chat_id
        self.text = text
        self.type = type if isinstance(type, MessageType) else MessageType(type)
        self.tools = list(map(lambda x: x if isinstance(x, Tool) else Tool(**x), tools)) if tools else []
        self.tool_answer = tool_answer
        self.created = created if created else now()

        self.fields = ["id", "chat_id", "text", "type", "tools", "tool_answer", "created"]

    @property
    def gpt_dump(self) -> dict:
        if self.type == MessageType.tools:
            return {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool.id,
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "arguments": tool.arguments
                        }
                    }
                    for tool in self.tools
                ]
            }

        elif self.type == MessageType.tool_answer:
            return {
                "role": "tool",
                "content": self.tool_answer.text,
                "tool_call_id": self.tool_answer.id,
                "name": self.tool_answer.name,
            }

        elif self.type == MessageType.assistant_skip:
            return {
                "role": "assistant",
                "content": self.text
            }

        else:
            return {
                "role": self.type.value,
                "content": self.text
            }
