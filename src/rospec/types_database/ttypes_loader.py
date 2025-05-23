import os

from rospec.language.frontend import parse_expression
from rospec.language.nodes import TypeAlias, Identifier
from rospec.language.ttypes import (
    t_float_float_float,
    t_bool_bool_bool,
    t_bool_bool,
    t_float_float_bool,
    AbstractionType,
    t_bottom,
    t_int,
    t_string,
    t_bool,
    ArrayType,
    StructType,
    EnumType,
    t_float,
    t_plugin,
)
from rospec.verification.context import Context

# Get the directory of this file (ttypes_loader.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
ROS_TYPES_PATH = os.path.join(current_dir, "ttypes")


def get_ros_types(context: Context) -> Context:
    for filename in os.listdir(ROS_TYPES_PATH):
        with open(os.path.join(ROS_TYPES_PATH, filename), "r") as f:
            specification = f.read()
            if not specification:
                continue
            # TODO: This assumes that the messages we have internally always follow the same format
            specifications = specification.split("\n\n")

            for spec in specifications:
                type_alias: TypeAlias = parse_expression(spec, "message_type")
                new_ttype, ttype = type_alias.new_ttype, type_alias.old_ttype
                context = context.add_alias(new_ttype, ttype)

    return context


def get_native_types(context: Context) -> Context:
    context.aliases[t_plugin] = t_string

    context.typing["+"] = t_float_float_float
    context.typing["-"] = t_float_float_float
    context.typing["*"] = t_float_float_float
    context.typing["/"] = t_float_float_float
    context.typing["%"] = t_float_float_float

    context.typing["and"] = t_bool_bool_bool
    context.typing["or"] = t_bool_bool_bool
    context.typing["!"] = t_bool_bool

    context.typing["<"] = t_float_float_bool
    context.typing["<="] = t_float_float_bool
    context.typing[">"] = t_float_float_bool
    context.typing[">="] = t_float_float_bool
    context.typing["=="] = t_float_float_bool
    context.typing["!="] = t_float_float_bool

    context.typing["content"] = AbstractionType(t_bottom, t_bottom)
    context.typing["len"] = AbstractionType(ArrayType(t_bottom), t_int)
    context.typing["count"] = AbstractionType(ArrayType(t_bottom), t_int)
    context.typing["publishers"] = AbstractionType(t_string, ArrayType(t_bottom))
    context.typing["subscribers"] = AbstractionType(t_string, ArrayType(t_bottom))
    context.typing["exists"] = AbstractionType(t_string, t_bool)

    context.typing["qos"] = StructType(
        {
            "history": EnumType(
                [
                    Identifier(name="KeepLast", ttype=t_bottom),
                    Identifier(name="KeepAll", ttype=t_bottom),
                ]
            ),
            "depth": t_float,
            "reliability": EnumType(
                [
                    Identifier(name="BestEffort", ttype=t_bottom),
                    Identifier(name="Reliable", ttype=t_bottom),
                ]
            ),
            "durability": EnumType(
                [
                    Identifier(name="TransientLocal", ttype=t_bottom),
                    Identifier(name="Volatile", ttype=t_bottom),
                ]
            ),
            "liveliness": EnumType(
                [
                    Identifier(name="Automatic", ttype=t_bottom),
                    Identifier(name="ManualByTopic", ttype=t_bottom),
                ]
            ),
            "deadline": t_float,
            "lifespan": t_float,
            "duration": t_float,
        }
    )

    context.typing["color_format"] = StructType(
        {
            "format": EnumType(
                [
                    Identifier(name="RGB8", ttype=t_bottom),
                    Identifier(name="Grayscale", ttype=t_bottom),
                ]
            ),
        }
    )

    return context
