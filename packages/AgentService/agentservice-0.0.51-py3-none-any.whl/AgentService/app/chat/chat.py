
import fastapi

from AgentService.config import Config
from AgentService.dtypes.response import OkResponse

from .models import SendMessage


chat_router = fastapi.APIRouter(prefix="/chat")


@chat_router.post("")
async def send_message(request: SendMessage):
    agent = Config().agent

    response = await agent.answer(
        chat_id=request.chat_id,
        text=request.text,
        context=request.context,
        tool_answers=list(map(lambda x: x.dict(), request.tool_answers))
    )

    return OkResponse(
        data=response
    ).to_dict()
