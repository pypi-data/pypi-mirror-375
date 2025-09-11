import os

from typing import List, Optional

from clipped.utils.git import (
    add_remote,
    checkout_revision,
    get_code_reference,
    git_fetch,
    git_init,
    set_remote,
    update_submodules,
)
from clipped.utils.paths import check_or_create_path
from git import Repo as GitRepo

from polyaxon._client.init import get_client_or_raise
from polyaxon._env_vars.keys import (
    ENV_KEYS_GIT_CREDENTIALS,
    ENV_KEYS_GIT_CREDENTIALS_STORE,
    ENV_KEYS_SSH_PATH,
    ENV_KEYS_SSH_PRIVATE_KEY,
)
from polyaxon._schemas.lifecycle import V1Statuses
from polyaxon.exceptions import PolyaxonContainerException
from traceml.artifacts import V1ArtifactKind, V1RunArtifact


def has_cred_access() -> bool:
    return os.environ.get(ENV_KEYS_GIT_CREDENTIALS) is not None


def has_cred_store_access() -> bool:
    cred_store_path = os.environ.get(ENV_KEYS_GIT_CREDENTIALS_STORE)
    return bool(cred_store_path and os.path.exists(cred_store_path))


def has_ssh_access() -> bool:
    ssh_path = os.environ.get(ENV_KEYS_SSH_PATH)
    return bool(ssh_path and os.path.exists(ssh_path))


def get_ssh_cmd():
    ssh_path = os.environ.get(ENV_KEYS_SSH_PATH)
    ssh_key_name = os.environ.get(ENV_KEYS_SSH_PRIVATE_KEY, "id_rsa")
    return "ssh -i {}/{} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no".format(
        ssh_path, ssh_key_name
    )


def get_clone_url(url: str) -> str:
    if not url:
        raise ValueError(
            "Git initializer requires a valid url, received {}".format(url)
        )

    if has_cred_access():
        if "https" in url:
            _url = url.replace("https://", "")
        elif url.startswith("git@") or url.endswith(".git"):
            _url = url.replace("git@", "")
            if _url.endswith(".git"):
                _url = ".git".join(_url.split(".git")[:-1])
            _url = _url.replace(":", "/")
        else:
            _url = url
        creds = os.environ.get(ENV_KEYS_GIT_CREDENTIALS)
        # Add user:pass to the git url
        return "https://{}@{}".format(creds, _url)
    if has_cred_store_access():
        if url.startswith("git@") or url.endswith(".git"):
            _url = url.replace("git@", "")
            if _url.endswith(".git"):
                _url = ".git".join(_url.split(".git")[:-1])
            _url = _url.replace(":", "/")
            return "https://{}".format(_url)
        return url
    if has_ssh_access() and "http" in url:
        if "https" in url:
            _url = url.replace("https://", "")
        elif "http" in url:
            _url = url.replace("http://", "")
        else:
            _url = url
        parts = _url.split("/")
        _url = "{}:{}".format(parts[0], "/".join(parts[1:]))
        if _url.endswith(".git"):
            _url = ".git".join(_url.split(".git")[:-1])
        return "git@{}.git".format(_url)

    return url


def clone_git_repo(
    repo_path: str, url: str, flags: Optional[List[str]] = None
) -> GitRepo:
    if has_ssh_access():
        return GitRepo.clone_from(
            url=url,
            to_path=repo_path,
            multi_options=flags,
            env={"GIT_SSH_COMMAND": get_ssh_cmd()},
        )
    return GitRepo.clone_from(url=url, to_path=repo_path, multi_options=flags)


def clone_and_checkout_git_repo(
    repo_path: str,
    clone_url: str,
    revision: str,
    flags: Optional[List[str]] = None,
):
    clone_git_repo(repo_path=repo_path, url=clone_url, flags=flags)
    if revision:
        checkout_revision(repo_path=repo_path, revision=revision)
        if flags and "--recurse-submodules" in flags:
            update_submodules(repo_path=repo_path)


def fetch_git_repo(
    repo_path: str,
    clone_url: str,
    revision: str,
    flags: Optional[List[str]] = None,
):
    check_or_create_path(repo_path, is_dir=True)
    git_init(repo_path)
    add_remote(repo_path, clone_url)
    env = None
    if has_ssh_access():
        env = {"GIT_SSH_COMMAND": get_ssh_cmd()}
    git_fetch(repo_path=repo_path, revision=revision, flags=flags, env=env)
    if flags and "--recurse-submodules" in flags:
        update_submodules(repo_path=repo_path)


def create_code_repo(
    repo_path: str,
    url: str,
    revision: str,
    connection: Optional[str] = None,
    flags: Optional[List[str]] = None,
):
    run_client = get_client_or_raise()

    try:
        clone_url = get_clone_url(url)
    except Exception as e:
        if run_client:
            run_client.log_status(
                status=V1Statuses.WARNING,
                reason="GitInitializer",
                message="Error parsing git url. "
                "Please check the git init container's logs for more details.",
            )
        raise PolyaxonContainerException("Error parsing url: {}.".format(url)) from e

    try:
        if flags and "--experimental-fetch" in flags:
            flags.remove("--experimental-fetch")
            fetch_git_repo(
                repo_path=repo_path, clone_url=clone_url, revision=revision, flags=flags
            )
        else:
            clone_and_checkout_git_repo(
                repo_path=repo_path, clone_url=clone_url, revision=revision, flags=flags
            )
    except Exception as e:
        if run_client:
            run_client.log_status(
                status=V1Statuses.WARNING,
                reason="GitInitializer",
                message="Error cloning git repo. "
                "Please check the git init container's logs for more details.",
            )
        raise e

    # Update remote
    set_remote(repo_path=repo_path, url=url)

    if not run_client:
        return

    code_ref = get_code_reference(path=repo_path, url=url)
    artifact_run = V1RunArtifact.construct(
        name=code_ref.get("commit"),
        kind=V1ArtifactKind.CODEREF,
        connection=connection,
        summary=code_ref,
        is_input=True,
    )
    run_client.log_artifact_lineage(artifact_run)
