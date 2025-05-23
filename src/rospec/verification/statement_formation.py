from typing import Union, Any

from rospec.language.nodes import (
    Statement,
    ConfigurableInformation,
    Expression,
    Field,
    Remapping,
    Action,
    Service,
    Subscriber,
    Publisher,
    TFTransform,
    Identifier,
)
from rospec.language.ttypes import TType, OptionalType
from rospec.verification.context import Context
from rospec.verification.expression_formation import expr_formation
from rospec.verification.type_formation import ty_formation


# It includes: spd_param, spd_arg, spd_ctx, spd_field, spd_setting
def spd_configuration(context: Context, config: ConfigurableInformation) -> (str, TType):
    return config.identifier.name, config.ttype


def spd_opt_configuration(context: Context, config: ConfigurableInformation) -> (str, TType):
    assert isinstance(config.ttype, OptionalType)
    ty_formation(context, config.ttype.ttype)
    # We don't verify the optional value here because it is verified later at instance
    # Why: we may not have the values to check this, we would only be able to check if this is a literal
    return config.identifier.name, config.ttype


def spi_configuration(context: Context, config: ConfigurableInformation) -> (str, Expression):
    expr_formation(context, config.value)
    return config.identifier.name, config.value


def s_field(context: Context, field: Field) -> (str, TType):
    ty_formation(context, field.ttype)
    return field.identifier.name, field.ttype


def s_remap(context: Context, remap: Remapping) -> (str, str):
    # t = context.get_typing(remap.node.name)
    # u = context.get_typing(remap.remap_from.name)
    # TODO: these should be present indeed -- need more work to support remappings
    return remap.remap_from.name, remap.remap_to.name


def s_connection(
    context: Context, connection: Union[Publisher, Subscriber, Service, Action]
) -> Union[Publisher, Subscriber, Service, Action]:
    expr_formation(context, connection.node)
    ty_formation(context, connection.topic.ttype)
    return connection


def s_frame(context: Context, frame: TFTransform) -> TFTransform:
    if isinstance(frame.parent_frame, Identifier):
        assert frame.parent_frame.name not in context.typing
    if isinstance(frame.child_frame, Identifier):
        assert frame.child_frame.name not in context.typing
    return frame


def st_formation(context: Context, st: Statement) -> Any:
    if isinstance(st, ConfigurableInformation):
        if st.value is None:
            if isinstance(st.ttype, OptionalType):
                return spd_opt_configuration(context, st)
            return spd_configuration(context, st)
        # For sure this is an instantiation of a configurable parameter
        return spi_configuration(context, st)
    elif isinstance(st, Field):
        return s_field(context, st)
    elif isinstance(st, Remapping):
        return s_remap(context, st)
    elif isinstance(st, (Publisher, Subscriber, Service, Action)):
        return s_connection(context, st)
    elif isinstance(st, TFTransform):
        return s_frame(context, st)
    assert False, f"Unknown statement type: {st}"
