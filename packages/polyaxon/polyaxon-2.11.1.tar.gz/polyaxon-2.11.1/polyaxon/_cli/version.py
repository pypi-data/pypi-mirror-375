import sys

import click

from clipped.formatting import Printer
from clipped.utils import indentation
from clipped.utils.dicts import dict_to_tabulate
from clipped.utils.versions import clean_version_for_check, compare_versions

from polyaxon import pkg
from polyaxon._cli.session import set_versions_config
from polyaxon._deploy.operators.pip import PipOperator
from polyaxon.logger import clean_outputs, logger

PROJECT_CLI_NAME = "polyaxon"


def pip_upgrade(project_name=PROJECT_CLI_NAME):
    PipOperator.execute(["install", "--upgrade", project_name], stream=True)
    Printer.print("polyaxon upgraded!")


def get_version(package: str, show_error: bool = True):
    try:
        import pkg_resources
    except ImportError:
        return

    try:
        return pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        if show_error:
            logger.error("`%s` is not installed", package)


def check_old_packages():
    pkg = "polyaxon-cli"
    if get_version(package=pkg, show_error=False):
        Printer.error(
            "Legacy package `{pkg}` is installed. Please run `pip uninstall {pkg}`".format(
                pkg=pkg
            ),
            sys_exit=True,
        )


def get_current_version():
    return pkg.VERSION


def check_cli_version(config, is_cli: bool = True):
    """Check if the current cli version satisfies the server requirements"""

    min_version = clean_version_for_check(config.min_version)
    latest_version = clean_version_for_check(config.latest_version)
    current_version = clean_version_for_check(config.current_version)
    if not min_version or not latest_version or not current_version:
        if is_cli:
            Printer.error(
                "Could not get the min/latest versions from compatibility API.",
                sys_exit=True,
            )
        else:
            return
    if compare_versions(current=current_version, reference=min_version, comparator="<"):
        Printer.print(
            "Your version of Polyaxon CLI ({}) is no longer supported.".format(
                config.current_version
            )
        )
        if click.confirm(
            "Do you want to upgrade to " "version {} now?".format(config.latest_version)
        ):
            pip_upgrade()
            sys.exit(0)
        else:
            indentation.puts(
                "To upgrade to the latest version `{}`, "
                "you can manually run:".format(config.latest_version)
            )
            with indentation.indent(4):
                indentation.puts("pip install -U polyaxon")

            sys.exit(0)
    elif compare_versions(
        current=current_version, reference=latest_version, comparator="<"
    ):
        indentation.puts(
            "New version of Polyaxon CLI ({}) is now available. To upgrade run:".format(
                config.latest_version
            )
        )
        with indentation.indent(4):
            indentation.puts("pip install -U polyaxon")
    elif compare_versions(
        current=current_version, reference=latest_version, comparator=">"
    ):
        indentation.puts(
            "Your version of CLI ({}) is ahead of the latest version "
            "supported by Polyaxon server ({}) on your cluster, "
            "and might be incompatible.".format(
                config.current_version, config.latest_version
            )
        )


@click.command()
@click.option(
    "--check", is_flag=True, default=False, help="Check compatibility versions."
)
@clean_outputs
def version(check):
    """Print the current version of the cli and platform."""
    check_old_packages()
    Printer.heading("Current cli version: {}".format(pkg.VERSION))
    if check:
        config = set_versions_config()
        Printer.heading("Platform version:")
        config_installation = (
            dict_to_tabulate(
                config.installation.to_dict(),
                humanize_values=True,
                exclude_attrs=["hmac", "auth", "host"],
            )
            if config.installation
            else {"Server": "not found or not deployed"}
        )
        Printer.dict_tabulate(config_installation)
        Printer.heading("Compatibility versions:")
        Printer.dict_tabulate(
            config.compatibility.to_dict() if config.compatibility else {}
        )
        check_cli_version(config)


@click.command()
@clean_outputs
def upgrade():
    """Install/Upgrade polyaxon cli."""
    try:
        pip_upgrade(PROJECT_CLI_NAME)
    except Exception as e:
        logger.error(e)
