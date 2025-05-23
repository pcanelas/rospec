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
)
from rospec.verification.context import Context
from rospec.verification.interpreter import interpret
from rospec.verification.subtyping import is_subtype


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
            f"Subscriber {subscriber.topic.name} has no publisher"
        )

    actions = filter_connection_by_type(connections, Action)
    action_providers = [action for action in actions if action.role == ServiceActionRole.PROVIDES]
    action_consumers = [action for action in actions if action.role == ServiceActionRole.CONSUMES]
    for action_consumer in action_consumers:
        # There must be at least one action provider for topic in action_providers
        assert any(
            [action_provider.topic.name == action_consumer.topic.name for action_provider in action_providers]
        ), f"Action consumer {action_consumer.topic.value} has no provider"

    services = filter_connection_by_type(connections, Service)
    service_providers = [service for service in services if service.role == ServiceActionRole.PROVIDES]
    service_consumers = [service for service in services if service.role == ServiceActionRole.CONSUMES]
    for service_consumer in service_consumers:
        # There must be at least one service provider for topic in service_providers
        assert any(
            [service_provider.topic.name == service_consumer.topic.name for service_provider in service_providers]
        ), f"Service consumer {service_consumer.topic.value} has no provider"


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
    raise ValueError(f"Unsupported type: {type(value)}")


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

    if set(consumer_qos.fields.keys()) != set(provider_qos.fields.keys()):
        context.add_error(f"QoS fields do not match: {consumer_qos.fields.keys()} != {provider_qos.fields.keys()}")
        return False
    for field in consumer_qos.fields.keys():
        assert isinstance(consumer_qos.fields[field], OptionalType)
        assert isinstance(consumer_qos.fields[field], OptionalType)
        consumer_value = consumer_qos.fields[field].default_value
        provider_value = provider_qos.fields[field].default_value

        if not rules[field](provider_value, consumer_value):
            context.add_error(f"QoS rule {field} not satisfied: {consumer_value} !< {provider_value}")
            return False

    return True


def check_color_format(context: Context, consumer: PolicyAttached, provider: PolicyAttached) -> bool:
    consumer_format = context.get_typing(consumer.policy_instance.name)
    provider_format = context.get_typing(provider.policy_instance.name)

    assert isinstance(consumer_format, StructType)
    assert isinstance(provider_format, StructType)

    if not consumer_format.fields["format"] == provider_format.fields["format"]:
        context.add_error(
            f"Color format not satisfied: {consumer_format.fields['format'].default_value} "
            f"!= {provider_format.fields['format'].default_value}"
        )
        return False

    return True


def check_qos(context: Context, consumer_qos: PolicyAttached, provider_qos: PolicyAttached) -> bool:
    consumer_qos_type = context.get_typing(consumer_qos.policy_instance.name)
    provider_qos_type = context.get_typing(provider_qos.policy_instance.name)

    assert isinstance(consumer_qos_type, StructType) and isinstance(provider_qos_type, StructType)

    if not check_qos_rules(context, consumer_qos_type, provider_qos_type):
        context.add_error("QoS rules not satisfied for subscriber and publisher")
        return False

    return True


def check_policies(
    context: Context,
    consumer_policy: Optional[dict[str, PolicyAttached]],
    provider_policy: Optional[dict[str, PolicyAttached]],
) -> bool:
    # TODO: this checking needs to be done in the actual policy check
    if consumer_policy is None or provider_policy is None:
        context.add_error("Policies not found for consumer or provider")
        return False
    if consumer_policy == {} and provider_policy == {}:
        return True
    if consumer_policy == {} and provider_policy != {}:
        context.add_error("Policy not found for consumer when publisher has policies")
        return False
    elif consumer_policy != {} and provider_policy == {}:
        context.add_error("Policy found for subscriber when publisher has no policies")
        return False
    elif set(consumer_policy.keys()) != set(provider_policy.keys()):
        context.add_error(f"Policies do not match: {consumer_policy.keys()} != {provider_policy.keys()}")
        return False

    dispatcher = {
        "qos": check_qos,
        "color_format": check_color_format,
    }

    result = True
    for name in consumer_policy.keys():
        result = result and dispatcher[name](context, consumer_policy[name], provider_policy[name])

    return result
