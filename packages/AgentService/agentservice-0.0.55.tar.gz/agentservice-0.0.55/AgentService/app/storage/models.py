
from typing import Dict, List
from pydantic import BaseModel


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


class SearchStorage(BaseModel):
    query: str
