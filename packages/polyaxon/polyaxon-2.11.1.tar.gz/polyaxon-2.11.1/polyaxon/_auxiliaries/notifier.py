from typing import Optional

from clipped.utils.versions import clean_version_post_suffix

from polyaxon import pkg
from polyaxon._containers.names import MAIN_JOB_CONTAINER
from polyaxon._containers.pull_policy import PullPolicy
from polyaxon._k8s import k8s_schemas
from polyaxon._schemas.services import BaseServiceConfig


def get_notifier_resources() -> k8s_schemas.V1ResourceRequirements:
    return k8s_schemas.V1ResourceRequirements(
        limits={"cpu": "1", "memory": "500Mi"},
        requests={"cpu": "0.1", "memory": "60Mi"},
    )


class V1PolyaxonNotifier(BaseServiceConfig):
    """Polyaxon notifier is a helper job that gets scheduled to handle post-done events
    and send webhooks for operations annotated with `hooks` or `notifications`.

    Polyaxon CE and Polyaxon Agent are deployed with default values for the notifier,
    however if you need to control or update one or several aspects
    of how the notifier is scheduled, this guide walks through the possible options.

    Args:
        image: str, optional.
        image_tag: str, optional.
        image_pull_policy: str, optional.
        resources: V1ResourceRequirements, optional.
        node_selector: Dict, optional
        affinity: V1Affinity, optional
        tolerations: List[V1Toleration], optional
        image_pull_secrets: List[str]

    ## YAML usage

    ```yaml
    >>> notifier:
    >>>   image: polyaxon/polyaxon-events-handlers
    >>>   imageTag: v1.x
    >>>   imagePullPolicy: IfNotPresent
    >>>   resources:
    >>>     requests:
    >>>       memory: "64Mi"
    >>>       cpu: "50m"
    >>>   nodeSelector:
    >>>     foo: bar
    ```

    ## Fields

    ### image

    The container image to use.

    ```yaml
    >>> notifier:
    >>>   image: polyaxon/polyaxon-events-handlers
    ```

    ### imageTag

    The container image tag to use.

    ```yaml
    >>> notifier:
    >>>   imageTag: dev
    ```

    ### imagePullPolicy

    The image pull policy to use, it must be a valid policy supported by Kubernetes.

    ```yaml
    >>> notifier:
    >>>   imagePullPolicy: Always
    ```

    ### resources

    The resources requirements to allocate to the container.

    ```yaml
    >>> notifier:
    >>>   resources:
    >>>     memory: "64Mi"
    >>>     cpu: "50m"
    ```

    ### nodeSelector

    From [Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector)  # noqa

    > nodeSelector is the simplest recommended form of node selection constraint.
    > nodeSelector is a field of PodSpec. It specifies a map of key-value pairs.
    > For the pod to be eligible to run on a node, the node must have each of
    > the indicated key-value pairs as labels (it can have additional labels as well).
    > The most common usage is one key-value pair.

    ```yaml
    >>> notifier:
    >>>   nodeSelector:
    >>>     node_label: node_value
    ```

    ### affinity

    From [Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)  # noqa

    > The affinity/anti-affinity feature, greatly expands the types of constraints you can express.

    The affinity to use for scheduling the job.

    ```yaml
    >>> notifier:
    >>>   affinity:
    >>>     podAffinity:
    >>>       preferredDuringSchedulingIgnoredDuringExecution:
    >>>         ...
    ```


    ### tolerations

    From [Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)  # noqa

    > Tolerations are applied to pods, and allow (but do not require)
    > the pods to schedule onto nodes with matching taints.

    ```yaml
    >>> notifier:
    >>>   tolerations:
    >>>     - key: "key"
    >>>       operator: "Exists"
    >>>       effect: "NoSchedule"
    ```

    ### imagePullSecrets

    From [Kubernetes docs](https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod)  # noqa

    > ImagePullSecrets is a list of references to secrets in the same namespace
    > to use for pulling any images in pods that reference this ServiceAccount.
    > ImagePullSecrets are distinct from Secrets because Secrets can be mounted in the pod,
    > but ImagePullSecrets are only accessed by the kubelet.

    ```yaml
    >>> notifier:
    >>>   imagePullSecrets: ['secret1', 'secret2']
    ```
    """

    _IDENTIFIER = "notifier"

    def get_image(self) -> str:
        image = self.image or "polyaxon/polyaxon-events-handlers"
        image_tag = (
            self.image_tag
            if self.image_tag is not None
            else clean_version_post_suffix(pkg.VERSION)
        )
        return "{}:{}".format(image, image_tag) if image_tag else image

    def get_resources(self) -> k8s_schemas.V1ResourceRequirements:
        return self.resources if self.resources else get_notifier_resources()


def get_default_notification_container(
    notifier: Optional[V1PolyaxonNotifier] = None,
) -> k8s_schemas.V1Container:
    image = "polyaxon/polyaxon-events-handlers"
    image_tag = clean_version_post_suffix(pkg.VERSION)
    image_pull_policy = PullPolicy.IF_NOT_PRESENT.value
    resources = get_notifier_resources()
    if notifier:
        image = notifier.image or image
        image_tag = notifier.image_tag or image_tag
        image_pull_policy = notifier.image_pull_policy or image_pull_policy
        resources = notifier.resources or resources
    return k8s_schemas.V1Container(
        name=MAIN_JOB_CONTAINER,
        image="{}:{}".format(image, image_tag),
        image_pull_policy=image_pull_policy,
        command=["polyaxon", "notify"],
        args=[
            "{{params.backend.as_arg}}",
            "{{params.owner.as_arg}}",
            "{{params.project.as_arg}}",
            "{{params.name.as_arg}}",
            "{{params.uuid.as_arg}}",
            "{{params.condition.as_arg}}",
        ],
        resources=resources,
    )
