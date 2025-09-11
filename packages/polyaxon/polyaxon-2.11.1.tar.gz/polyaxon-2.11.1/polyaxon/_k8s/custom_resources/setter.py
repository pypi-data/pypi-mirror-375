from typing import Dict, List

from polyaxon._flow import V1Notification, V1SchedulingPolicy, V1Termination


def set_termination(custom_object: Dict, termination: V1Termination) -> Dict:
    if not termination:
        return custom_object

    termination_spec = {}
    if termination.max_retries:
        termination_spec["backoffLimit"] = termination.max_retries
    if termination.timeout:
        termination_spec["activeDeadlineSeconds"] = termination.timeout
    if termination.ttl:
        termination_spec["ttlSecondsAfterFinished"] = termination.ttl

    custom_object["termination"] = termination_spec
    return custom_object


def set_collect_logs(custom_object: Dict, collect_logs: bool) -> Dict:
    if collect_logs is None:
        collect_logs = False

    custom_object["collectLogs"] = collect_logs
    return custom_object


def set_sync_statuses(custom_object: Dict, sync_statuses: bool) -> Dict:
    if sync_statuses is None:
        sync_statuses = False

    custom_object["syncStatuses"] = sync_statuses
    return custom_object


def set_notify(custom_object: Dict, notifications: List[V1Notification]) -> Dict:
    if notifications is None:
        notifications = []

    custom_object["notifications"] = [n.to_operator() for n in notifications]
    return custom_object


def set_clean_pod_policy(template_spec: Dict, clean_pod_policy: str) -> Dict:
    if not clean_pod_policy:
        # Sets default clean pod policy
        clean_pod_policy = "None"

    template_spec["cleanPodPolicy"] = clean_pod_policy.capitalize()
    return template_spec


def set_scheduling_policy(
    template_spec: Dict, scheduling_policy: V1SchedulingPolicy = None
) -> Dict:
    if not scheduling_policy:
        return template_spec

    template_spec["schedulingPolicy"] = scheduling_policy.to_light_dict()
    return template_spec
