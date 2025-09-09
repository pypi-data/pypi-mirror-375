from typing import Optional, List, Tuple, Dict, Iterator

import httpx

from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.core.api_client_core import TheStageApiClientCore
from thestage.services.clients.thestage_api.dtos.docker_container_controller.docker_container_list_request import \
    DockerContainerListRequest
from thestage.services.clients.thestage_api.dtos.docker_container_controller.docker_container_list_response import \
    DockerContainerListResponse
from thestage.services.clients.thestage_api.dtos.entity_filter_request import EntityFilterRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.deploy_inference_model_to_instance_request import \
    DeployInferenceModelToInstanceRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.deploy_inference_model_to_instance_response import \
    DeployInferenceModelToInstanceResponse
from thestage.services.clients.thestage_api.dtos.inference_controller.deploy_inference_model_to_sagemaker_request import \
    DeployInferenceModelToSagemakerRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.deploy_inference_model_to_sagemaker_response import \
    DeployInferenceModelToSagemakerResponse
from thestage.services.clients.thestage_api.dtos.inference_controller.get_inference_simulator_request import \
    GetInferenceSimulatorRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.get_inference_simulator_response import \
    GetInferenceSimulatorResponse
from thestage.services.clients.thestage_api.dtos.inference_controller.inference_simulator_list_for_project_request import \
    InferenceSimulatorListForProjectRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.inference_simulator_list_for_project_response import \
    InferenceSimulatorListForProjectResponse
from thestage.services.clients.thestage_api.dtos.inference_controller.inference_simulator_model_list_for_project_request import \
    InferenceSimulatorModelListForProjectRequest
from thestage.services.clients.thestage_api.dtos.inference_controller.inference_simulator_model_list_for_project_response import \
    InferenceSimulatorModelListForProjectResponse
from thestage.services.clients.thestage_api.dtos.inference_simulator_model_response import \
    InferenceSimulatorModelStatusMapperResponse
from thestage.services.clients.thestage_api.dtos.inference_simulator_response import \
    InferenceSimulatorStatusMapperResponse
from thestage.services.clients.thestage_api.dtos.logging_controller.log_polling_request import LogPollingRequest
from thestage.services.clients.thestage_api.dtos.logging_controller.log_polling_response import LogPollingResponse
from thestage.services.clients.thestage_api.dtos.logging_controller.user_logs_query_request import UserLogsQueryRequest
from thestage.services.clients.thestage_api.dtos.logging_controller.user_logs_query_response import \
    UserLogsQueryResponse
from thestage.services.clients.thestage_api.dtos.paginated_entity_list import PaginatedEntityList
from thestage.services.clients.thestage_api.dtos.project_controller.project_get_deploy_ssh_key_request import \
    ProjectGetDeploySshKeyRequest
from thestage.services.clients.thestage_api.dtos.project_controller.project_get_deploy_ssh_key_response import \
    ProjectGetDeploySshKeyResponse
from thestage.services.clients.thestage_api.dtos.project_controller.project_push_inference_simulator_model_request import \
    ProjectPushInferenceSimulatorModelRequest
from thestage.services.clients.thestage_api.dtos.project_controller.project_push_inference_simulator_model_response import \
    ProjectPushInferenceSimulatorModelResponse
from thestage.services.clients.thestage_api.dtos.project_controller.project_run_task_request import \
    ProjectRunTaskRequest
from thestage.services.clients.thestage_api.dtos.project_controller.project_run_task_response import \
    ProjectRunTaskResponse
from thestage.services.clients.thestage_api.dtos.project_controller.project_start_inference_simulator_request import \
    ProjectStartInferenceSimulatorRequest
from thestage.services.clients.thestage_api.dtos.project_controller.project_start_inference_simulator_response import \
    ProjectStartInferenceSimulatorResponse
from thestage.services.clients.thestage_api.dtos.project_response import ProjectDto, ProjectViewResponse
from thestage.services.clients.thestage_api.dtos.selfhosted_instance_response import SelfHostedInstanceListResponse, \
    SelfHostedInstanceDto, SelfHostedRentedItemResponse, SelfHostedRentedRentedBusinessStatusMapperResponse
