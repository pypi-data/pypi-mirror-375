
import re
from pathlib import Path
from typing import Optional, List

from thestage.cli_command import CliCommand
from thestage.cli_command_helper import get_command_metadata, check_command_permission
from thestage.services.clients.thestage_api.dtos.enums.container_pending_action import DockerContainerAction
from thestage.services.clients.thestage_api.dtos.container_response import DockerContainerDto
from thestage.i18n.translation import __
from thestage.services.container.container_service import ContainerService
from thestage.helpers.logger.app_logger import app_logger
from thestage.controllers.utils_controller import validate_config_and_get_service_factory, get_current_directory

import typer

from thestage.services.logging.logging_service import LoggingService

app = typer.Typer(no_args_is_help=True, help=__("Manage containers"))


@app.command(name='ls', help=__("List containers"), **get_command_metadata(CliCommand.CONTAINER_LS))
def list_containers(
        row: int = typer.Option(
            5,
            '--row',
            '-r',
            help=__("Set number of rows displayed per page"),
            is_eager=False,
        ),
        page: int = typer.Option(
            1,
            '--page',
            '-p',
            help=__("Set starting page for displaying output"),
            is_eager=False,
        ),
        project_uid: str = typer.Option(
            None,
            '--project-uid',
            '-puid',
            help=__("Filter containers by project unique ID"),
            is_eager=False,
        ),
        statuses: List[str] = typer.Option(
            None,
            '--status',
            '-s',
            help=__("Filter by status, use --status all to list all containers"),
            is_eager=False,
        ),
):
    command_name = CliCommand.CONTAINER_LS
    app_logger.info(f'Running {command_name}')
    check_command_permission(command_name)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()
    container_service.print_container_list(
        row=row,
        page=page,
        project_uid=project_uid,
        statuses=statuses,
    )

    typer.echo(__("Containers listing complete"))
    raise typer.Exit(0)


@app.command(name="info", no_args_is_help=True, help=__("Get container info"), **get_command_metadata(CliCommand.CONTAINER_INFO))
def container_info(
        container_uid: Optional[str] = typer.Argument(hidden=False, help=__("Container unique ID")),
):
    command_name = CliCommand.CONTAINER_INFO
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_container(
        container_slug=container_uid,
    )

    if not container:
        typer.echo(__("Container not found: %container_item%", {'container_item': str(container_uid) if container_uid else ''}))
        raise typer.Exit(1)

    typer.echo(__("STATUS: %status%", {'status': str(container.frontend_status.status_translation if container and container.frontend_status else 'UNKNOWN')}))
    typer.echo(__("UNIQUE ID: %slug%", {'slug': str(container.slug)}))
    typer.echo(__("TITLE: %title%", {'title': str(container.title)}))
    typer.echo(__("IMAGE: %image%", {'image': str(container.docker_image)}))

    if container.instance_rented:
        typer.echo(
            __("RENTED SERVER INSTANCE UNIQUE ID: %instance_slug%", {'instance_slug': str(container.instance_rented.slug)})
        )
        typer.echo(
            __("RENTED SERVER INSTANCE STATUS: %instance_status%",
               {'instance_status': str(container.instance_rented.frontend_status.status_translation if container.instance_rented.frontend_status else 'UNKNOWN')})
        )

    if container.selfhosted_instance:
        typer.echo(
            __("SELF-HOSTED INSTANCE UNIQUE ID: %instance_slug%", {'instance_slug': str(container.selfhosted_instance.slug)})
        )
        typer.echo(
            __("SELF-HOSTED INSTANCE STATUS: %instance_status%",
               {'instance_status': str(container.selfhosted_instance.frontend_status.status_translation if container.selfhosted_instance.frontend_status else 'UNKNOWN')})
        )

    if container.mappings and (container.mappings.port_mappings or container.mappings.directory_mappings):
        if container.mappings.port_mappings:
            typer.echo(__("CONTAINER PORT MAPPING:"))
            for src, dest in container.mappings.port_mappings.items():
                typer.echo(f"    {src} : {dest}")

        if container.mappings.directory_mappings:
            typer.echo(__("CONTAINER DIRECTORY MAPPING:"))
            for src, dest in container.mappings.directory_mappings.items():
                typer.echo(f"    {src} : {dest}")

    raise typer.Exit(0)


@app.command(name="connect", no_args_is_help=True, help=__("Connect to container"), **get_command_metadata(CliCommand.CONTAINER_CONNECT))
def container_connect(
        container_uid: Optional[str] = typer.Argument(help=__("Container unique ID"),),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Username for the server instance (required when connecting to self-hosted instance)"),
            is_eager=False,
        ),
        private_ssh_key_path: str = typer.Option(
            None,
            "--private-key-path",
            "-pk",
            help=__("Path to private key that will be accepted by remote server (optional)"),
            is_eager=False,
        ),
):
    command_name = CliCommand.CONTAINER_CONNECT
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    if private_ssh_key_path and not Path(private_ssh_key_path).is_file():
        typer.echo(f'No file found at provided path {private_ssh_key_path}')
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container_service.connect_to_container(
        container_uid=container_uid,
        username=username,
        input_ssh_key_path=private_ssh_key_path,
    )

    app_logger.info(f'Stop connect to container')
    raise typer.Exit(0)


