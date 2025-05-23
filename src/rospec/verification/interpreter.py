from typing import Type, Union

from rospec.language.nodes import (
    Expression,
    FunctionCall,
    Literal,
    Identifier,
    Message,
    Array,
    ArrayAccess,
    Publisher,
    Subscriber,
    Action,
    Service,
    Connection,
    ServiceActionRole,
    TFTransform,
)
from rospec.language.ttypes import OptionalType
from rospec.verification.context import Context

evaluation_context = {
    # Arithmetic operations
    "+": lambda ctx, x, y: interpret(ctx, x) + interpret(ctx, y),
    "-": lambda ctx, x, y: interpret(ctx, x) - interpret(ctx, y),
    "*": lambda ctx, x, y: interpret(ctx, x) * interpret(ctx, y),
    "/": lambda ctx, x, y: interpret(ctx, x) / interpret(ctx, y),
    "%": lambda ctx, x, y: interpret(ctx, x) % interpret(ctx, y),
    # Boolean operations
    "==": lambda ctx, x, y: interpret(ctx, x) == interpret(ctx, y),
    "!=": lambda ctx, x, y: interpret(ctx, x) != interpret(ctx, y),
    "<": lambda ctx, x, y: interpret(ctx, x) < interpret(ctx, y),
    "<=": lambda ctx, x, y: interpret(ctx, x) <= interpret(ctx, y),
    ">": lambda ctx, x, y: interpret(ctx, x) > interpret(ctx, y),
    ">=": lambda ctx, x, y: interpret(ctx, x) >= interpret(ctx, y),
    "->": lambda ctx, x, y: (not interpret(ctx, x)) or interpret(ctx, y),
    "and": lambda ctx, x, y: interpret(ctx, x) and interpret(ctx, y),
    "or": lambda ctx, x, y: interpret(ctx, x) or interpret(ctx, y),
    "!": lambda ctx, x: not interpret(ctx, x),
    # Custom ROSpec functions
    "content": lambda ctx, x: ctx.values[x.name],
    "len": lambda ctx, x: len(interpret(ctx, x)),
    "count": lambda ctx, x: len(interpret(ctx, x)),
    "publishers": lambda ctx, x: interpret_connection(ctx, x, Publisher),
    "subscribers": lambda ctx, x: interpret_connection(ctx, x, Subscriber),
    "providers": lambda ctx, x: [
        y
        for y in interpret_connection(ctx, x, Action) + interpret_connection(ctx, x, Service)
        if y.role == ServiceActionRole.PROVIDES
    ],
    "consumers": lambda ctx, x: [
        y
        for y in interpret_connection(ctx, x, Action) + interpret_connection(ctx, x, Service)
        if y.role == ServiceActionRole.CONSUMES
    ],
    "exists": lambda ctx, x: (not isinstance(ctx.typing[x.name], OptionalType)) and x.name in ctx.values,
    # TODO: default(plugin_name):
}


def interpret_connection(
    ctx: Context, x: Expression, ty_node: Type[Union[Action, Service, Publisher, Subscriber]]
) -> list:
    x = x.name if isinstance(x, Identifier) else interpret(ctx, x)

    result = []
    all_connections: list[tuple[str, Connection]] = []

    for node, connections in ctx.connections.items():
        all_connections.extend([(node, connection) for connection in connections])

    for node, connection in all_connections:
        if isinstance(connection, TFTransform):
            continue
        other_name = (
            connection.topic.name if isinstance(connection.topic, Identifier) else interpret(ctx, connection.topic)
        )
        if isinstance(connection, ty_node) and other_name == x:
            result.append(connection)
    return result


def interpret(context: Context, expr: Expression):
    if isinstance(expr, Literal):
        return expr.value
    if isinstance(expr, Identifier):
        # TODO: this is an hack to deal with identifiers not defined in the context (e.g., tf frames and enum values)
        return context.values[expr.name] if expr.name in context.values else expr.name
    if isinstance(expr, Message):
        return {interpret(context, field): interpret(context, value) for field, value in expr.fields.items()}
    if isinstance(expr, Array):
        return [interpret(context, operand) for operand in expr.elements]
    if isinstance(expr, ArrayAccess):
        indexes = [interpret(context, operand) for operand in expr.indexes]
        target = interpret(context, expr.target)
        for index in indexes:
            target = target[index]
        return target
    if isinstance(expr, FunctionCall):
        result = evaluation_context[expr.operator.name](context, *expr.operands)
        return result

    assert False, f"Expression {expr} of type {type(expr)} not supported"