from thestage.services.clients.thestage_api.dtos.container_param_request import DockerContainerActionRequestDto
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto, \
    DockerContainerViewResponse, ContainerBusinessStatusMapperResponse
from thestage.entities.enums.order_direction_type import OrderDirectionType
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.add_ssh_key_to_user_request import \
    AddSshKeyToUserRequest
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.add_ssh_key_to_user_response import \
    AddSshKeyToUserResponse
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.add_ssh_public_key_to_instance_request import \
    AddSshPublicKeyToInstanceRequest
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.add_ssh_public_key_to_instance_response import \
    AddSshPublicKeyToInstanceResponse
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.is_user_has_public_ssh_key_request import \
    IsUserHasSshPublicKeyRequest
from thestage.services.clients.thestage_api.dtos.ssh_key_controller.is_user_has_public_ssh_key_response import \
    IsUserHasSshPublicKeyResponse
from thestage.services.clients.thestage_api.dtos.task_controller.task_list_for_project_request import \
    TaskListForProjectRequest
from thestage.services.clients.thestage_api.dtos.task_controller.task_list_for_project_response import \
    TaskListForProjectResponse
from thestage.services.clients.thestage_api.dtos.task_controller.task_status_localized_map_response import \
    TaskStatusLocalizedMapResponse
from thestage.services.clients.thestage_api.dtos.task_controller.task_view_response import TaskViewResponse
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedListResponse, \
    InstanceRentedDto, InstanceRentedItemResponse, InstanceRentedBusinessStatusMapperResponse

from thestage.services.clients.thestage_api.dtos.base_response import TheStageBaseResponse
from thestage.services.config_provider.config_provider import ConfigProvider
from thestage.services.project.dto.inference_simulator_dto import InferenceSimulatorDto
from thestage.services.project.dto.inference_simulator_model_dto import InferenceSimulatorModelDto
from thestage.services.task.dto.task_dto import TaskDto


