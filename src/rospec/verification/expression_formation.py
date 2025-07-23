from rospec.language.nodes import Literal, Expression, FunctionCall, Identifier, Message, Array, ArrayAccess
from rospec.language.ttypes import (
    t_int,
    t_float,
    t_string,
    t_bool,
    StructType,
    ArrayType,
    AbstractionType,
    BasicType,
    TType,
)
from rospec.verification.context import Context
from rospec.verification.subtyping import is_subtype
from rospec.verification.type_formation import ty_formation
from rospec.language import errors


def e_literal(context: Context, literal: Literal):
    u, t = literal.ttype, type(literal.value)
    dispatcher = {int: t_int, float: t_float, str: t_string, bool: t_bool}
    assert is_subtype(context, u, dispatcher[t]), errors.FIELD_NOT_SUBTYPE.format(field=u, ttype=u, expected_type=t)


def e_var(context: Context, identifier: Identifier):
    ty_formation(context, identifier.ttype)


def e_exp_bin_op(context: Context, exp_bin: FunctionCall):
    assert exp_bin.operator.name in [">", "<", ">=", "<=", "==", "!="], errors.EXPR_NOT_SUPPORTED.format(
        expr=exp_bin, type=exp_bin.operator.name
    )

    # Check the operands
    e_1: Expression = exp_bin.operands[0]
    e_2: Expression = exp_bin.operands[1]
    expr_formation(context, e_1)
    expr_formation(context, e_2)

    assert is_subtype(context, e_1.ttype, t_int) or is_subtype(context, e_1.ttype, t_float), (
        errors.FIELD_NOT_SUBTYPE.format(field=e_1, ttype=e_1.ttype, expected_type="int or float")
    )
    assert is_subtype(context, e_2.ttype, t_int) or is_subtype(context, e_2.ttype, t_float), (
        errors.FIELD_NOT_SUBTYPE.format(field=e_2, ttype=e_2.ttype, expected_type="int or float")
    )


def e_bool_bin_op(context: Context, bin_op: FunctionCall):
    assert bin_op.operator.name in ["and", "or", "->"], errors.EXPR_NOT_SUPPORTED.format(
        expr=bin_op, type=bin_op.operator.name
    )

    # Check the operands
    e_1: Expression = bin_op.operands[0]
    e_2: Expression = bin_op.operands[1]
    expr_formation(context, e_1)
    expr_formation(context, e_2)

    assert is_subtype(context, e_1.ttype, t_bool), errors.FIELD_NOT_SUBTYPE.format(
        field=e_1, ttype=e_1.ttype, expected_type="bool"
    )
    assert is_subtype(context, e_2.ttype, t_bool), errors.FIELD_NOT_SUBTYPE.format(
        field=e_2, ttype=e_2.ttype, expected_type="bool"
    )


def e_not(context: Context, operation: FunctionCall):
    assert operation.operator.name == "not", errors.EXPR_NOT_SUPPORTED.format(
        expr=operation, type=operation.operator.name
    )
    # Check the operand
    e: Expression = operation.operands[0]
    expr_formation(context, e)
    assert is_subtype(context, e.ttype, t_bool), errors.FIELD_NOT_SUBTYPE.format(
        field=e, ttype=e.ttype, expected_type="bool"
    )


def e_message(context: Context, message: Message):
    t_struct = context.get_alias(message.ttype)
    assert isinstance(t_struct, StructType), errors.FIELD_NOT_SUBTYPE.format(
        field=t_struct, ttype=type(t_struct), expected_type="StructType"
    )
    assert isinstance(message.ttype, BasicType), errors.FIELD_NOT_SUBTYPE.format(
        field=message.ttype, ttype=type(message.ttype), expected_type="BasicType"
    )

    instantiated_struct: dict[str, TType] = {}
    for field, value in message.fields.items():
        expr_formation(context, value)
        instantiated_struct[field.name] = value.ttype
    assert is_subtype(context, StructType(instantiated_struct), t_struct), errors.FIELD_NOT_SUBTYPE.format(
        field=instantiated_struct, ttype=StructType(instantiated_struct), expected_type=t_struct
    )


def e_array(context: Context, array: Array):
    for element in array.elements:
        ty_formation(context, element.ttype)
        expr_formation(context, element)
        # TODO: This requires an inference step before to fill array.type
        # assert is_subtype(context, element.ttype,
        #                  array.ttype), f"Element {element} : {element.ttype} not a subtype of {array.ttype}"


def e_array_access(context: Context, array_access: ArrayAccess):
    target_type = array_access.target.ttype  # int[][][]
    number_of_accesses = len(array_access.indexes)

    # We want to ensure that all the indexes are integers
    for index in array_access.indexes:
        expr_formation(context, index)
        assert is_subtype(context, index.ttype, t_int), errors.FIELD_NOT_SUBTYPE.format(
            field=index, ttype=index.ttype, expected_type="int"
        )

    # We want to make sure that array_access type is a subtype of the final type of accessing n times
    # for instance, if target type is int[][][] and we access it 2 times, the final type should be int[]
    for i in range(number_of_accesses):
        assert isinstance(target_type, ArrayType), errors.FIELD_NOT_SUBTYPE.format(
            field=target_type, ttype=type(target_type), expected_type="ArrayType"
        )
        target_type = target_type.ttype

    assert is_subtype(context, target_type, array_access.ttype), errors.FIELD_NOT_SUBTYPE.format(
        field=target_type, ttype=target_type, expected_type=array_access.ttype
    )


def e_call(context: Context, call: FunctionCall):
    call_ttype = context.get_typing(call.operator.name)
    assert isinstance(call_ttype, AbstractionType), errors.FIELD_NOT_SUBTYPE.format(
        field=call_ttype, ttype=type(call_ttype), expected_type="AbstractionType"
    )

    for argument in call.operands:
        expr_formation(context, argument)
        ty_formation(context, argument.ttype)
        ty_formation(context, call_ttype)
        assert is_subtype(context, argument.ttype, call_ttype.argument), errors.FIELD_NOT_SUBTYPE.format(
            field=argument, ttype=argument.ttype, expected_type=call_ttype.argument
        )

        # Keep progressing with the type
        if isinstance(call_ttype.result_type, AbstractionType):
            call_ttype = call_ttype.result_type

    # Check if the type of the arguments is a subtype of the type of the function
    assert is_subtype(context, call.ttype, call_ttype), errors.FIELD_NOT_SUBTYPE.format(
        field=call, ttype=call.ttype, expected_type=call_ttype
    )


def expr_formation(context: Context, expression: Expression):
    if isinstance(expression, Literal):
        e_literal(context, expression)
    elif isinstance(expression, Identifier):
        e_var(context, expression)
    elif isinstance(expression, FunctionCall):
        if expression.operator.name in [">", "<", ">=", "<=", "==", "!="]:
            e_exp_bin_op(context, expression)
        elif expression.operator.name in ["and", "or", "->"]:
            e_bool_bin_op(context, expression)
        elif expression.operator.name == "not":
            e_not(context, expression)
        else:
            e_call(context, expression)
    elif isinstance(expression, Array):
        e_array(context, expression)
    elif isinstance(expression, ArrayAccess):
        e_array_access(context, expression)
    elif isinstance(expression, Message):
        e_message(context, expression)
    else:
        assert False, errors.EXPR_NOT_RECOGNIZED.format(expr=expression)
