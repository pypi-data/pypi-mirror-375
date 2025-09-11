
import enum

from AgentService.utils import now
from AgentService.dtypes.db import DatabaseItem


class ChatStatus(enum.Enum):
    created = "created"
    error = "error"
    idle = "idle"
    tools = "tools"
    generating = "generating"
    finished = "finished"


class Chat(DatabaseItem):
    def __init__(
        self,
        id: str,
        chat_id: str,
        status: ChatStatus | str,
        created: int = None,
        data: dict = None
    ):

        self.id = id
        self.chat_id = chat_id
        self.status = status if isinstance(status, ChatStatus) else ChatStatus(status)
        self.data = data
        self.created = created if created else now()

        self.fields = ["id", "chat_id", "status", "data", "created"]
