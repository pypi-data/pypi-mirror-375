from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectTaskEntity(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: Optional[int] = Field(None, alias='ID')
    title: Optional[str] = Field(None, alias='TITLE')
    status: Optional[str] = Field(None, alias='STATUS')
    docker_container_id: Optional[int] = Field(None, alias='DOCKER_CONTAINER_ID')
    docker_container_slug: Optional[str] = Field(None, alias='DOCKER_CONTAINER_UID')
    started_at: Optional[str] = Field(None, alias='STARTED AT')
    finished_at: Optional[str] = Field(None, alias='FINISHED_AT')
