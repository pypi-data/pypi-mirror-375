from typing import Dict, List, Optional, Union

from polyaxon._flow.io.io import V1IO
from polyaxon._flow.joins import V1Join
from polyaxon._flow.matrix import V1Mapping, V1Matrix
from polyaxon._flow.params.params import ParamSpec, V1Param
from polyaxon.exceptions import PolyaxonValidationError


def validate_params(
    params: Dict[str, Union[Dict, V1Param]],
    inputs: List[V1IO],
    outputs: List[V1IO],
    contexts: Optional[List[V1IO]] = None,
    matrix: Optional[Union[Dict, V1Matrix]] = None,
    joins: List[V1Join] = None,
    context: Optional[Dict] = None,
    is_template: bool = True,
    check_all_refs: bool = False,
    extra_info: Optional[str] = None,
    parse_values: bool = False,
) -> List[ParamSpec]:
    """
    Validates Params given inputs, and an optional context.

    Params can be:
     * plain values: we check them against the inputs types
     * job/experiment references: We postpone to server side validation.
     * ops reference: in that case a context must be provided to validate that the reference exists.
        and types are correct.
    """
    contexts_by_keys = {k.name: k for k in contexts or []}

    def parse_param(k, v) -> V1Param:
        if not isinstance(v, V1Param):
            v = V1Param.read(v, config_type=".yaml") if v else V1Param()
        if v and k in contexts_by_keys:
            v.context_only = True
            if v.to_init is None:
                v.to_init = contexts_by_keys[k].to_init
            if v.to_env is None:
                v.to_env = contexts_by_keys[k].to_env
            if v.connection is None:
                v.connection = contexts_by_keys[k].connection
        return v

    def validate_matrix(io: V1IO) -> bool:
        if isinstance(matrix, V1Mapping):
            return matrix.has_key(io.name)  # noqa
        elif io.name in matrix.params:
            matrix.params[io.name].validate_io(io)
            return True
        elif hasattr(matrix, "resource") and io.name == matrix.resource.name:
            return True
        return False

    params = params or {}
    params = {k: parse_param(k, params[k]) for k in params}
    # Extend with params coming from joins
    params.update(
        {k: v for j in (joins or []) for k, v in j.params.items() if k not in params}
    )

    if requires_params(inputs, outputs):
        if not is_template and not params and not matrix:
            message = (
                "The Polyaxonfile has non optional inputs/outputs, "
                "you need to pass valid params"
            )
            if extra_info:
                message += " Please check: {}".format(extra_info)

            raise PolyaxonValidationError(message)
    elif not accepts_params(inputs, outputs) and params:
        extra_params = set(params.keys()) - {
            p for p in params if params[p].context_only
        }
        if extra_params:
            message = "Received unexpected params `{}`".format(extra_params)
            if extra_info:
                message += " Please check: {}".format(extra_info)
            raise PolyaxonValidationError(message)

    matrix = matrix or {}
    inputs = inputs or []
    outputs = outputs or []

    processed_params = []
    validated_params = []

    for inp in inputs:
        if inp.name in params:
            param_value = params[inp.name]
            param_spec = param_value.get_spec(
                name=inp.name,
                iotype=inp.type,
                is_flag=inp.is_flag,
                is_list=inp.is_list,
                is_context=False,
                arg_format=inp.arg_format,
            )
            if param_spec.param.is_ref or param_spec.param.is_template_ref:
                param_spec.validate_ref(context, is_template, check_all_refs)
            else:
                parsed_value = inp.validate_value(param_value.value)
                if parse_values:
                    param_spec.param.value = parsed_value
                    if not param_spec.param.connection and param_value.connection:
                        param_spec.param.connection = inp.connection
                    if not param_spec.param.to_init and param_value.to_init:
                        param_spec.param.to_init = inp.to_init
                    if not param_spec.param.to_env and param_value.to_env:
                        param_spec.param.to_env = inp.to_env
            validated_params.append(param_spec)
            if not param_spec.param.context_only:
                processed_params.append(inp.name)
        elif matrix and validate_matrix(inp):
            pass
        elif not (inp.is_optional or inp.delay_validation or is_template):
            message = "Input {} is required, no param was passed.".format(inp.name)
            if extra_info:
                message += " Please check: {}".format(extra_info)
            raise PolyaxonValidationError(message)
        else:
            validated_params.append(
                ParamSpec(
                    name=inp.name,
                    param=V1Param(
                        value=inp.value,
                        connection=inp.connection,
                        to_init=inp.to_init,
                        to_env=inp.to_env,
                    ),
                    type=inp.type,
                    is_flag=inp.is_flag,
                    is_list=inp.is_list,
                    is_context=False,
                    is_requested=True,
                    arg_format=inp.arg_format,
                )
            )

    for out in outputs:
        if out.name in params:
            param_value = params[out.name]
            param_spec = param_value.get_spec(
                name=out.name,
                iotype=out.type,
                is_flag=out.is_flag,
                is_list=out.is_list,
                is_context=False,
                arg_format=out.arg_format,
            )
            if param_spec.param.is_ref or param_spec.param.is_template_ref:
                param_spec.validate_ref(
                    None, is_template=False, check_all_refs=check_all_refs
                )
            else:  # Plain value
                parsed_value = out.validate_value(param_value.value)
                if parse_values:
                    param_spec.param.value = parsed_value
                    if not param_spec.param.connection and param_value.connection:
                        param_spec.param.connection = out.connection
                    if not param_spec.param.to_init and param_value.to_init:
                        param_spec.param.to_init = out.to_init
                    if not param_spec.param.to_env and param_value.to_env:
                        param_spec.param.to_env = out.to_env
            validated_params.append(param_spec)
            if not param_spec.param.context_only:
                processed_params.append(out.name)
        # No validation for outputs we assume that the op might populate a context or send a metric
        elif out.delay_validation is not False:
            validated_params.append(
                ParamSpec(
                    name=out.name,
                    param=V1Param(
                        value=out.value,
                        connection=out.connection,
                        to_init=out.to_init,
                        to_env=out.to_env,
                    ),
                    type=out.type,
                    is_flag=out.is_flag,
                    is_list=out.is_list,
                    is_context=False,
                    is_requested=True,
                    arg_format=out.arg_format,
                )
            )
    extra_params = set(params.keys()) - set(processed_params)
    context_params = {p for p in params if params[p].context_only}
    extra_invalid_params = extra_params - context_params
    if extra_invalid_params:
        message = "Received unexpected params `{}`".format(extra_invalid_params)
        if extra_info:
            message += " Please check: {}".format(extra_info)
        raise PolyaxonValidationError(message)

    # Add all (extra) context params that were not processed during the IO check
    for p in contexts_by_keys:
        if p in extra_params:
            param_value = params[p]
            param_spec = param_value.get_spec(
                name=p,
                iotype=None,
                is_flag=None,
                is_list=None,
                is_context=True,
                arg_format=None,
            )
            validated_params.append(param_spec)
        else:
            context_io = contexts_by_keys[p]
            validated_params.append(
                ParamSpec(
                    name=p,
                    param=V1Param(
                        value=context_io.value,
                        connection=context_io.connection,
                        to_init=context_io.to_init,
                        to_env=context_io.to_env,
                    ),
                    type=None,
                    is_flag=None,
                    is_list=None,
                    is_context=True,
                    is_requested=True,
                    arg_format=None,
                )
            )
    return validated_params


