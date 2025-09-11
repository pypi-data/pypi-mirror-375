import os
import sys

import click

from clipped.formatting import Printer
from clipped.utils import indentation
from urllib3.exceptions import HTTPError

from polyaxon._cli.errors import handle_cli_error
from polyaxon._cli.options import OPTIONS_PROJECT
from polyaxon._env_vars.getters import get_project_or_local
from polyaxon._managers.git import GitConfigManager
from polyaxon._managers.ignore import IgnoreConfigManager
from polyaxon._managers.project import ProjectConfigManager
from polyaxon._polyaxonfile import check_polyaxonfile
from polyaxon._schemas.types import V1GitType
from polyaxon._utils import cli_constants
from polyaxon._utils.cache import get_local_project
from polyaxon.client import ProjectClient
from polyaxon.exceptions import ApiException
from polyaxon.logger import clean_outputs


def create_init_file() -> bool:
    if os.path.exists(cli_constants.INIT_FILE_PATH):
        return False

    with open(cli_constants.INIT_FILE_PATH, "w") as f:
        f.write(cli_constants.INIT_FILE_TEMPLATE)

    return True


def create_polyaxonfile():
    if os.path.isfile(cli_constants.INIT_FILE_PATH):
        try:
            _ = check_polyaxonfile(cli_constants.INIT_FILE_PATH)  # noqa
            Printer.success("A valid polyaxonfile.yaml was found in this project.")
        except Exception as e:
            handle_cli_error(e, message="A Polyaxonfile was found but it is not valid.")
            sys.exit(1)
    else:
        create_init_file()
        # if we are here the file was not created
        if not os.path.isfile(cli_constants.INIT_FILE_PATH):
            Printer.error(
                "Something went wrong, init command did not create a file.\n"
                "Possible reasons: you don't have enough rights to create the file."
            )
            sys.exit(1)

        Printer.success(
            "{} was created successfully.".format(cli_constants.INIT_FILE_PATH)
        )


@click.command()
@click.option(
    *OPTIONS_PROJECT["args"],
    type=str,
    help="To enable local cache in this folder, "
    "the project name to initialize, e.g. 'mnist' or 'acme/mnist'.",
)
@click.option(
    "--git-connection",
    type=str,
    help="Optional git connection to use for the interactive mode and to "
    "automatically injecting code references in your operation manifests.",
)
@click.option(
    "--git-url",
    type=str,
    help="Optional git url to use for the interactive mode and for "
    "automatically injecting code references in your operation manifests. "
    "If no git-connection is passed, this url must point to a public repo,"
    "If a connection is passed and if it has a git url reference in the schema "
    "it will be patched with this url.",
)
@click.option(
    "--polyaxonfile",
    is_flag=True,
    default=False,
    show_default=False,
    help="Init a polyaxon file in this project.",
)
@click.option(
    "--polyaxonignore",
    is_flag=True,
    default=False,
    show_default=False,
    help="Init a polyaxonignore file in this project.",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Automatic yes to prompts. "
    'Assume "yes" as answer to all prompts and run non-interactively.',
)
@clean_outputs
def init(project, git_connection, git_url, polyaxonfile, polyaxonignore, yes):
    """Initialize a new local project and cache directory.

    Note: Make sure to add the local cache `.polyaxon`
    to your `.gitignore` and `.dockerignore` files.
    """
    if not any([project, git_connection, git_url, polyaxonfile, polyaxonignore]):
        Printer.warning(
            "`polyaxon init` did not receive any valid option.",
            command_help="polyaxon init",
        )
    if project:
        owner, _, project_name = get_project_or_local(project, is_cli=True)
        try:
            polyaxon_client = ProjectClient(
                owner=owner, project=project_name, manual_exceptions_handling=True
            )
            polyaxon_client.refresh_data()
        except (ApiException, HTTPError) as e:
            Printer.error(
                "Make sure you have a project with this name `{}`".format(project)
            )
            handle_cli_error(
                e,
                message="You can a create new project with this command: "
                "polyaxon project create "
                "--name={} [--description=...] [--tags=...]".format(project_name),
            )
            sys.exit(1)
        init_project = False
        if ProjectConfigManager.is_initialized():
            local_project = get_local_project(is_cli=True)
            Printer.warning(
                "Warning! This project is already initialized with the following project:"
            )
            with indentation.indent(4):
                indentation.puts("Owner: {}".format(local_project.owner))
                indentation.puts("Project: {}".format(local_project.name))
            if yes or click.confirm(
                "Would you like to override this current config?", default=False
            ):
                init_project = True
        else:
            init_project = True

        if init_project:
            ProjectConfigManager.purge(visibility=ProjectConfigManager.Visibility.LOCAL)
            config = polyaxon_client.client.sanitize_for_serialization(
                polyaxon_client.project_data
            )
            ProjectConfigManager.set_config(
                config, init=True, visibility=ProjectConfigManager.Visibility.LOCAL
            )
            Printer.success("Project was initialized")
            Printer.heading(
                "Make sure to add the local cache `.polyaxon` "
                "to your `.gitignore` and `.dockerignore` files."
            )
        else:
            Printer.heading("Project config was not changed.")

    if git_connection or git_url:
        init_git = False
        if GitConfigManager.is_initialized():
            Printer.warning(
                "Warning! A {} file was found.".format(
                    GitConfigManager.CONFIG_FILE_NAME
                )
            )
            if yes or click.confirm("Would you like to override it?", default=False):
                init_git = True
        else:
            init_git = True

        if init_git:
            GitConfigManager.purge(visibility=GitConfigManager.Visibility.LOCAL)
            config = GitConfigManager.CONFIG(
                connection=git_connection,
                git=V1GitType(url=git_url) if git_url else None,
            )
            GitConfigManager.set_config(config=config, init=True)
            Printer.success(
                "New {} file was created.".format(GitConfigManager.CONFIG_FILE_NAME)
            )
        else:
            Printer.heading(
                "{} file was not changed.".format(GitConfigManager.CONFIG_FILE_NAME)
            )

    if polyaxonfile:
        create_polyaxonfile()

    if polyaxonignore:
        init_ignore = False
        if IgnoreConfigManager.is_initialized():
            Printer.warning(
                "Warning! A {} file was found.".format(
                    IgnoreConfigManager.CONFIG_FILE_NAME
                )
            )
            if yes or click.confirm("Would you like to override it?", default=False):
                init_ignore = True
        else:
            init_ignore = True

        if init_ignore:
            IgnoreConfigManager.init_config()
            Printer.success(
                "New {} file was created.".format(IgnoreConfigManager.CONFIG_FILE_NAME)
            )
        else:
            Printer.heading(
                "{} file was not changed.".format(IgnoreConfigManager.CONFIG_FILE_NAME)
            )
