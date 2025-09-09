from typing import Optional

from pydantic import Field, ConfigDict, BaseModel


class ProjectStartInferenceSimulatorRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    projectSlug: str = Field(None, alias='projectSlug')
    instanceRentedUId: Optional[str] = Field(None, alias='instanceRentedUId')
    selfhostedInstanceUId: Optional[str] = Field(None, alias='selfhostedInstanceUId')
    commitHash: Optional[str] = Field(None, alias='commitHash')
    inferenceDir: Optional[str] = Field(None, alias='inferenceDir')
    isSkipInstallation: Optional[bool] = Field(False, alias='isSkipInstallation')