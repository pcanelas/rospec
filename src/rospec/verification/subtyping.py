import rospec.language.nodes as rospec_nodes

from rospec.language.ttypes import (
    TType,
    t_bottom,
    StructType,
    ArrayType,
    EnumType,
    AbstractionType,
    OptionalType,
    RefinedType,
    BasicType,
    t_float,
    t_int,
    t_double,
    t_string,
    t_float64,
)
from rospec.verification.context import Context
from rospec.verification.interpreter import interpret
from rospec.verification.substitution import inverse_substitution_expr_expr


def is_subtype_refined(context: Context, t: TType, u: TType) -> bool:
    if isinstance(t, RefinedType) and isinstance(u, RefinedType):
        # TODO: for now lets have the assumption that the left hand side is always ==
        assert isinstance(t.refinement, rospec_nodes.FunctionCall) and t.refinement.operator.name == "==", (
            f"{t.refinement} not =="
        )
        value = t.refinement.operands[1]  # TODO: Assuming that the right hand side is always already interpreted
        new_expr = inverse_substitution_expr_expr(u.name.name, value, u.refinement)
        is_satisfied = interpret(context, new_expr)
        assert isinstance(is_satisfied, bool)
        if not is_satisfied:
            context.add_error(f"Refinement {t.refinement} not satisfied in {u}")

        return is_satisfied

    elif isinstance(t, RefinedType):
        if t.ttype == t_string and isinstance(u, EnumType):
            # We assume the condition holds, this checks if enum value is in the enum, we assume a format for this
            expr = t.refinement
            assert isinstance(expr, rospec_nodes.FunctionCall)
            return expr.operands[1].value in [tee.name for tee in u.ttypes]

        result_subtype = is_subtype(context, t.ttype, u)
        # TODO: circular imports here
        # result_formation = isinstance(expr_form_module.expr_formation(context, t.refinement),
        #                              bool)
        return result_subtype  # and result_formation

    elif isinstance(u, RefinedType):
        result_subtype = is_subtype(context, t, u.ttype)
        # TODO: missing checking if u.e is true
        return result_subtype

    return False


def is_subtype_struct(context: Context, t: StructType, u: StructType) -> bool:
    # ##################################################################################################################
    # PROPERTY: ALL FIELDS OF t MUST BE FIELDS OF u
    # Check if the set of keys in t all belong to u
    result = True
    for key in t.fields.keys():
        if key not in u.fields:
            context.add_error(f">> Struct {t} is not a subtype of {u}, because the field {key} is not present in {u}")
            result = False

    # ##################################################################################################################
    # PROPERTY: ALL NON-OPTIONAL VALUES IN u MUST EXIST IN t
    for u_key, u_value in u.fields.items():
        if not isinstance(u_value, OptionalType) and u_key not in t.fields:
            context.add_error(f"Struct {t} is not a subtype of {u}, because the field {u_key} is not present in {t}")
            result = False

    # ##################################################################################################################
    # PROPERTY: FOR FIELDS THAT EXIST IN BOTH t AND u, THE TYPE OF t MUST BE A SUBTYPE OF THE TYPE OF u
    for t_key, t_value in t.fields.items():
        if t_key in u.fields:
            u_value = u.fields[t_key]
            if not is_subtype(context, t_value, u_value):
                context.add_error(
                    f"Struct {t} is not a subtype of {u} :: {t_key} has type {t_value} and is not subtype of {u_value}"
                )
                result = False

    return result


def is_subtype(context: Context, t: TType, u: TType) -> bool:
    if t == u or t == t_bottom:
        return True
    if t in context.aliases:
        # TODO: we need a better way to handle these aliases
        return is_subtype(context, context.aliases[t], u)
    if u in context.aliases:  # TODO: Test edge cases to see if these work for everything
        return is_subtype(context, t, context.aliases[u])

    if t in [t_int, t_float, t_double, t_float64] and u in [t_float, t_double, t_float64]:
        # For now we assume these are all equivalent
        return True

    if u == t_string and isinstance(t, EnumType):
        return True

    if isinstance(t, BasicType) and isinstance(u, EnumType):
        return t in u.ttypes

    if isinstance(t, OptionalType):
        return is_subtype(context, t.ttype, u)

    if isinstance(u, OptionalType):
        return is_subtype(context, t, u.ttype)

    if isinstance(t, RefinedType) or isinstance(u, RefinedType):
        return is_subtype_refined(context, t, u)

    if isinstance(t, ArrayType):
        return (
            isinstance(u, ArrayType)
            and t.max_size_refinement == u.max_size_refinement
            and is_subtype(context, t.ttype, u.ttype)
        )

    if isinstance(t, EnumType) and isinstance(u, EnumType):
        # An enum type t is subtype of enum type u, if all elements of t are also elements of u
        return isinstance(u, EnumType) and all(t_elem in u.ttypes for t_elem in t.ttypes)

    if isinstance(t, StructType) and isinstance(u, StructType):
        return is_subtype_struct(context, t, u)

    if isinstance(t, AbstractionType):
        return True  # User cannot define these, they will always be true because we ensure they are correct internally

    return False
