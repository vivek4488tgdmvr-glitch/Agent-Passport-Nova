from typing import Any
from pydantic import BaseModel, Field


class InputContract(BaseModel):
    type: str


class OutputContract(BaseModel):
    type: str


class BehaviorContract(BaseModel):
    input: InputContract
    output: OutputContract


class AgentInfo(BaseModel):
    id: str
    name: str
    version: str
    description: str = ""


class Identity(BaseModel):
    capabilities: list[str] = Field(default_factory=list)


class ToolContract(BaseModel):
    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_type: str = "json"


class ModelContract(BaseModel):
    interface_version: str = "1.0"
    provider: str = "any"
    model: str = "any"


class Runtime(BaseModel):
    api_version: str
    compatible: list[str] = Field(default_factory=list)


class Verification(BaseModel):
    required: list[str] = Field(default_factory=list)


class Passport(BaseModel):
    passport: dict[str, str]
    agent: AgentInfo
    identity: Identity
    behavior: BehaviorContract
    tools: list[ToolContract] = Field(default_factory=list)
    model: ModelContract = Field(default_factory=ModelContract)
    runtime: Runtime
    verification: Verification