@app.command(name="upload", no_args_is_help=True, help=__("Upload file to container"), **get_command_metadata(CliCommand.CONTAINER_UPLOAD))
def upload_file(
        source_path: str = typer.Argument(help=__("Source file path"),),
        destination: Optional[str] = typer.Argument(help=__("Destination directory path in container. Format: container_uid:/path/to/file"),),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Username for the server instance (required when connecting to self-hosted instance)"),
            is_eager=False,
        ),
):
    command_name = CliCommand.CONTAINER_UPLOAD
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    container_args = re.match(r"^([\w\W]+?):([\w\W]+)$", destination)

    if container_args is None:
        typer.echo(__('Container unique ID and source file path are required as the second argument'))
        typer.echo(__('Example: container_uid:/path/to/file'))
        raise typer.Exit(1)
    container_slug = container_args.groups()[0]
    destination_path = container_args.groups()[1].rstrip("/")

    if not container_slug:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_container(
        container_slug=container_slug,
    )

    if container:
        container_service.check_if_container_running(
            container=container
        )

        typer.echo(__("Uploading file(s) to container '%container-slug%'", {'container-slug': container_slug}))

        container_service.put_file_to_container(
            container=container,
            src_path=source_path,
            destination_path=destination_path,
            username_param=username,
            copy_only_folder_contents=source_path.endswith("/")
        )
    else:
        typer.echo(__("Container not found: %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End send files to container')
    raise typer.Exit(0)


@app.command(name="download", no_args_is_help=True, help=__("Download file from container"), **get_command_metadata(CliCommand.CONTAINER_DOWNLOAD))
def download_file(
        source_path: str = typer.Argument(help=__("Source file path in container. Format: container_uid:/path/to/file"),),
        destination_path: str = typer.Argument(help=__("Destination directory path on local machine"),),
        username: Optional[str] = typer.Option(
            None,
            '--username',
            '-u',
            help=__("Username for the server instance (required when connecting to self-hosted instance)"),
            is_eager=False,
        ),
):
    command_name = CliCommand.CONTAINER_DOWNLOAD
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    container_args = re.match(r"^([\w\W]+?):([\w\W]+)$", source_path)

    if container_args is None:
        typer.echo(__('Container unique ID and source directory path are required as the first argument'))
        typer.echo(__('Example: container-uid:/path/to/file'))
        raise typer.Exit(1)
    container_slug = container_args.groups()[0]
    source_path = container_args.groups()[1]

    if not container_slug:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container: Optional[DockerContainerDto] = container_service.get_container(
        container_slug=container_slug,
    )

    if container:
        container_service.check_if_container_running(
            container=container
        )

        typer.echo(__("Downloading files from container: '%container-slug%'", {'container-slug': container_slug}))

        container_service.get_file_from_container(
            container=container,
            src_path=source_path,
            destination_path=destination_path.rstrip("/"),
            username_param=username,
            copy_only_folder_contents=source_path.endswith("/"),
        )
    else:
        typer.echo(__("Container not found: %container_item%", {'container_item': container_slug}))

    app_logger.info(f'End download files from container')
    raise typer.Exit(0)


@app.command(name="start", no_args_is_help=True, help=__("Start container"), **get_command_metadata(CliCommand.CONTAINER_START))
def start_container(
        container_uid: Optional[str] = typer.Argument(help=__("Container unique ID"), ),
):
    command_name = CliCommand.CONTAINER_START
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container_service.request_docker_container_action(
        container_uid=container_uid,
        action=DockerContainerAction.START
    )

    app_logger.info(f'End start container')
    raise typer.Exit(0)


@app.command(name="stop", no_args_is_help=True, help=__("Stop container"), **get_command_metadata(CliCommand.CONTAINER_STOP))
def stop_container(
        container_uid: Optional[str] = typer.Argument(help=__("Container unique ID"), ),
):
    command_name = CliCommand.CONTAINER_STOP
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container_service.request_docker_container_action(
        container_uid=container_uid,
        action=DockerContainerAction.STOP
    )

    app_logger.info(f'End stop container')
    raise typer.Exit(0)


@app.command(name="restart", no_args_is_help=True, help=__("Restart container"), **get_command_metadata(CliCommand.CONTAINER_RESTART))
def restart_container(
        container_uid: Optional[str] = typer.Argument(help=__("Container unique ID"), ),
):
    command_name = CliCommand.CONTAINER_RESTART
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    container_service: ContainerService = service_factory.get_container_service()

    container_service.request_docker_container_action(
        container_uid=container_uid,
        action=DockerContainerAction.RESTART
    )

    app_logger.info(f'End stop container')
    raise typer.Exit(0)


@app.command(name="logs", no_args_is_help=True, help=__("Stream real-time Docker container logs or view last logs for a container"), **get_command_metadata(CliCommand.CONTAINER_LOGS))
def container_logs(
        container_uid: Optional[str] = typer.Argument(help=__("Container unique id")),
        logs_number: Optional[int] = typer.Option(
            None,
            '--number',
            '-n',
            help=__("Display a number of latest log entries. No real-time stream if provided."),
            is_eager=False,
        ),
):
    command_name = CliCommand.CONTAINER_LOGS
    app_logger.info(f'Running {command_name} from {get_current_directory()}')
    check_command_permission(command_name)

    if not container_uid:
        typer.echo(__('Container unique ID is required'))
        raise typer.Exit(1)

    service_factory = validate_config_and_get_service_factory()
    logging_service: LoggingService = service_factory.get_logging_service()

    if logs_number is None:
        logging_service.stream_container_logs_with_controls(
            container_uid=container_uid
        )
    else:
        logging_service.print_last_container_logs(container_uid=container_uid, logs_number=logs_number)

    app_logger.info(f'Container logs - end')
    raise typer.Exit(0)
