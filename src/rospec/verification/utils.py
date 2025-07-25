from typing import Union, Any, Optional

from rospec.language.nodes import (
    Expression,
    FunctionCall,
    Identifier,
    Literal,
    Publisher,
    Subscriber,
    Action,
    Service,
    TransformType,
    ServiceActionRole,
    TFTransform,
    Message,
    Array,
    PolicyAttached,
)
from rospec.language.ttypes import (
    t_bool,
    t_comparison_type,
    t_int,
    t_float,
    t_string,
    TType,
    StructType,
    ArrayType,
    OptionalType,
    BasicType,
    EnumType,
)
from rospec.verification.context import Context
from rospec.verification.interpreter import interpret
from rospec.verification.subtyping import is_subtype
from rospec import errors


def wrap_equals(identifier: Identifier, value: Expression) -> FunctionCall:
    return FunctionCall(
        operator=Identifier(name="==", ttype=t_comparison_type),
        operands=[identifier, value],
        ttype=t_bool,
    )


def filter_connection_by_type(connections: list[Union[Publisher, Subscriber, Service, Action]], connection_type: type):
    return list(filter(lambda connection: isinstance(connection, connection_type), connections))


def check_at_least_one_publisher(connections: list[Union[Publisher, Subscriber, Service, Action]]):
    subscribers = filter_connection_by_type(connections, Subscriber)
    publishers = filter_connection_by_type(connections, Publisher)
    for subscriber in subscribers:
        # There must be at least one publisher for topic in publishers
        assert any([publisher.topic.name == subscriber.topic.name for publisher in publishers]), (
            errors.PUBLISHER_NOT_FOUND.format(topic=subscriber.topic, component=subscriber.node)
        )

    actions = filter_connection_by_type(connections, Action)
    action_providers = [action for action in actions if action.role == ServiceActionRole.PROVIDES]
    action_consumers = [action for action in actions if action.role == ServiceActionRole.CONSUMES]
    for action_consumer in action_consumers:
        # There must be at least one action provider for topic in action_providers
        assert any(
            [action_provider.topic.name == action_consumer.topic.name for action_provider in action_providers]
        ), errors.PROVIDER_NOT_FOUND.format(topic=action_consumer.topic, component=action_consumer.node)

    services = filter_connection_by_type(connections, Service)
    service_providers = [service for service in services if service.role == ServiceActionRole.PROVIDES]
    service_consumers = [service for service in services if service.role == ServiceActionRole.CONSUMES]
    for service_consumer in service_consumers:
        # There must be at least one service provider for topic in service_providers
        assert any(
            [service_provider.topic.name == service_consumer.topic.name for service_provider in service_providers]
        ), errors.PROVIDER_NOT_FOUND.format(topic=service_consumer.topic, component=service_consumer.node)


def check_subtyping_connections(context: Context, connections: list[Union[Publisher, Subscriber, Service, Action]]):
    subscribers = filter_connection_by_type(connections, Subscriber)
    publishers = filter_connection_by_type(connections, Publisher)

    for subscriber in subscribers:
        for publisher in publishers:
            if subscriber.topic.name == publisher.topic.name:
                assert is_subtype(context, publisher.topic.ttype, subscriber.topic.ttype)

    # TODO: for actions and services


def check_frames_wellformedness(frames: list[TFTransform]):
    frame_broadcasters = [frame for frame in frames if frame.transform == TransformType.BROADCAST]
    frame_listeners = [frame for frame in frames if frame.transform == TransformType.LISTEN]

    for listener in frame_listeners:
        assert any(
            [
                listener.parent_frame == broadcaster.parent_frame and listener.child_frame == broadcaster.child_frame
                for broadcaster in frame_broadcasters
            ]
        )

    for broadcaster in frame_broadcasters:
        assert not (any([broadcaster.child_frame == broadcaster2.child_frame for broadcaster2 in frame_broadcasters]))


def convert_to_expression(context: Context, value: Any, ttype: TType) -> Expression:
    if isinstance(ttype, OptionalType):
        ttype = ttype.ttype  # TODO: small hack for this

    if isinstance(value, bool):
        return Literal(value=value, ttype=t_bool)
    elif isinstance(value, int):
        return Literal(value=value, ttype=t_int)
    elif isinstance(value, float):
        return Literal(value=value, ttype=t_float)
    elif isinstance(value, str):
        return Literal(value=value, ttype=t_string)
    elif isinstance(value, dict):
        if isinstance(ttype, BasicType) and ttype in context.aliases:
            ttype = context.aliases[ttype]  # TODO: this has layers of indirection, we need to solve aliases
        assert isinstance(ttype, StructType)
        return Message(
            fields={key: convert_to_expression(context, val, ttype.fields[key]) for key, val in value.items()},
            ttype=ttype,
        )
    elif isinstance(value, list):
        assert isinstance(ttype, ArrayType)
        return Array(elements=[convert_to_expression(context, item, ttype.ttype) for item in value], ttype=ttype)
    raise ValueError(errors.UNSUPPORTED_TYPE.format(type=type(value)))


