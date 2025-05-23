from rospec.language.ttypes import (
    t_bool,
    TType,
    BasicType,
    RefinedType,
    OptionalType,
    StructType,
    EnumType,
    ArrayType,
    AbstractionType,
    default_types,
)
from rospec.verification.context import Context
from rospec.verification.subtyping import is_subtype


def type_basic(context: Context, ttype: BasicType):
    # t_int, t_bool, t_float and t_string are the basic native types of the language
    if ttype in default_types:  # TODO: add all default types here
        return
    assert ttype in context.aliases, f"Type {ttype} not found in context"


def type_where(context: Context, ttype: RefinedType):
    assert is_subtype(context, ttype.refinement.ttype, t_bool)
    ty_formation(context, ttype.ttype)  # Check the underlying type


def type_optional(context: Context, ttype: OptionalType):
    u: TType = ttype.default_value.ttype
    t: TType = ttype.ttype
    ty_formation(context, t)
    assert is_subtype(context, u, t), f"Default value {ttype.default_value} not a subtype of {t}"


def type_struct(context: Context, ttype: StructType):
    for _, t in ttype.fields.items():
        ty_formation(context, t)


def type_enum(context: Context, ttype: EnumType):
    pass
    # TODO: check this better


def type_array(context: Context, ttype: ArrayType):
    ty_formation(context, ttype.ttype)


def type_abstraction(context: Context, ttype: AbstractionType):
    ty_formation(context, ttype.argument)
    ty_formation(context, ttype.result_type)


def ty_formation(context: Context, ttype: TType):
    if isinstance(ttype, BasicType):
        type_basic(context, ttype)
    elif isinstance(ttype, RefinedType):
        type_where(context, ttype)
    elif isinstance(ttype, OptionalType):
        type_optional(context, ttype)
    elif isinstance(ttype, StructType):
        type_struct(context, ttype)
    elif isinstance(ttype, EnumType):
        type_enum(context, ttype)
    elif isinstance(ttype, ArrayType):
        type_array(context, ttype)
    elif isinstance(ttype, AbstractionType):
        type_abstraction(context, ttype)
    else:
        assert False, f"Type {ttype} ({type(ttype)})not found in context"
