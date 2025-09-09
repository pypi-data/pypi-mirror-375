from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DockerContainerEntity(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    slug: Optional[str] = Field(None, alias='UNIQUE ID')
    status: Optional[str] = Field(None, alias='STATUS')
    title: Optional[str] = Field(None, alias='TITLE')
    instance_type: Optional[str] = Field(None, alias='INSTANCE TYPE')
    instance_slug: Optional[str] = Field(None, alias='INSTANCE UNIQUE ID')
