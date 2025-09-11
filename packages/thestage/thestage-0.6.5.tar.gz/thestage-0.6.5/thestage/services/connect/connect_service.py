from typing import Optional
import typer

from thestage.cli_command import CliCommand
from thestage.cli_command_helper import check_command_permission
from thestage.i18n.translation import __
from thestage.services.clients.thestage_api.core.http_client_exception import HttpClientException
from thestage.services.clients.thestage_api.dtos.enums.container_status import DockerContainerStatus
from thestage.services.clients.thestage_api.dtos.enums.selfhosted_status import SelfhostedBusinessStatus
from thestage.services.clients.thestage_api.dtos.enums.instance_rented_status import InstanceRentedBusinessStatus
from thestage.services.abstract_service import AbstractService
from thestage.helpers.error_handler import error_handler
from thestage.services.clients.thestage_api.api_client import TheStageApiClient
from thestage.services.clients.thestage_api.dtos.enums.task_status import TaskStatus
from thestage.services.clients.thestage_api.dtos.instance_rented_response import InstanceRentedDto
from thestage.services.container.container_service import ContainerService
from thestage.services.instance.instance_service import InstanceService
from thestage.services.logging.logging_service import LoggingService
from thestage.services.task.dto.task_dto import TaskDto
from thestage.helpers.logger.app_logger import app_logger


