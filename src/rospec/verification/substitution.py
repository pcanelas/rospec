from typing import Any

from rospec.language.nodes import (
    Expression,
    Identifier,
    Message,
    Array,
    FunctionCall,
    ArrayAccess,
    TFTransform,
    Publisher,
    Subscriber,
    Service,
    Action,
    Connection,
)
from rospec.language.ttypes import TType, RefinedType, OptionalType, StructType, t_bottom, ArrayType
from rospec.verification.interpreter import interpret


def selfification(expression: Any, name: str = "_") -> RefinedType:
    import rospec.verification.utils as rospec_utils

    return RefinedType(
        name=Identifier(name=name, ttype=expression.ttype),
        ttype=expression.ttype,
        refinement=rospec_utils.wrap_equals(Identifier(name=name, ttype=expression.ttype), expression),
    )


def substitute_connection_with_assignments(context, connection: Connection, s: str, value: Expression):
    if isinstance(connection, TFTransform):
        connection.parent_frame = inverse_substitution_expr_expr(s, value, connection.parent_frame)
        connection.child_frame = inverse_substitution_expr_expr(s, value, connection.child_frame)

        if isinstance(connection.parent_frame, FunctionCall):
            assert connection.parent_frame.operator.name == "content", "The only function call allowed is content()"
            assert len(connection.parent_frame.operands) == 1, "content() must have one operand"
            connection.parent_frame = connection.parent_frame.operands[0]

        if isinstance(connection.child_frame, FunctionCall):
            assert connection.child_frame.operator.name == "content", "The only function call allowed is content()"
            assert len(connection.child_frame.operands) == 1, "content() must have one operand"
            connection.child_frame = connection.child_frame.operands[0]

    # It is a Publisher, Subscriber, Service or Action
    if isinstance(connection, (Publisher, Subscriber, Service, Action)):
        connection.topic = inverse_substitution_expr_expr(s, value, connection.topic)

        if isinstance(connection.topic, FunctionCall):
            assert connection.topic.operator.name == "content", "For now the only function call allowed is content()"
            assert len(connection.topic.operands) == 1, "content() must have one operand"
            connection.topic = Identifier(
                name=interpret(context, connection.topic.operands[0]), ttype=connection.topic.ttype
            )

    return connection


def substitute_connection_with_remaps(connection: Connection, old: str, new: str):
    if isinstance(connection, TFTransform):
        inverse_substitution_expr_expr(old, Identifier(name=new, ttype=t_bottom), connection.parent_frame)
        inverse_substitution_expr_expr(old, Identifier(name=new, ttype=t_bottom), connection.child_frame)

    if isinstance(connection, (Publisher, Subscriber, Service, Action)):
        inverse_substitution_expr_expr(old, Identifier(name=new, ttype=t_bottom), connection.topic)

    assert False, f"Not implemented yet for {type(connection)}"


def inverse_expr_substitution_in_type(s: str, expr: Expression, ttype: TType) -> TType:
    if isinstance(ttype, RefinedType):
        new_name = inverse_substitution_expr_expr(s, expr, ttype.name)
        if not isinstance(new_name, Identifier):
            new_name = Identifier(name="_", ttype=ttype.refinement.ttype)
        new_internal_ttype = inverse_expr_substitution_in_type(s, expr, ttype.ttype)
        return RefinedType(new_name, new_internal_ttype, inverse_substitution_expr_expr(s, expr, ttype.refinement))

    if isinstance(ttype, OptionalType):
        return OptionalType(
            inverse_expr_substitution_in_type(s, expr, ttype.ttype),
            inverse_substitution_expr_expr(s, expr, ttype.default_value),
        )

    if isinstance(ttype, StructType):
        new_fields = {}
        for field, field_ttype in ttype.fields.items():
            new_fields[field] = inverse_expr_substitution_in_type(s, expr, field_ttype)
        return StructType(new_fields)

    if isinstance(ttype, ArrayType):
        return ArrayType(inverse_expr_substitution_in_type(s, expr, ttype.ttype), ttype.max_size_refinement)
    # TODO: the rest of the types
    return ttype


def inverse_substitution_expr_expr(old: str, new: Expression, expr: Expression) -> Expression:
    if isinstance(expr, Identifier):
        if expr.name == old or expr.name == "_":
            return new

    if isinstance(expr, Message):
        new_fields = {}
        for field, field_expr in expr.fields.items():
            new_fields[field] = inverse_substitution_expr_expr(old, new, field_expr)
        return Message(fields=new_fields, ttype=new.ttype)

    if isinstance(expr, Array):
        elements = [inverse_substitution_expr_expr(old, new, element) for element in expr.elements]
        return Array(elements=elements, ttype=new.ttype)

    if isinstance(expr, ArrayAccess):
        # There is not much we need to do here
        target_name = inverse_substitution_expr_expr(old, new, expr.target)
        return ArrayAccess(ttype=expr.ttype, indexes=expr.indexes, target=target_name)

    if isinstance(expr, FunctionCall):
        new_operands = [inverse_substitution_expr_expr(old, new, operand) for operand in expr.operands]
        return FunctionCall(operator=expr.operator, operands=new_operands, ttype=expr.ttype)

    return expr
