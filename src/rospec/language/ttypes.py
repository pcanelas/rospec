from __future__ import annotations
import typing

from dataclasses import dataclass

import rospec.language.nodes as rospec_nodes


@dataclass(frozen=True)
class TType:
    pass


@dataclass(frozen=True)
class BasicType(TType):
    ttype: typing.Any

    def __eq__(self, other):
        return isinstance(other, BasicType) and self.ttype == other.ttype

    def __hash__(self):
        return 31 * hash(self.ttype)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.ttype


@dataclass(frozen=True)
class ArrayType(TType):
    ttype: TType
    max_size_refinement: int = 0

    def __eq__(self, other):
        return (
            isinstance(other, ArrayType)
            and self.ttype == other.ttype
            and self.max_size_refinement == other.max_size_refinement
        )

    def __hash__(self):
        return 31 * hash(self.ttype) and 31 * hash(self.max_size_refinement) and 31 * self.max_size_refinement

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.ttype}{f'[{self.max_size_refinement}]' if self.max_size_refinement > 0 else '[]'}"


@dataclass(frozen=True)
class EnumType(TType):
    ttypes: list[rospec_nodes.Identifier]

    def __eq__(self, other):
        return isinstance(other, EnumType) and self.ttypes == other.ttypes

    def __hash__(self):
        return 31 * hash("Enum") + sum([31 * hash(t) for t in self.ttypes])

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Enum[{', '.join(map(str, self.ttypes))}]"


@dataclass(frozen=True)
class RefinedType(TType):
    name: rospec_nodes.Identifier
    ttype: TType
    refinement: rospec_nodes.Expression

    def __eq__(self, other):
        return isinstance(other, RefinedType) and self.ttype == other.ttype and self.refinement == other.refinement

    def __hash__(self):
        return 31 * hash(self.ttype) + 31 * hash(self.refinement)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}:{self.ttype} where {{{self.refinement}}}"


@dataclass(frozen=True)
class OptionalType(TType):
    ttype: TType
    default_value: rospec_nodes.Expression

    def __eq__(self, other):
        return (
            isinstance(other, OptionalType) and self.ttype == other.ttype and self.default_value == other.default_value
        )

    def __hash__(self):
        return 31 * hash(self.ttype) + 31 * hash(self.default_value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.ttype} | {self.default_value}"


@dataclass(frozen=True)
class StructType(TType):
    fields: typing.Dict[str, TType]

    def __eq__(self, other):
        return isinstance(other, StructType) and self.fields == other.fields

    def __hash__(self):
        result = 0
        for k, v in self.fields.items():
            result += hash(k) + hash(v)
        return 31 * hash("Struct") + result

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Struct{{{', '.join([f'{k}: {v}' for k, v in self.fields.items()])}}}"


@dataclass(frozen=True)
class NodeT(TType):
    fields: StructType
    connections: typing.List[
        typing.Union[rospec_nodes.Publisher, rospec_nodes.Subscriber, rospec_nodes.Service, rospec_nodes.Action]
    ]
    frames: typing.List[rospec_nodes.TFTransform]

    def __eq__(self, other):
        return isinstance(other, NodeT) and self.fields == other.fields and self.connections == other.connections

    def __hash__(self):
        return 31 * hash("Node") + 31 * hash(self.fields) + 31 * hash(self.connections)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        fields_str = ", ".join([f"{k}: {v}" for k, v in self.fields.fields.items()])
        conn_str = ", ".join(map(str, self.connections))
        frames_str = ", ".join(map(str, self.frames))
        return f"Node{{{fields_str}}} | Connections: {conn_str} | Frames: {frames_str}"


@dataclass(frozen=True)
class PluginT(TType):
    fields: StructType
    connections: typing.List[
        typing.Union[rospec_nodes.Publisher, rospec_nodes.Subscriber, rospec_nodes.Service, rospec_nodes.Action]
    ]
    frames: typing.List[rospec_nodes.TFTransform]

    def __eq__(self, other):
        return isinstance(other, PluginT) and self.fields == other.fields and self.connections == other.connections

    def __hash__(self):
        return 31 * hash("PluginT") + 31 * hash(self.fields) + 31 * hash(self.connections)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        fields_str = ", ".join([f"{k}: {v}" for k, v in self.fields.fields.items()])
        conn_str = ", ".join(map(str, self.connections))
        frames_str = ", ".join(map(str, self.frames))
        return f"PluginT{{{fields_str}}} | Connections: {conn_str} | Frames: {frames_str}"


@dataclass(frozen=True)
class AbstractionType(TType):
    argument: TType
    result_type: TType

    def __eq__(self, other):
        return (
            isinstance(other, AbstractionType)
            and self.argument == other.argument
            and self.result_type == other.result_type
        )

    def __hash__(self):
        return 31 * hash(self.argument) + 31 * hash(self.result_type)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.argument} -> {self.result_type}"


t_bool = BasicType("bool")
t_int = BasicType("int")
t_uint8 = BasicType("uint8")
t_int32 = BasicType("int32")
t_uint32 = BasicType("uint32")
t_int64 = BasicType("int64")
t_float = BasicType("float")
t_double = BasicType("double")
t_float32 = BasicType("float32")
t_float64 = BasicType("float64")
t_string = BasicType("string")
t_bottom = BasicType("Bottom")

t_plugin = BasicType("Plugin")

t_comparison_type = AbstractionType(t_bottom, AbstractionType(t_bottom, t_bool))
t_bool_bool_bool = AbstractionType(t_bool, AbstractionType(t_bool, t_bool))
t_bool_bool = AbstractionType(t_bool, t_bool)

t_float_float_float = AbstractionType(t_float, AbstractionType(t_float, t_float))
t_float_float_bool = AbstractionType(t_float, AbstractionType(t_float, t_bool))

default_types = [
    t_bottom,
    t_bool,
    t_string,
    t_plugin,
    t_int,
    t_uint8,
    t_int32,
    t_uint32,
    t_int64,
    t_float,
    t_double,
    t_float32,
    t_float64,
]
