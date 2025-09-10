import click

from clipped.formatting import Printer

from polyaxon._cli.options import OPTIONS_MODEL_VERSION, OPTIONS_NAME, OPTIONS_PROJECT
from polyaxon._cli.project_versions import (
    copy_project_version,
    delete_project_version,
    get_project_version,
    get_project_version_stages,
    list_project_versions,
    open_project_version_dashboard,
    pull_one_or_many_project_versions,
    push_one_or_many_project_versions,
    register_project_version,
    stage_project_version,
    transfer_project_version,
    update_project_version,
)
from polyaxon._env_vars.getters import get_project_or_local
from polyaxon._schemas.lifecycle import V1ProjectVersionKind, V1Stages
from polyaxon.logger import clean_outputs


@click.group()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.pass_context
@clean_outputs
def models(ctx, project, version):
    """Commands for managing model versions."""
    ctx.obj = ctx.obj or {}
    if project or version:
        Printer.warning(
            "Passing arguments to command groups is deprecated and will be removed in v2! "
            "Please use arguments on the sub-command directly: `polyaxon ops SUB_COMMAND --help`"
        )
    ctx.obj["project"] = project
    if ctx.invoked_subcommand not in ["ls"]:
        ctx.obj["version"] = version


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(
    "--query",
    "-q",
    type=str,
    help="To filter the model versions based on this query spec.",
)
@click.option(
    "--sort",
    "-s",
    type=str,
    help="To order the model versions based on the sort spec.",
)
@click.option("--limit", type=int, help="To limit the list of model versions.")
@click.option("--offset", type=int, help="To offset the list of model versions.")
@click.pass_context
@clean_outputs
def ls(ctx, project, query, sort, limit, offset):
    """List model versions by owner or owner/model.

    Examples:

    \b
    $ polyaxon models ls -p=project-name

    \b
    $ polyaxon models ls -p=acme/project-name
    """
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )

    list_project_versions(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        query=query,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option("--description", type=str, help="Description of the version.")
@click.option("--tags", type=str, help="Tags of the version (comma separated values).")
@click.option(
    "--content",
    type=str,
    help="Additional content/metadata to save with the model version.",
)
@click.option("--run-uid", type=str, help="The run to promote as a model version.")
@click.option(
    "--artifacts",
    "artifacts_",
    type=str,
    help="The artifacts to link to this model version.",
)
@click.option(
    "--connection", type=str, help="The connection to link to this model version."
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Flag to force register if the version already exists.",
)
@click.pass_context
@clean_outputs
def register(
    ctx,
    project,
    version,
    description,
    tags,
    content,
    run_uid,
    artifacts_,
    connection,
    force,
):
    """Push a new model version.
    If the name corresponds to an existing model version,
    it will raise an error or it will update the version if `--force` is provided.

    Examples:

    \b
    $ polyaxon models register --version=version-name --run-uid=uuid

    \b
    $ polyaxon models register --content='{"foo": "bar"}' --project=ml-project --description="..."

    \b
    $ polyaxon models register -p ml-project -ver latest --run-uid=uuid --artifacts=model-ref

    \b
    $ polyaxon models register -p owner/name -ver v1 --tags="tag1,tag2"
    """
    version = version or ctx.obj.get("version")
    owner, team, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    register_project_version(
        owner=owner,
        team=team,
        project_name=project_name,
        version=version,
        kind=V1ProjectVersionKind.MODEL,
        description=description,
        tags=tags,
        content=content,
        run=run_uid,
        connection=connection,
        artifacts=artifacts_,
        force=force,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--to-project",
    "-to",
    help="The project to transfer the version to.",
)
@click.option(
    *OPTIONS_NAME["args"],
    type=str,
    help="Name of the model version, must be unique within the same project.",
)
@click.option(
    "--description", type=str, help="Optional new description of the version."
)
@click.option(
    "--tags",
    type=str,
    help="Optional new tags of the version (comma separated values).",
)
@click.option(
    "--content",
    type=str,
    help="Optional new content/metadata (Json object) to save with the model version.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Flag to force copy if the version already exists.",
)
@click.pass_context
@clean_outputs
def copy(
    ctx,
    project,
    version,
    to_project,
    name,
    description,
    tags,
    content,
    force,
):
    """Copy a model version.
    If the name corresponds to an existing model version,
    it will raise an error or it will update the version if `--force` is provided.

    Examples:

    \b
    $ polyaxon models copy --version=version-name --to-project dest-project

    \b
    $ polyaxon models copy --project=ml-project -to dest-project --force

    \b
    $ polyaxon models copy -p ml-project --content='{"foo": "bar"}' -ver latest

    \b
    $ polyaxon models copy -p owner/name -ver v1 --tags="tag1,tag2" --name new-v1
    """
    version = version or ctx.obj.get("version")
    owner, team, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    copy_project_version(
        owner=owner,
        team=team,
        project_name=project_name,
        version=version,
        kind=V1ProjectVersionKind.MODEL,
        to_project=to_project,
        name=name,
        description=description,
        tags=tags,
        content=content,
        force=force,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.pass_context
@clean_outputs
def get(ctx, project, version):
    """Get info for a model version by name.

    Examples:

    \b
    $ polyaxon models get  // returns `latest` in current project

    \b
    $ polyaxon models get --project=my-project --version=test-version

    \b
    $ polyaxon models get -p owner/my-project -ver rc12
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, team, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    get_project_version(
        owner=owner,
        team=team,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.pass_context
@clean_outputs
def stages(ctx, project, version):
    """List stages information for a model version by name, name & version, owner/name & tag.

    Examples:

    \b
    $ polyaxon models stages // returns `latest` in current project

    \b
    $ polyaxon models stages --project=my-project --version=test-version

    \b
    $ polyaxon models stages -p owner/my-project -ver rc12
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    get_project_version_stages(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Automatic yes to prompts. "
    'Assume "yes" as answer to all prompts and run non-interactively.',
)
@click.pass_context
@clean_outputs
def delete(ctx, project, version, yes):
    """Delete a model version.

    Examples:

    \b
    $ polyaxon models delete  // delete `latest` in current project

    \b
    $ polyaxon models delete --project=my-project --version=test-version

    \b
    $ polyaxon models get -p owner/my-project -ver rc12
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    delete_project_version(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        yes=yes,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    *OPTIONS_NAME["args"],
    type=str,
    help="Name of the model version, must be unique within the same project.",
)
@click.option("--description", type=str, help="Description of the model version.")
@click.option(
    "--tags", type=str, help="Tags of the model version (comma separated values)."
)
@click.pass_context
@clean_outputs
def update(ctx, project, version, name, description, tags):
    """Update model version.

    Uses /docs/core/cli/#caching

    Examples:

    \b
    $ polyaxon models update --version=foobar --description="..."

    \b
    $ polyaxon models update -p mike1/foobar -ver current-name --name=new-name

    \b
    $ polyaxon models update --tags="foo, bar"
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    update_project_version(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        name=name,
        description=description,
        tags=tags,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--to",
    "-to",
    type=click.Choice(V1Stages.to_list(), case_sensitive=True),
    help="Stage to transition to.",
)
@click.option(
    "--reason",
    type=str,
    help="Reason or service to set with this stage change. "
    "Default: UserStageUpdate, e.g. CustomAlertTrigger.",
)
@click.option(
    "--message", type=str, help="Additional information to set with this stage change."
)
@click.pass_context
@clean_outputs
def stage(ctx, project, version, to, reason, message):
    """Update stage for a model version.

    Uses /docs/core/cli/#caching

    Examples:

    \b
    $ polyaxon models stage -ver rc12 -to production

    \b
    $ polyaxon models stage -p acme/foobar -ver rc12 --to=staging --reason GithubAction --message="Use carefully!"
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    stage_project_version(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        to=to,
        reason=reason,
        message=message,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--to-project",
    "-to",
    help="The project to transfer the version to.",
)
@click.pass_context
@clean_outputs
def transfer(ctx, project, version, to_project):
    """Transfer the version to a destination project under the same owner/organization.

    Uses /docs/core/cli/#caching

    Examples:

    \b
    $ polyaxon models transfer -ver rc12 -to dest-project

    \b
    $ polyaxon models transfer -p acme/foobar -ver rc12 --to-project=dest-project
    """
    version = version or ctx.obj.get("version") or "latest"
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    transfer_project_version(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        to_project=to_project,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--all-versions",
    "-a",
    is_flag=True,
    default=False,
    help="To pull all versions.",
)
@click.option(
    "--query", "-q", type=str, help="To filter the versions based on a query spec."
)
@click.option("--limit", "-l", type=int, help="To limit the list of runs.")
@click.option("--offset", "-off", type=int, help="To offset the list of runs.")
@click.option(
    "--path",
    "--path-to",
    type=click.Path(exists=False),
    help="Optional path where the model versions are persisted, "
    "default value is taken from the env var: `POLYAXON_OFFLINE_ROOT`.",
)
@click.option(
    "--no-artifacts",
    is_flag=True,
    default=False,
    help="To disable downloading the run's artifacts and only persist the metadata.",
)
@click.pass_context
@clean_outputs
def pull(
    ctx,
    project,
    version,
    all_versions,
    query,
    limit,
    offset,
    path,
    no_artifacts,
):
    """Package and download a model version or multiple model versions
    to a local path with or without artifacts.

    Uses /docs/core/cli/#caching

    Examples:

    \b
    $ polyaxon models pull -ver rc12

    \b
    $ polyaxon models pull -p acme/foobar -q "stage: production, name: %-v1%"

    \b
    $ polyaxon models pull -p acme/foobar -a --path /tmp/versions
    """
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    pull_one_or_many_project_versions(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        all_versions=all_versions,
        query=query,
        limit=limit,
        offset=offset,
        path=path,
        download_artifacts=not no_artifacts,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--all-versions",
    "-a",
    is_flag=True,
    default=False,
    help="To push all versions.",
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    default=False,
    help="To clean the version(s) local data after syncing.",
)
@click.option(
    "--path",
    "--path-from",
    type=click.Path(exists=False),
    help="Optional path where the model versions are persisted, "
    "default value is taken from the env var: `POLYAXON_OFFLINE_ROOT`.",
)
@click.option(
    "--reset-project",
    is_flag=True,
    default=False,
    help="Optional, to ignore the owner/project of the local "
    "version and use the owner/project provided or resolved from the current project.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Flag to force register if the version already exists.",
)
@click.pass_context
@clean_outputs
def push(
    ctx,
    project,
    version,
    all_versions,
    clean,
    path,
    reset_project,
    force,
):
    """Push local packaged model version or multiple model versions to a remove server.

    Uses /docs/core/cli/#caching

    Examples:

    \b
    $ polyaxon models push -ver rc12

    \b
    $ polyaxon models push -p acme/foobar --path /tmp/versions

    \b
    $ polyaxon models pull -p acme/foobar -a --path /tmp/versions
    """
    owner, _, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    push_one_or_many_project_versions(
        owner=owner,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        all_versions=all_versions,
        path=path,
        clean=clean,
        force=force,
        reset_project=reset_project,
    )


@models.command()
@click.option(*OPTIONS_PROJECT["args"], **OPTIONS_PROJECT["kwargs"])
@click.option(*OPTIONS_MODEL_VERSION["args"], **OPTIONS_MODEL_VERSION["kwargs"])
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Automatic yes to prompts. "
    'Assume "yes" as answer to all prompts and run non-interactively.',
)
@click.option(
    "--url",
    is_flag=True,
    default=False,
    help="Print the url of the dashboard for this model version.",
)
@click.pass_context
@clean_outputs
def dashboard(ctx, project, version, yes, url):
    """Open this model version's dashboard details in browser."""
    version = version or ctx.obj.get("version") or "latest"
    owner, team, project_name = get_project_or_local(
        project or ctx.obj.get("project"), is_cli=True
    )
    open_project_version_dashboard(
        owner=owner,
        team=team,
        project_name=project_name,
        kind=V1ProjectVersionKind.MODEL,
        version=version,
        url=url,
        yes=yes,
    )