def check_qos_rules(context, consumer_qos: StructType, provider_qos: StructType) -> bool:
    rules = {
        "reliability": lambda x, y: not (interpret(context, x) == "BestEffort" and interpret(context, y) == "Reliable"),
        "durability": lambda x, y: not (
            interpret(context, x) == "Volatile" and interpret(context, y) == "TransientLocal"
        ),
        "liveliness": lambda x, y: not (
            interpret(context, x) == "Automatic" and interpret(context, y) == "ManualByTopic"
        ),
        "deadline": lambda x, y: interpret(context, x) >= interpret(context, y),
        "duration": lambda x, y: interpret(context, x) >= interpret(context, y),
        "history": lambda x, y: True,
        "lifespan": lambda x, y: True,
        "depth": lambda x, y: True,
    }
    local_errors = []
    for field in provider_qos.fields.keys():
        if field not in provider_qos.fields.keys():
            errors.append(
                errors.QOS_FIELDS_MISMATCH.format(
                    field=field,
                    expected_fields=list(provider_qos.fields.keys()),
                )
            )

    if len(local_errors) > 0:
        context.errors.extend(local_errors)
        return False

    for field in consumer_qos.fields.keys():
        assert isinstance(consumer_qos.fields[field], OptionalType)
        assert isinstance(consumer_qos.fields[field], OptionalType)
        consumer_value = consumer_qos.fields[field].default_value
        provider_value = provider_qos.fields[field].default_value

        if not rules[field](provider_value, consumer_value):
            context.add_error(
                errors.QOS_RULE_NOT_SATISFIED.format(
                    qos_field=field, consumer_value=consumer_value, provider_value=provider_value
                )
            )
            return False

    return True


def check_color_format(context: Context, consumer: PolicyAttached, provider: PolicyAttached) -> bool:
    consumer_format = context.get_typing(consumer.policy_instance.name)
    provider_format = context.get_typing(provider.policy_instance.name)

    assert isinstance(consumer_format, StructType)
    assert isinstance(provider_format, StructType)

    if not consumer_format.fields["format"] == provider_format.fields["format"]:
        context.add_error(
            errors.COLOR_FORMAT_NOT_SATISFIED.format(
                consumer=consumer_format.fields["format"].default_value,
                provider=provider_format.fields["format"].default_value,
            )
        )
        return False

    return True


def check_qos(context: Context, consumer_qos: PolicyAttached, provider_qos: PolicyAttached) -> bool:
    consumer_qos_type = context.get_typing(consumer_qos.policy_instance.name)
    provider_qos_type = context.get_typing(provider_qos.policy_instance.name)

    assert isinstance(consumer_qos_type, StructType) and isinstance(provider_qos_type, StructType)

    return check_qos_rules(context, consumer_qos_type, provider_qos_type)


def check_policies(
    context: Context,
    consumer_policy: Optional[dict[str, PolicyAttached]],
    provider_policy: Optional[dict[str, PolicyAttached]],
) -> bool:
    # TODO: this checking needs to be done in the actual policy check
    if consumer_policy is None or provider_policy is None:
        context.add_error(errors.POLICIES_NOT_FOUND)
        return False
    if consumer_policy == {} and provider_policy == {}:
        return True
    if consumer_policy == {} and provider_policy != {}:
        context.add_error(errors.POLICY_NOT_FOUND_CONSUMER.format(policies=list(provider_policy.keys())))
        return False
    elif consumer_policy != {} and provider_policy == {}:
        context.add_error(errors.POLICY_FOUND_NO_PUBLISHER.format(policies=list(consumer_policy.keys())))
        return False
    elif set(consumer_policy.keys()) != set(provider_policy.keys()):
        context.add_error(
            errors.POLICIES_MISMATCH.format(
                consumer_keys=list(consumer_policy.keys()), provider_keys=list(provider_policy.keys())
            )
        )
        return False

    dispatcher = {
        "qos": check_qos,
        "color_format": check_color_format,
    }

    result = True
    for name in consumer_policy.keys():
        result = dispatcher[name](context, consumer_policy[name], provider_policy[name]) and result

    return result


def aux_replace_enums(enum_type: EnumType, expr: Expression) -> Expression:
    if isinstance(expr, Literal):
        if isinstance(expr.value, str) and Identifier(name=expr.value, ttype=t_string) in enum_type.ttypes:
            return Literal(value=enum_type.ttypes.index(Identifier(name=expr.value, ttype=t_string)), ttype=t_int)
        return expr
    elif isinstance(expr, Identifier):
        if Identifier(name=expr.name, ttype=t_string) in enum_type.ttypes:
            return Literal(value=enum_type.ttypes.index(Identifier(name=expr.name, ttype=t_string)), ttype=t_int)
        return expr
    elif isinstance(expr, FunctionCall):
        return FunctionCall(
            operator=expr.operator,
            operands=[aux_replace_enums(enum_type, op) for op in expr.operands],
            ttype=expr.ttype,
        )
    elif isinstance(expr, Message):
        return Message(
            fields={k: aux_replace_enums(enum_type, v) for k, v in expr.fields.items()},
            ttype=expr.ttype,
        )
    elif isinstance(expr, Array):
        return Array(elements=[aux_replace_enums(enum_type, e) for e in expr.elements], ttype=expr.ttype)
    else:
        raise ValueError(f"Unsupported expression type: {type(expr)}")