class TheStageApiClient(TheStageApiClientCore):
    __config_provider: ConfigProvider = None

    def __init__(
            self,
            config_provider: ConfigProvider,
    ):
        # TODO this is super bullshit, remove all abstract classes
        super().__init__(url=config_provider.get_config().main.thestage_api_url)
        self.__config_provider = config_provider

    def get_task(
            self,
            task_id: int,
    ) -> Optional[TaskViewResponse]:
        data = {
            "taskId": task_id,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/view',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = TaskViewResponse.model_validate(response) if response else None
        return result if result and result.is_success else None

    def get_task_list_for_project(
            self,
            project_slug: str,
            page: int = 1,
            limit: int = 10,
    ) -> Optional[PaginatedEntityList[TaskDto]]:
        request = TaskListForProjectRequest(
            projectSlug=project_slug,
            entityFilterRequest=EntityFilterRequest(
                orderByField="id",
                orderByDirection=OrderDirectionType.DESC,
                page=page,
                limit=limit,
            ),
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/task/list-for-project',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = TaskListForProjectResponse.model_validate(response) if response else None
        return result.tasks if result and result.is_success else None

    def get_inference_simulator_list_for_project(
            self,
            project_slug: str,
            statuses: List[str] = [],
            page: int = 1,
            limit: int = 10,
    ) -> Optional[PaginatedEntityList[InferenceSimulatorDto]]:
        request = InferenceSimulatorListForProjectRequest(
            projectSlug=project_slug,
            statuses=statuses,
            entityFilterRequest=EntityFilterRequest(
                orderByField="id",
                orderByDirection=OrderDirectionType.DESC,
                page=page,
                limit=limit,
            ),
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/inference-simulator/list',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )
        result = InferenceSimulatorListForProjectResponse.model_validate(response) if response else None
        return result.inferenceSimulators if result and result.is_success else None

    def get_inference_simulator_model_list_for_project(
            self,
            project_slug: str,
            statuses: Optional[List[str]] = None,
            page: int = 1,
            limit: int = 10,
    ) -> Optional[PaginatedEntityList[InferenceSimulatorModelDto]]:
        request = InferenceSimulatorModelListForProjectRequest(
            projectSlug=project_slug,
            statuses=statuses,
            entityFilterRequest=EntityFilterRequest(
                orderByField="id",
                orderByDirection=OrderDirectionType.DESC,
                page=page,
                limit=limit,
            ),
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/inference-simulator-model/list',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )
        result = InferenceSimulatorModelListForProjectResponse.model_validate(response) if response else None
        return result.inferenceSimulatorModels if result and result.is_success else None

    def get_rented_instance_list(
            self,
            statuses: List[str],
            query: Optional[str] = None,
            page: int = 1,
            limit: int = 10,
    ) -> PaginatedEntityList[InstanceRentedDto]:
        data = {
            #"statuses": [item.value for item in statuses],
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "queryString": query
        }

        if statuses:
            data['businessStatuses'] = statuses

        response = self._request(
            method='POST',
            url='/user-api/v2/instance-rented/list',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = InstanceRentedListResponse.model_validate(response) if response else None
        return result.paginated_list if result and result.paginated_list else ([], None)

    def get_rented_business_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v2/instance-rented/business-status-localized-map',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = InstanceRentedBusinessStatusMapperResponse.model_validate(response) if response else None

        return data.instance_rented_business_status_map if data else None

    def get_task_localized_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v1/task/status-localized-mapping',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = TaskStatusLocalizedMapResponse.model_validate(response) if response else None

        return data.taskStatusMap if data else None

    def get_rented_instance(
            self,
            instance_slug: Optional[str] = None,
            instance_id: Optional[int] = None,
    ) -> Optional[InstanceRentedDto]:
        if not instance_slug and not instance_id:
            return None

        data = {
            "instanceRentedSlug": instance_slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v2/instance-rented/view-by-slug',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return InstanceRentedItemResponse.model_validate(response).instance_rented if response else None

    def get_selfhosted_instance(
            self,
            instance_slug: Optional[str] = None,
            instance_id: Optional[int] = None,
    ) -> Optional[SelfHostedInstanceDto]:
        if not instance_slug and not instance_id:
            return None

        data = {
            "selfhostedInstanceSlug": instance_slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v2/self-hosted-instance/view-by-slug',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return SelfHostedRentedItemResponse.model_validate(response).selfhosted_instance if response else None

    def get_selfhosted_instance_list(
            self,
            statuses: List[str],
            query: Optional[str] = None,
            page: int = 1,
            limit: int = 10,
    ) -> PaginatedEntityList[SelfHostedInstanceDto]:
        data = {
            #"statuses": [item.value for item in statuses] if statuses else [],
            "entityFilterRequest": {
                "orderByField": "id",
                "orderByDirection": "DESC",
                "page": page,
                "limit": limit
            },
            "queryString": query
        }

        if statuses:
            data['businessStatuses'] = statuses

        response = self._request(
            method='POST',
            url='/user-api/v2/self-hosted-instance/list',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = SelfHostedInstanceListResponse.model_validate(response) if response else None
        return result.paginated_list if result and result.paginated_list else ([], None)

    def get_selfhosted_business_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v2/self-hosted-instance/business-status-localized-map',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = SelfHostedRentedRentedBusinessStatusMapperResponse.model_validate(response) if response else None
        return data.selfhosted_instance_business_status_map if data else None


    def cancel_task(
            self,
            task_id: int,
    ) -> Optional[TheStageBaseResponse]:
        data = {
            "taskId": task_id,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/task/cancel-task',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = TheStageBaseResponse.model_validate(response) if response else None
        return result if result else None

    def get_container_list(
            self,
            project_id: Optional[int] = None,
            statuses: List[str] = [],
            page: int = 1,
            limit: int = 10,
    ) -> PaginatedEntityList[DockerContainerDto]:
        request = DockerContainerListRequest(
            statuses=statuses,
            projectId=project_id,
            entityFilterRequest=EntityFilterRequest(
                orderByField="id",
                orderByDirection=OrderDirectionType.DESC,
                page=page,
                limit=limit,
            ),
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/list',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token
        )

        result = DockerContainerListResponse.model_validate(response) if response else None
        # return result.paginatedList.entities, result.paginatedList.pagination_data.total_pages if result and result.is_success else None
        return result.paginatedList if result and result.is_success else None

    def get_container(
            self,
            container_slug: Optional[str] = None,
            container_id: Optional[int] = None,
    ) -> Optional[DockerContainerDto]:
        if not container_slug and not container_id:
            return None

        if container_id:
            data = {
                "dockerContainerId": container_id,
            }
        else:
            data = {
                "dockerContainerSlug": container_slug,
            }

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/view',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return DockerContainerViewResponse.model_validate(response).docker_container if response else None

    def container_action(
            self,
            request_param: DockerContainerActionRequestDto,
    ) -> TheStageBaseResponse:

        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/action',
            data=request_param.model_dump(by_alias=True),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = TheStageBaseResponse.model_validate(response) if response else None
        return result

    def get_container_business_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v1/docker-container/status-localized-mapping',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = ContainerBusinessStatusMapperResponse.model_validate(response) if response else None
        return data.docker_container_status_map if data else None

    def get_project_by_slug(self, slug: str) -> Optional[ProjectDto]:
        data = {
            "projectSlug": slug,
        }

        response = self._request(
            method='POST',
            url='/user-api/v1/project/view-by-slug',
            data=data,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = ProjectViewResponse.model_validate(response) if response else None
        project = ProjectDto.model_validate(result.project) if result else None
        return project if result and result.is_success else None

    def get_project_deploy_ssh_key(self, slug: str) -> str:
        request = ProjectGetDeploySshKeyRequest(
            projectSlug=slug
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/get-deploy-ssh-key',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = ProjectGetDeploySshKeyResponse.model_validate(response) if response else None
        return result.privateKey if result and result.is_success else None

    def execute_project_task(
            self,
            project_slug: str,
            run_command: str,
            task_title: str,
            docker_container_slug: Optional[str] = None,
            commit_hash: Optional[str] = None,
    ) -> Optional[ProjectRunTaskResponse]:
        request = ProjectRunTaskRequest(
            projectSlug=project_slug,
            dockerContainerSlug=docker_container_slug,
            commitHash=commit_hash,
            runCommand=run_command,
            taskTitle=task_title,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/execute-task',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return ProjectRunTaskResponse.model_validate(response) if response else None

    async def poll_logs_httpx(self, docker_container_id: Optional[int], last_log_timestamp: str,
                              last_log_id: str, task_id: Optional[int] = None,
                              inference_simulator_id: Optional[int] = None) -> Optional[LogPollingResponse]:
        request_headers = {'Content-Type': 'application/json'}
        token = self.__config_provider.get_config().main.thestage_auth_token
        if token: request_headers['Authorization'] = f"Bearer {token}"

        request = LogPollingRequest(
            inferenceSimulatorId=inference_simulator_id,
            taskId=task_id,
            dockerContainerId=docker_container_id,
            lastLogTimestamp=last_log_timestamp,
            lastLogId=last_log_id
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self._get_host()}/user-api/v1/logging/poll",
                headers=request_headers,
                json=request.model_dump(),
                timeout=3.5
            )

            return LogPollingResponse.model_validate(response.json()) if response else None

    def add_public_ssh_key_to_user(self, public_key: str, note: str) -> AddSshKeyToUserResponse:
        request = AddSshKeyToUserRequest(
            sshKey=public_key,
            note=note
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/ssh-key/add-public-key-to-user',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = AddSshKeyToUserResponse.model_validate(response) if response else None
        return result

    def is_user_has_ssh_public_key(self, public_key: str) -> IsUserHasSshPublicKeyResponse:
        request = IsUserHasSshPublicKeyRequest(
            sshKey=public_key,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/ssh-key/is-user-has-public-ssh-key',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = IsUserHasSshPublicKeyResponse.model_validate(response) if response else None
        return result

    def add_public_ssh_key_to_instance_rented(self, instance_rented_id: int,
                                              ssh_key_pair_id: int) -> AddSshPublicKeyToInstanceResponse:
        request = AddSshPublicKeyToInstanceRequest(
            instanceRentedId=instance_rented_id,
            sshPublicKeyId=ssh_key_pair_id,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/ssh-key/add-public-ssh-key-to-instance-rented',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = AddSshPublicKeyToInstanceResponse.model_validate(response) if response else None
        return result

    def start_project_inference_simulator(
            self,
            project_slug: str,
            commit_hash: Optional[str] = None,
            rented_instance_unique_id: Optional[str] = None,
            self_hosted_instance_unique_id: Optional[str] = None,
            inference_dir: Optional[str] = None,
            is_skip_installation: Optional[bool] = False,
    ) -> Optional[ProjectStartInferenceSimulatorResponse]:
        request = ProjectStartInferenceSimulatorRequest(
            projectSlug=project_slug,
            commitHash=commit_hash,
            instanceRentedUId=rented_instance_unique_id,
            selfhostedInstanceUId=self_hosted_instance_unique_id,
            inferenceDir=inference_dir,
            isSkipInstallation=is_skip_installation,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/inference-simulator/create',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return ProjectStartInferenceSimulatorResponse.model_validate(response) if response else None

    def push_project_inference_simulator_model(
            self,
            slug: str,
    ) -> Optional[ProjectPushInferenceSimulatorModelResponse]:
        request = ProjectPushInferenceSimulatorModelRequest(
            slug=slug,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/project/inference-simulator/push-model',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        return ProjectPushInferenceSimulatorModelResponse.model_validate(response) if response else None

    def get_inference_simulator_business_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v1/inference-simulator/status-localized-mapping',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = InferenceSimulatorStatusMapperResponse.model_validate(response) if response else None

        return data.inference_simulator_status_map if data else None

    def get_inference_simulator_model_business_status_map(self) -> Optional[Dict[str, str]]:
        response = self._request(
            method='POST',
            url='/user-api/v1/inference-simulator-model/status-localized-mapping',
            data=None,
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        data = InferenceSimulatorModelStatusMapperResponse.model_validate(response) if response else None

        return data.inference_simulator_model_status_map if data else None

    @error_handler()
    def get_inference_simulator(
            self,
            slug: str,
    ) -> Optional[GetInferenceSimulatorResponse]:
        request = GetInferenceSimulatorRequest(
            slug=slug,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/inference-simulator/get',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )
        return GetInferenceSimulatorResponse.model_validate(response) if response else None

    @error_handler()
    def deploy_inference_model_to_instance(
            self,
            unique_id: str,
            unique_id_with_timestamp: str,
            rented_instance_unique_id: Optional[str] = None,
            self_hosted_instance_unique_id: Optional[str] = None,

    ) -> Optional[DeployInferenceModelToInstanceResponse]:
        request = DeployInferenceModelToInstanceRequest(
            inferenceSimulatorSlug=unique_id_with_timestamp,
            modelSlug=unique_id,
            instanceRentedSlug=rented_instance_unique_id,
            selfhostedInstanceSlug=self_hosted_instance_unique_id
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/inference-simulator-model/deploy/instance',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )
        return DeployInferenceModelToInstanceResponse.model_validate(response) if response else None

    @error_handler()
    def deploy_inference_model_to_sagemaker(
            self,
            unique_id: str,
            arn: Optional[str] = None,
    ) -> Optional[DeployInferenceModelToSagemakerResponse]:
        request = DeployInferenceModelToSagemakerRequest(
            modelSlug=unique_id,
            arn=arn,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/inference-simulator-model/grant-user-arn-access',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )
        return DeployInferenceModelToSagemakerResponse.model_validate(response) if response else None

    def query_user_logs(self, limit: int, task_id: Optional[int] = None,
                        inference_simulator_id: Optional[int] = None,
                        container_id: Optional[int] = None) -> UserLogsQueryResponse:
        request = UserLogsQueryRequest(
            inferenceSimulatorId=inference_simulator_id,
            taskId=task_id,
            containerId=container_id,
            limit=limit,
            ascendingOrder=False,
        )

        response = self._request(
            method='POST',
            url='/user-api/v1/logging/query-user-logs',
            data=request.model_dump(),
            token=self.__config_provider.get_config().main.thestage_auth_token,
        )

        result = UserLogsQueryResponse.model_validate(response) if response else None
        return result
