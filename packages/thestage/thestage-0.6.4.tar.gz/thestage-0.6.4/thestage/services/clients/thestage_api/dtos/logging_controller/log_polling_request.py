from typing import Optional

from pydantic import Field, ConfigDict, BaseModel


class LogPollingRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    taskId: Optional[int] = Field(None, alias='taskId')
    inferenceSimulatorId: Optional[int] = Field(None, alias='inferenceSimulatorId')
    lastLogId: Optional[str] = Field(None, alias='lastLogId')
    dockerContainerId: Optional[int] = Field(None, alias='dockerContainerId')
    lastLogTimestamp: Optional[str] = Field(None, alias='lastLogTimestamp')
