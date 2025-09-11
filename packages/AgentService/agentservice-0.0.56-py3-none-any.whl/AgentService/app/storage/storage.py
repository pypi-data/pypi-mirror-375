
import fastapi
import io
import json

from .models import GetStorage, AddStorage, RemoveStorage, UpdateStorage, SearchStorage

from AgentService.config import Config
from AgentService.db import Db
from AgentService.dtypes.db import method as dmth
from AgentService.dtypes.storage import StorageItem, Storage
from AgentService.dtypes.response import OkResponse, ErrResponse
from AgentService.utils.convert import string_to_uuid
from AgentService.agent.file_search import search_in_files


storage_router = fastapi.APIRouter(prefix="/storage")
db = Db()


async def get_packed_storage(key: str) -> io.BytesIO:
    storage_items: list[StorageItem] = await db.ex(dmth.GetMany(StorageItem, key=key))
    data = [
        {
            "text": item.data,
            "metadata": {"id": item.id}
        }
        for item in storage_items
    ]

    buffer = io.BytesIO()
    buffer.write((json.dumps(data, ensure_ascii=False)).encode("utf-8"))
    buffer.seek(0)

    return buffer


@storage_router.get("")
async def get_storage(request: GetStorage):
    key = request.key

    items: list[StorageItem] = await db.ex(dmth.GetMany(StorageItem, key=key))

    return OkResponse(
        data=items
    ).to_dict()


@storage_router.post("/add")
async def add_to_storage(request: AddStorage):
    key = request.key
    data = request.data

    agent = Config().agent

    if not isinstance(data, list):
        data = [data]

    storage: Storage = await db.ex(dmth.GetOne(Storage, key=key))
    if not storage:
        storage = await agent.create_storage(key=key)
        await db.ex(dmth.AddOne(Storage, storage))

    storage_items = [
        StorageItem(
            id=string_to_uuid(key+str(row)),
            key=key,
            data=row
        )
        for row in data
    ]
    await db.ex(dmth.AddMany(StorageItem, storage_items))

    buffer = await get_packed_storage(key)
    await agent.update_storage(buffer, storage.id)

    return OkResponse().to_dict()


@storage_router.post("/remove")
async def remove_from_storage(request: RemoveStorage):
    key = request.key
    data = request.data

    agent = Config().agent

    if not isinstance(data, list):
        data = [data]

    for item in data:
        item_id = string_to_uuid(key+str(item))

        storage_item: StorageItem = await db.ex(dmth.GetOne(StorageItem, key=key, id=item_id))
        if not storage_item:
            return ErrResponse(
                description=f"No such storage item -> {key} -> {item}@{item_id}"
            ).to_dict()

        await db.ex(dmth.RemoveOne(StorageItem, storage_item))

    storage: Storage = await db.ex(dmth.GetOne(Storage, key=key))
    buffer = await get_packed_storage(key)
    await agent.update_storage(buffer, storage.id)

    return OkResponse().to_dict()


@storage_router.post("/update")
async def update_storage(request: UpdateStorage):
    key = request.key
    data = request.data
    new_data = request.new_data

    agent = Config().agent

    item_id = string_to_uuid(key+str(data))

    storage_item: StorageItem = await db.ex(dmth.GetOne(StorageItem, key=key, id=item_id))
    if not storage_item:
        return ErrResponse(
            description=f"No such storage item -> {key} -> {data}:{item_id}"
        ).to_dict()

    await db.ex(dmth.RemoveOne(StorageItem, storage_item))

    storage_item.id = string_to_uuid(str(new_data))
    storage_item.data = new_data
    await db.ex(dmth.AddOne(StorageItem, storage_item))

    storage: Storage = await db.ex(dmth.GetOne(Storage, key=key))
    buffer = await get_packed_storage(key)
    await agent.update_storage(buffer, storage.id)

    return OkResponse().to_dict()


@storage_router.get("/search")
async def search_in_storage(request: SearchStorage):
    content = await search_in_files(request.query)

    return OkResponse(data=content).to_dict()
