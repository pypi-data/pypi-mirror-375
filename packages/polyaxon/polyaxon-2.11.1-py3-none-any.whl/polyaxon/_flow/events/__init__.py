from typing import List, Union

from clipped.compact.pydantic import StrictStr
from clipped.types.ref_or_obj import RefField

from polyaxon._contexts import refs as ctx_refs
from polyaxon._flow.events.enums import V1EventKind
from polyaxon._schemas.base import BaseSchemaModel


class V1EventTrigger(BaseSchemaModel, ctx_refs.RefMixin):
    """Events are an advanced triggering logic that users can take advantage of in addition to:
      * Manual triggers via API/CLI/UI.
      * Time-based triggers with schedules and crons.
      * Upstream triggers with upstream runs or upstream ops in DAGs.

    Events can be attached to an operation in the context of a DAG
    to extend the simple trigger process,
    this is generally important when the user defines a dependency between two operations
    and needs a run to start as soon as
    the upstream run generates an event instead of waiting until it reaches a final state.
    For instance, a usual use-case is to start a tensorboard as soon as training starts.
    In that case the downstream operation will watch for the `running` status.

    Events can be attached as well to a single operation
    to wait for an internal alert or external events,
    for instance if a user integrates Polyaxon with Github,
    they can trigger training as soon as Polyaxon is notified that a new git commit was created.

    Polyaxon provides several internal and external events that users
    can leverage to fully automate their usage of the platform:
      * "run_status_created"
      * "run_status_resuming"
      * "run_status_compiled"
      * "run_status_queued"
      * "run_status_scheduled"
      * "run_status_starting"
      * "run_status_initializing"
      * "run_status_running"
      * "run_status_processing"
      * "run_status_stopping"
      * "run_status_failed"
      * "run_status_stopped"
      * "run_status_succeeded"
      * "run_status_skipped"
      * "run_status_warning"
      * "run_status_unschedulable"
      * "run_status_upstream_failed"
      * "run_status_retrying"
      * "run_status_unknown"
      * "run_status_done"
      * "run_approved_actor"
      * "run_invalidated_actor"
      * "run_new_artifacts"
      * "connection_git_commit"
      * "connection_dataset_version"
      * "connection_registry_image"
      * "alert_info"
      * "alert_warning"
      * "alert_critical"
      * "model_version_new_metric"
      * "project_custom_event"
      * "org_custom_event"

    Args:
         kinds: List[str]
         ref: str

    > **Important**: Currently only events with prefix `run_status_*` are supported.

    ## YAML usage

    ```yaml
    >>> event:
    >>>   ref: {{ ops.upstream-operation }}
    >>>   kinds: [run_status_running]
    ```

    ```yaml
    >>> event:
    >>>   ref: {{ connections.git-repo-connection-name }}
    >>>   kinds: [connection_git_commit]
    ```

    ## Python usage

    ```python
    >>> from polyaxon.schemas import V1EventKind, V1EventTrigger
    >>> event1 = V1EventTrigger(
    >>>     ref="{{ ops.upstream-operation }}",
    >>>     kinds=[V1EventTrigger.RUN_STATUS_RUNNING],
    >>> )
    >>> event2 = V1EventTrigger(
    >>>     ref="{{ connections.git-repo-connection-name }}",
    >>>     kinds=[V1EventTrigger.CONNECTION_GIT_COMMIT],
    >>> )
    ```

    ## Fields

    ### kinds

    The trigger event kinds to watch, if any event is detected the operation defining the `events`
    section will be initiated.

    ```yaml
    >>> event:
    >>>   kinds: [run_status_running, run_status_done]
    ```

    > **Note**: Similar to trigger in DAGs, after an operation is initiated,
    > it will still have to validate the rest of the Polyaxonfile,
    > i.e. conditions, contexts, connections, ...

    ### ref

    A valid reference that Polyaxon can resolve the objects that will send the events to watch for.
    All supported events are prefixed with the object reference that can send such events.

    The `run_*` events can be referenced both by `runs.UUID` or
    `ops.OPERATION_NAME` if defined in the context of a DAG.

    ```yaml
    >>> event:
    >>>   ref: ops.upstream_operation_name
    ```
    """

    _IDENTIFIER = "event_trigger"

    kinds: List[Union[V1EventKind, RefField]]
    ref: StrictStr
