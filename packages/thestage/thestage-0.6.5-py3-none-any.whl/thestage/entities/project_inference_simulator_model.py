from typing import Optional, Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class ProjectInferenceSimulatorModelEntity(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: Optional[int] = Field(None, alias='ID')
    slug: Optional[str] = Field(None, alias='UNIQUE_ID')
    status: Optional[str] = Field(None, alias='STATUS')
    commit_hash: Optional[str] = Field(None, alias='COMMIT_HASH')
    environment_metadata: Optional[Dict[str, Any]] = Field(None, alias='ENVIRONMENT_METADATA')