class ConnectService(AbstractService):
    __thestage_api_client: TheStageApiClient = None
    __instance_service: InstanceService = None
    __container_service: ContainerService = None
    __logging_service: LoggingService = None

    def __init__(
            self,
            thestage_api_client: TheStageApiClient,
            instance_service: InstanceService,
            container_service: ContainerService,
            logging_service: LoggingService,
    ):
        super(ConnectService, self).__init__(
        )
        self.__thestage_api_client = thestage_api_client
        self.__instance_service = instance_service
        self.__container_service = container_service
        self.__logging_service = logging_service


    @error_handler()
    def connect_to_entity(
            self,
            uid: str,
            username: Optional[str],
            private_key_path: Optional[str],
    ):
        try:
            instance_selfhosted = self.__thestage_api_client.get_selfhosted_instance(instance_slug=uid)
        except HttpClientException as e:
            app_logger.warn(f"get_selfhosted_instance: code {e.get_status_code()}")
            instance_selfhosted = None

        try:
            instance_rented = self.__thestage_api_client.get_rented_instance(instance_slug=uid)
        except HttpClientException as e:
            app_logger.warn(f"get_rented_instance: code {e.get_status_code()}")
            instance_rented = None

        try:
            container = self.__thestage_api_client.get_container(container_slug=uid,)
        except HttpClientException as e:
            app_logger.warn(f"get_container: code {e.get_status_code()}")
            container = None

        task: Optional[TaskDto] = None
        if uid.isdigit():
            try:
                task_view_response = self.__thestage_api_client.get_task(task_id=int(uid))
            except HttpClientException as e:
                app_logger.warn(f"get_task error: code {e.get_status_code()}")
                task_view_response = None
            if task_view_response and task_view_response.task:
                task = task_view_response.task

        rented_exists = int(instance_rented is not None and instance_rented.frontend_status.status_key == InstanceRentedBusinessStatus.ONLINE)
        selfhosted_exists = int(instance_selfhosted is not None)
        container_exists = int(container is not None)
        task_exists = int(task is not None)

        rented_presence = int(rented_exists and instance_rented.frontend_status.status_key == InstanceRentedBusinessStatus.ONLINE)
        selfhosted_presence = int(selfhosted_exists and instance_selfhosted.frontend_status.status_key == SelfhostedBusinessStatus.RUNNING)
        container_presence = int(container_exists and (container.frontend_status.status_key == DockerContainerStatus.RUNNING or container.frontend_status.status_key == DockerContainerStatus.BUSY))
        task_presence = int(task_exists and task.frontend_status.status_key in [TaskStatus.RUNNING, TaskStatus.SCHEDULED])

        if rented_exists:
            typer.echo(__("Found a rented instance with the provided UID in status: '%rented_status%'", {"rented_status": instance_rented.frontend_status.status_translation}))

        if selfhosted_exists:
            typer.echo(__("Found a self-hosted instance with the provided UID in status: '%selfhosted_status%'", {"selfhosted_status": instance_selfhosted.frontend_status.status_translation}))

        if container_exists:
            typer.echo(__("Found a docker container with the provided UID in status: '%container_status%'", {"container_status": container.frontend_status.status_translation}))

        if task_exists:
            typer.echo(__("Found a task with the provided ID in status: '%task_status%'", {"task_status": task.frontend_status.status_translation}))

        if (rented_presence + selfhosted_presence + container_presence + task_presence) > 1:
            typer.echo("Provided identifier caused ambiguity")
            typer.echo("Consider running a dedicated command to connect to the entity you need")
            raise typer.Exit(code=1)

        if (rented_presence + selfhosted_presence + container_presence + task_presence) == 0:
            typer.echo("There is nothing to connect to with the provided identifier")
            raise typer.Exit(code=1)

        if rented_presence:
            check_command_permission(CliCommand.INSTANCE_RENTED_CONNECT)
            typer.echo("Connecting to rented instance...")
            self.__instance_service.connect_to_rented_instance(
                instance_rented_slug=uid,
                input_ssh_key_path=private_key_path
            )

        if container_presence:
            check_command_permission(CliCommand.CONTAINER_CONNECT)
            typer.echo("Connecting to docker container...")
            self.__container_service.connect_to_container(
                container_uid=uid,
                username=username,
                input_ssh_key_path=private_key_path
            )

        if selfhosted_presence:
            check_command_permission(CliCommand.INSTANCE_SELF_HOSTED_CONNECT)
            typer.echo("Connecting to self-hosted instance...")

            self.__instance_service.connect_to_selfhosted_instance(
                selfhosted_instance_slug=uid,
                username=username,
                input_ssh_key_path=private_key_path
            )

        if task_presence:
            typer.echo(__("Connecting to task..."))
            self.__logging_service.stream_task_logs_with_controls(task_id=int(uid))


    @error_handler()
    def upload_ssh_key(self, public_key_contents: str, instance_slug: Optional[str]):
        instance_rented: Optional[InstanceRentedDto] = None
        if instance_slug:
            try:
                instance_rented = self.__thestage_api_client.get_rented_instance(instance_slug=instance_slug)
            except HttpClientException as e:
                instance_rented = None

            # if no instances found - exit 1
            if instance_rented is None:
                typer.echo(f"No rented instance found with matching unique ID '{instance_slug}'")
                raise typer.Exit(1)

        note_to_send: Optional[str] = None

        is_user_already_has_key_response = self.__thestage_api_client.is_user_has_ssh_public_key(
            public_key=public_key_contents
        )

        ssh_key_pair_id = is_user_already_has_key_response.sshKeyPairId
        is_adding_key_to_user = not is_user_already_has_key_response.isUserHasPublicKey

        if is_adding_key_to_user and not note_to_send:
            note_to_send: str = typer.prompt(
                text=__('SSH key will be added to your profile. Please provide a title for this key'),
                show_choices=False,
                type=str,
                show_default=False,
            )

        if not is_adding_key_to_user and not instance_rented:
            typer.echo("Key already exists on your profile")

        if is_adding_key_to_user:
            add_ssh_key_to_user_response = self.__thestage_api_client.add_public_ssh_key_to_user(
                public_key=public_key_contents,
                note=note_to_send
            )
            typer.echo(f"Public key '{note_to_send}' added to your profile")
            ssh_key_pair_id = add_ssh_key_to_user_response.sshKeyPairId

        if instance_rented:
            self.__thestage_api_client.add_public_ssh_key_to_instance_rented(
                instance_rented_id=instance_rented.id,
                ssh_key_pair_id=ssh_key_pair_id
            )

            if instance_rented.frontend_status.status_key != InstanceRentedBusinessStatus.ONLINE:
                typer.echo(f"Rented instance '{instance_rented.slug}' status is '{instance_rented.frontend_status.status_translation}'. Key will be added as soon as it is back online.")
            else:
                typer.echo(f"Public key added to rented instance '{instance_rented.slug}'")
