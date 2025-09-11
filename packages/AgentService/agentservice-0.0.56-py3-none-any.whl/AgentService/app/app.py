
import fastapi
import uvicorn

from AgentService.config import Config

from .chat import chat_router
from .storage import storage_router


app = fastapi.FastAPI()
app.include_router(chat_router)
app.include_router(storage_router)


def start_app():
    config = Config()
    uvicorn.run(app, host=config.app_host, port=config.app_port)
