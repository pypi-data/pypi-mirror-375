
from pydantic import BaseModel


class AgentTool:
    name: str = "tool"
    description: str = "this is tool"
    parameters: BaseModel = None

    @property
    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.model_json_schema() if self.parameters else {},
        }
