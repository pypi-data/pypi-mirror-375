
from AgentService.dtypes.db import DatabaseItem


class Storage(DatabaseItem):
    def __init__(
        self,
        id: str,
        key: str
    ):

        self.id = id
        self.key = key

        self.fields = ["id", "key"]


class StorageItem(DatabaseItem):
    def __init__(
        self,
        id: str,
        key: str,
        data: dict
    ):

        self.id = id
        self.key = key
        self.data = data

        self.fields = ["id", "key", "data"]
