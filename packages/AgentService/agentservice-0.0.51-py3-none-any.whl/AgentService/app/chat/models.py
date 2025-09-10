
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class ToolAnswer(BaseModel):
    id: str
    name: str
    text: Optional[str] = None


class SendMessage(BaseModel):
    chat_id: str
    text: Optional[str] = None
    context: Dict = Field(default_factory=dict)
    tool_answers: List[ToolAnswer] = Field(default_factory=list)


class GetStorage(BaseModel):
    key: str


class AddStorage(BaseModel):
    key: str
    data: List[Dict] | Dict


class RemoveStorage(BaseModel):
    key: str
    data: List[Dict] | Dict


class UpdateStorage(BaseModel):
    key: str
    data: Dict
    new_data: Dict
