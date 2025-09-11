from typing import Optional, List

from pydantic import Field, ConfigDict, BaseModel

from thestage.services.clients.thestage_api.dtos.entity_filter_request import EntityFilterRequest


class DeployInferenceModelToInstanceRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    modelSlug: Optional[str] = Field(None, alias='modelSlug')
    instanceRentedSlug: Optional[str] = Field(None, alias='instanceRentedSlug')
    selfhostedInstanceSlug: Optional[str] = Field(None, alias='selfhostedInstanceSlug')
    inferenceSimulatorSlug: Optional[str] = Field(None, alias='inferenceSimulatorSlug')