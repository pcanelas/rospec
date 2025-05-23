from typing import Union, Tuple, Optional

from rospec.language.nodes import (
    ROSpecNode,
    Expression,
    Identifier,
    FunctionCall,
    Publisher,
    Subscriber,
    Action,
    PolicyAttached,
    TFTransform,
    Service,
    ConfigurableInformation,
    Remapping,
)
from rospec.language.ttypes import (
    t_bool,
    t_float,
    t_int,
    t_string,
    t_double,
    TType,
    EnumType,
    t_bool_bool_bool,
    t_bottom,
)


def convert_literal(value: str, ttype: str) -> Tuple[Union[int, float, bool, str], TType]:
    """Converts a literal value to the appropriate type and returns the converted value with its TType."""
    literal_dispatcher = {
        "INT": lambda x: (int(x), t_int),
        "FLOAT": lambda x: (float(x), t_float),
        "BOOLLIT": lambda x: (x == "true", t_bool),
        "ESCAPED_STRING": lambda x: (x[1:-1], t_string),
    }
    return literal_dispatcher[ttype](value)


def filter_nodes_by_type(nodes, args: list[ROSpecNode]):
    """Filters a list of nodes to include only instances of a specified type or types."""
    return [x for x in args if isinstance(x, nodes)]


def aux_node_plugin_fields_constructor(args, node_name):
    node_type_fields = {
        ConfigurableInformation: [],
        Publisher: [],
        Subscriber: [],
        Service: [],
        Action: [],
        TFTransform: [],
        Remapping: [],
        PolicyAttached: {},
    }
    dependencies = []

    for arg in args:
        if isinstance(arg, PolicyAttached):
            node_type_fields[PolicyAttached][arg.policy_type.name] = arg
        elif type(arg) in node_type_fields:
            # Extra: Assign the node name to the node
            if type(arg) in [Publisher, Subscriber, Service, Action, TFTransform, Remapping]:
                arg.node = Identifier(name=node_name, ttype=arg.node.ttype)

            node_type_fields[type(arg)].append(arg)

            # Copy policies for the current argument
            arg.policies = node_type_fields[PolicyAttached]
            # Reset policies after they are assigned
            node_type_fields[PolicyAttached] = {}
        else:
            dependencies.append(arg)

    return node_type_fields, dependencies


def infer_qos_type(identifier: Identifier) -> TType:
    name = identifier.name
    dispatcher = {
        "history": EnumType(
            ttypes=[Identifier(name="KeepLast", ttype=t_bottom), Identifier(name="KeepAll", ttype=t_bottom)]
        ),
        "reliability": EnumType(
            ttypes=[Identifier(name="Reliable", ttype=t_bottom), Identifier(name="BestEffort", ttype=t_bottom)]
        ),
        "durability": EnumType(
            ttypes=[Identifier(name="TransientLocal", ttype=t_bottom), Identifier(name="Volatile", ttype=t_bottom)]
        ),
        "liveliness": EnumType(
            ttypes=[Identifier(name="Automatic", ttype=t_bottom), Identifier(name="Manual", ttype=t_bottom)]
        ),
        "depth": t_int,
        "deadline": t_double,
        "lifespan": t_double,
        "duration": t_double,
        "format": EnumType(
            ttypes=[
                Identifier(name="RGB8", ttype=t_bottom),
                Identifier(name="Grayscale", ttype=t_bottom),
            ]
        ),
    }
    return dispatcher[name]


def merge_and_dependencies(dependencies: list[Expression]) -> Optional[Expression]:
    if len(dependencies) == 0:
        return None
    if len(dependencies) == 1:
        return dependencies[0]
    return FunctionCall(
        ttype=t_bool,
        operator=Identifier(name="and", ttype=t_bool_bool_bool),
        operands=[dependencies[0], merge_and_dependencies(dependencies[1:])],
    )


def replace_empty_in_attributes(attributes, name: str):
    for list_values in attributes.values():
        for value in list_values:
            if type(value) in [Publisher, Subscriber, Service, Action, TFTransform, Remapping]:
                value.node = Identifier(name=name, ttype=value.node.ttype)

    return attributes
