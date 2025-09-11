
from loguru import logger
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from AgentService.types.agent_tool import AgentTool
from AgentService.db import Db
from AgentService.dtypes.db import method as dmth
from AgentService.dtypes.storage import Storage


db = Db()


class FileSearchParameters(BaseModel):
    query: str = Field(..., description="Search query to find specific data")


class FileSearchTool(AgentTool):
    name = "file_search"
    description = "Function to search data in files"
    parameters = FileSearchParameters


async def search_in_files(data: str):
    storages: list[Storage] = await db.ex(dmth.GetMany(Storage))

    try:
        client = AsyncOpenAI()
        response = await client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "user", "content": data}
            ],
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [storage.id for storage in storages]
                }
            }
        )

        text = response.output_text

        logger.info(f"Searching with {data} in {storages} -> {text}")
        return text

    except Exception as err:
        logger.exception(err)

        return str(err)