def requires_params(inputs: List[V1IO], outputs: List[V1IO]):
    if not inputs and not outputs:
        return False

    def parse_io(ios: List[V1IO], delay_validation: bool):
        if not ios:
            return False
        for i in ios:
            delay_validation = (
                i.delay_validation
                if i.delay_validation is not None
                else delay_validation
            )
            if not i.is_optional and not delay_validation:
                return True
        return False

    if parse_io(inputs, False):
        return True

    if parse_io(outputs, True):
        return True

    return False


def accepts_params(inputs: List[V1IO], outputs: List[V1IO]):
    return bool(inputs or outputs)


def get_upstream_op_params_by_names(params: Dict[str, V1Param]):
    upstream = {}

    if not params:
        return upstream

    for param in params:
        param_ref = params[param].get_spec(
            name=param,
            iotype=None,
            is_flag=None,
            is_list=None,
            is_context=None,
            arg_format=None,
        )
        if param_ref and param_ref.param.is_ops_ref:
            if param_ref.param.entity_ref in upstream:
                upstream[param_ref.param.entity_ref].append(param_ref)
            else:
                upstream[param_ref.param.entity_ref] = [param_ref]

    return upstream


def get_upstream_run_params_by_names(params: Dict[str, V1Param]):
    upstream = {}

    if not params:
        return upstream

    for param in params:
        param_ref = params[param].get_spec(
            name=param,
            iotype=None,
            is_flag=None,
            is_list=None,
            is_context=None,
            arg_format=None,
        )
        if param_ref and param_ref.param.is_runs_ref:
            if param_ref.param.entity_ref in upstream:
                upstream[param_ref.param.entity_ref].append(param_ref)
            else:
                upstream[param_ref.param.entity_ref] = [param_ref]

    return upstream


def get_dag_params_by_names(params: Dict[str, V1Param]):
    upstream = {}

    if not params:
        return upstream

    for param in params:
        param_ref = params[param].get_spec(
            name=param,
            iotype=None,
            is_flag=None,
            is_list=None,
            is_context=None,
            arg_format=None,
        )
        if param_ref and param_ref.param.is_dag_ref:
            if param_ref.param.entity_ref in upstream:
                upstream[param_ref.param.entity_ref].append(param_ref)
            else:
                upstream[param_ref.param.entity_ref] = [param_ref]

    return upstream
