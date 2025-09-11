import os

from typing import Optional

from clipped.config.contexts import get_project_path, get_temp_path
from clipped.utils.enums import get_enum_value

from polyaxon._env_vars.keys import (
    ENV_KEYS_ARCHIVES_ROOT,
    ENV_KEYS_ARTIFACTS_ROOT,
    ENV_KEYS_CONTEXT_ROOT,
    ENV_KEYS_OFFLINE_ROOT,
)

CONTEXT_RELATED_RUNS = "_related_runs"

# Local contexts
CONTEXT_LOCAL_LINEAGES = "lineages.plx.json"
CONTEXT_LOCAL_CONTENT = "content.plx.json"
CONTEXT_LOCAL_README = "readme.plx.md"
CONTEXT_LOCAL_POLYAXONFILE = "polyaxonfile.plx.json"
CONTEXT_LOCAL_PROJECT = "project.plx.json"
CONTEXT_LOCAL_RUN = "run.plx.json"
CONTEXT_LOCAL_VERSION = "version.plx.json"

CONTEXT_ROOT = os.environ.get(ENV_KEYS_CONTEXT_ROOT, "/plx-context")
CONTEXT_MOUNT_CONFIGS = "{}/.configs".format(CONTEXT_ROOT)
CONTEXT_MOUNT_AUTH = "{}/.auth".format(CONTEXT_MOUNT_CONFIGS)
CONTEXT_MOUNT_ARTIFACTS = "{}/artifacts".format(CONTEXT_ROOT)
CONTEXT_MOUNT_FILE_WATCHER = "{}/.fs".format(CONTEXT_MOUNT_ARTIFACTS)
CONTEXT_MOUNT_ARTIFACTS_FORMAT = "{}/{{}}".format(CONTEXT_MOUNT_ARTIFACTS)
CONTEXT_MOUNT_ARTIFACTS_RELATED = CONTEXT_MOUNT_ARTIFACTS_FORMAT.format(
    CONTEXT_RELATED_RUNS
)
CONTEXT_MOUNT_ARTIFACTS_RELATED_FORMAT = "{}/{{}}".format(
    CONTEXT_MOUNT_ARTIFACTS_RELATED
)
CONTEXT_MOUNT_RUN_ASSETS_FORMAT = "{}/assets".format(CONTEXT_MOUNT_ARTIFACTS_FORMAT)
CONTEXT_MOUNT_RUN_OUTPUTS_FORMAT = "{}/outputs".format(CONTEXT_MOUNT_ARTIFACTS_FORMAT)
CONTEXT_MOUNT_RUN_EVENTS_FORMAT = "{}/events".format(CONTEXT_MOUNT_ARTIFACTS_FORMAT)
CONTEXT_MOUNT_RUN_SYSTEM_RESOURCES_EVENTS_FORMAT = "{}/resources".format(
    CONTEXT_MOUNT_ARTIFACTS_FORMAT
)
CONTEXT_MOUNT_SHM = "/dev/shm"
CONTEXT_MOUNT_DOCKER = "/var/run/docker.sock"

CONTEXT_TMP_POLYAXON_PATH = get_temp_path(".polyaxon")
CONTEXT_USER_POLYAXON_PATH = get_project_path(".polyaxon")

CONTEXT_TMP_RUNS_ROOT_FORMAT = os.environ.get(
    ENV_KEYS_ARCHIVES_ROOT, "/tmp/plx/.runs/{}"
)
CONTEXT_ARCHIVES_ROOT = os.environ.get(ENV_KEYS_ARCHIVES_ROOT, "/tmp/plx/archives")
CONTEXT_ARTIFACTS_ROOT = os.environ.get(ENV_KEYS_ARTIFACTS_ROOT, "/tmp/plx/artifacts")
CONTEXT_OFFLINE_ROOT = os.environ.get(ENV_KEYS_OFFLINE_ROOT, "/tmp/plx/offline")
CONTEXT_OFFLINE_FORMAT = "{}/{{}}".format(CONTEXT_OFFLINE_ROOT)
CONTEXT_ARTIFACTS_FORMAT = "{}/{{}}".format(CONTEXT_ARTIFACTS_ROOT)

CONTEXTS_OUTPUTS_SUBPATH_FORMAT = "{}/outputs"
CONTEXTS_EVENTS_SUBPATH_FORMAT = "{}/events"
CONTEXTS_SYSTEM_RESOURCES_EVENTS_SUBPATH_FORMAT = "{}/resources"


def get_offline_base_path(entity_kind: str, path: Optional[str] = None) -> str:
    from polyaxon._schemas.lifecycle import V1ProjectFeature

    path = path or CONTEXT_OFFLINE_ROOT
    entity_kind = "run" if entity_kind == V1ProjectFeature.RUNTIME else entity_kind
    return "{}/{}s".format(path.rstrip("/"), get_enum_value(entity_kind))


def get_offline_path(
    entity_value: str, entity_kind: str, path: Optional[str] = None
) -> str:
    from polyaxon._schemas.lifecycle import V1ProjectFeature

    path = path or CONTEXT_OFFLINE_ROOT
    entity_kind = "run" if entity_kind == V1ProjectFeature.RUNTIME else entity_kind
    return "{}/{}s/{}".format(
        path.rstrip("/"), get_enum_value(entity_kind), entity_value
    )


def mount_sandbox(path: Optional[str] = None):
    global CONTEXT_OFFLINE_ROOT
    global CONTEXT_ARTIFACTS_ROOT
    global CONTEXT_OFFLINE_FORMAT
    global CONTEXT_ARTIFACTS_FORMAT

    path = path or CONTEXT_OFFLINE_ROOT
    CONTEXT_OFFLINE_ROOT = path
    CONTEXT_ARTIFACTS_ROOT = path
    CONTEXT_OFFLINE_FORMAT = "{}/{{}}".format(CONTEXT_OFFLINE_ROOT)
    CONTEXT_ARTIFACTS_FORMAT = "{}/{{}}".format(CONTEXT_ARTIFACTS_ROOT)
    return path
