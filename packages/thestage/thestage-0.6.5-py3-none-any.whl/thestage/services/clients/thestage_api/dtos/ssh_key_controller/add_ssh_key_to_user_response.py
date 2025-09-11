from typing import Optional

from pydantic import Field, ConfigDict

from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse
from thestage.services.task.dto.task_dto import TaskDto


class AddSshKeyToUserResponse(TheStageBaseResponse):
    model_config = ConfigDict(use_enum_values=True)

    sshKeyPairId: Optional[int] = Field(None, alias='sshKeyPairId')