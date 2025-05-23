from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import List, Union, Optional, Dict
from dataclasses import dataclass, field

from rospec.language.ttypes import TType, OptionalType, BasicType


class TransformType(Enum):
    BROADCAST = "broadcast"
    LISTEN = "listen"

    def __str__(self) -> str:
        return self.value


class ConfigurationType(Enum):
    PARAMETER = "param"
    CONTEXT = "context"
    ARGUMENT = "argument"
    FIELD = "field"
    SETTING = "setting"

    def __str__(self) -> str:
        return self.value


class FieldType(Enum):
    REQUEST = "request"
    FEEDBACK = "feedback"
    RESPONSE = "response"
    RESULT = "result"

    def __str__(self) -> str:
        return self.value


class ServiceActionRole(Enum):
    PROVIDES = "provides"
    CONSUMES = "consumes"

    def __str__(self) -> str:
        return self.value


@dataclass
class ROSpecNode(ABC):
    """Base class for ROSpec nodes."""

    dependency: Optional["Expression"]


@dataclass
class Statement(ABC):
    """Base class for Statements."""

    pass


@dataclass(frozen=True)
class Expression(ABC):
    """Base class for ROS expression."""

    ttype: TType


# ----------------------------------------------------------------------------------------------------------- Expression
@dataclass(repr=True, frozen=True)
class Literal(Expression):
    """Represents a literal value with a type."""

    value: Union[int, float, bool, str]

    def __str__(self):
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)


@dataclass(repr=True, frozen=True)
class Identifier(Expression):
    """Represents a named identifier in a ROS component."""

    name: str

    def __str__(self):
        return f"{self.name}"


@dataclass(repr=True, frozen=True)
class Message(Expression):
    """Represents a message with a type and optional fields."""

    fields: Dict[Identifier, Expression] = field(default_factory=dict)

    def __hash__(self) -> int:
        return 31 * hash("Message") + 31 * hash(tuple(self.fields))

    def __str__(self):
        return f"{self.ttype} {{ {', '.join(map(str, self.fields))} }}"


@dataclass(repr=True, frozen=True)
class Array(Expression):
    """Represents an array of expressions."""

    elements: List[Expression]

    def __hash__(self):
        return 31 * hash("Array") + 31 * hash(tuple(self.elements))

    def __str__(self):
        return f"[{', '.join(map(str, self.elements))}]"


@dataclass(repr=True, frozen=True)
class ArrayAccess(Expression):
    """Represents an array of expressions."""

    indexes: List[Expression]  # these elements are the indexes, e.g., a[0][1]
    target: Expression

    def __hash__(self):
        return 31 * hash("ArrayAccess") + 31 * hash(tuple(self.indexes)) + 31 * hash(self.target)

    def __str__(self):
        return f"{self.target}[{', '.join(map(str, self.indexes))}]"


@dataclass(repr=True, frozen=True)
class FunctionCall(Expression):
    """Represents a function call or operator expression."""

    operator: Identifier
    operands: List[Expression]

    def __hash__(self):
        return 31 * hash("FunctionCall") + 31 * hash(self.operator) + 31 * hash(tuple(self.operands))

    def __str__(self):
        if len(self.operands) == 1 and self.operator.name == "-":  # if it is is_unary
            return f"-{self.operands[0]}"
        elif self.operator.name in [
            "+",
            "-",
            "*",
            "/",
            "<",
            ">",
            "<=",
            ">=",
            "==",
            "!=",
            "->",
            "and",
            "or",
        ]:  # is_binary operation
            return f"{self.operands[0]} {self.operator.name} {self.operands[1]}"

        return f"{self.operator}({', '.join(map(str, self.operands))})"


# ------------------------------------------------------------------------------------------------------------ Statement
@dataclass(repr=True)
class PolicyAttached(Statement):
    """Represents the definition of a Policy type in a ROS component."""

    policy_type: Identifier
    policy_instance: Identifier

    def __str__(self):
        return f"@{self.policy_type}{{{self.policy_instance}}}\n"


@dataclass(repr=True)
class ConfigurableInformation(Statement):
    """Represents configurable information fields in the different statements. All of them follow a similar format, so
    they are all merged together into one."""

    configuration_ttype: ConfigurationType
    identifier: Identifier
    ttype: TType
    value: Optional[Union[Literal, Identifier, Message, Array, FunctionCall]]

    def __str__(self):
        is_optional = "optional " if isinstance(self.ttype, OptionalType) else ""
        value = f" = {self.value}" if self.value else ""
        return f"\n{is_optional}{self.configuration_ttype} {self.identifier}{value}"


@dataclass(repr=True)
class Field(Statement):
    """Represents a field with an optional value and type in ROS."""

    field_type: Optional[FieldType]  # We will pretty much ignore these for now
    identifier: Identifier
    ttype: TType

    def __str__(self):
        field_type = f"{self.field_type} " if self.field_type else ""
        return f"{field_type}field {self.identifier}"


@dataclass(repr=True)
class Publisher(Statement):
    """Defines a connection type within a ROS node."""

    node: Identifier
    topic: Expression
    policies: Optional[dict[str, PolicyAttached]]

    def __str__(self):
        return f"{self.node} publishes to {self.topic}: {self.topic.ttype}"


@dataclass(repr=True)
class Subscriber(Statement):
    """Defines a connection type within a ROS node."""

    node: Identifier
    topic: Expression
    policies: Optional[dict[str, PolicyAttached]]

    def __str__(self):
        return f"{self.node} subscribes to {self.topic}: {self.topic.ttype}"


@dataclass(repr=True)
class Service(Statement):
    role: ServiceActionRole
    node: Identifier
    topic: Expression
    policies: Optional[dict[str, PolicyAttached]]

    def __str__(self):
        return f"{self.node} {self.role} service {self.topic}: {self.topic.ttype}"


@dataclass(repr=True)
class Action(Statement):
    role: ServiceActionRole
    node: Identifier
    topic: Expression
    policies: Optional[dict[str, PolicyAttached]]

    def __str__(self):
        return f"{self.node} {self.role} action {self.topic}: {self.topic.ttype}"


@dataclass(repr=True)
class TFTransform(Statement):
    node: Identifier
    transform: TransformType
    parent_frame: Expression
    child_frame: Expression
    policies: Optional[dict[str, PolicyAttached]]

    # TODO: static transforms do not have a QoS

    def __str__(self):
        return f"{self.transform} {self.parent_frame} to {self.child_frame}"


@dataclass(repr=True)
class Remapping(Statement):
    """Specifies a remapping directive between identifiers in a ROS node."""

    node: Identifier
    remap_from: Identifier
    remap_to: Identifier

    def __str__(self):
        return f"remaps {self.remap_from} to {self.remap_to};"


# ----------------------------------------------------------------------------------------------------------------- Node
@dataclass(repr=True)
class TypeAlias(ROSpecNode):
    new_ttype: BasicType
    old_ttype: TType

    def __str__(self):
        return f"type alias {self.new_ttype}: {self.old_ttype}"


@dataclass(repr=True)
class MessageAlias(ROSpecNode):
    new_ttype: TType
    old_ttype: TType
    fields: list[ConfigurableInformation] = field(default_factory=list)

    def __str__(self):
        fields_str = ", ".join(map(str, self.fields))
        content = f"{{{fields_str}"
        if self.dependency:
            content += f"}} where {{{self.dependency}}}"
        else:
            content += "}"
        return f"message alias {self.new_ttype}: {self.old_ttype} {content}"


@dataclass(repr=True)
class PolicyInstance(ROSpecNode):
    """Represents the definition of a Policy type in a ROS component."""

    instance_name: Identifier
    policy_name: Identifier
    parameters: list[ConfigurableInformation] = field(default_factory=list)

    def __str__(self):
        content = "{" + ", ".join(map(str, self.parameters)) + "}"
        return f"policy instance {self.instance_name} : {self.policy_name} {content}"


@dataclass(repr=True)
class NodeType(ROSpecNode):
    """Represents the definition of a Node type in a ROS component."""

    name: Identifier

    configurable_information: list[ConfigurableInformation] = field(default_factory=list)
    publishers: list[Publisher] = field(default_factory=list)
    subscribers: list[Subscriber] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    frames: list[TFTransform] = field(default_factory=list)


@dataclass(repr=True)
class NodeInstance(ROSpecNode):
    """Represents the definition of a Node instance."""

    name: Identifier
    node_type: Identifier

    configurable_information: list[ConfigurableInformation] = field(default_factory=list)
    publishers: list[Publisher] = field(default_factory=list)
    subscribers: list[Subscriber] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    frames: list[TFTransform] = field(default_factory=list)
    remaps: list[Remapping] = field(default_factory=list)


@dataclass(repr=True)
class PluginType(ROSpecNode):
    name: Identifier

    configurable_information: list[ConfigurableInformation] = field(default_factory=list)
    publishers: list[Publisher] = field(default_factory=list)
    subscribers: list[Subscriber] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    frames: list[TFTransform] = field(default_factory=list)


@dataclass(repr=True)
class PluginInstance(ROSpecNode):
    name: Identifier
    plugin_ttype: Identifier

    configurable_information: list[ConfigurableInformation] = field(default_factory=list)
    publishers: list[Publisher] = field(default_factory=list)
    subscribers: list[Subscriber] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    frames: list[TFTransform] = field(default_factory=list)
    remaps: list[Remapping] = field(default_factory=list)


@dataclass(repr=True)
class System(ROSpecNode):
    """Contains a list of programs overall"""

    node_instances: list[NodeInstance] = field(default_factory=list)
    plugin_instances: list[NodeInstance] = field(default_factory=list)

    def __str__(self):
        return f"{self.node_instances}\n{self.plugin_instances}"


# ----------------------------------------------------------------------------------------------------- Program & System
@dataclass(repr=True)
class Program:
    """Defines a complete ROS program structure with all ROSpec nodes."""

    policy_instances: List[PolicyInstance] = field(default_factory=list)
    node_types: List[NodeType] = field(default_factory=list)
    node_instances: List[NodeInstance] = field(default_factory=list)
    plugin_types: List[PluginType] = field(default_factory=list)
    plugin_instances: List[PluginInstance] = field(default_factory=list)
    message_aliases: List[MessageAlias] = field(default_factory=list)
    type_aliases: List[TypeAlias] = field(default_factory=list)

    system: List[System] = field(default_factory=list)

    def __str__(self):
        # Implement proper string representation
        result = ""
        for node in self.policy_instances:
            result += str(node) + "\n"

        for node in self.node_types:
            result += str(node) + "\n"

        for node in self.node_instances:
            result += str(node) + "\n"

        for node in self.plugin_types:
            result += str(node) + "\n"

        for node in self.plugin_instances:
            result += str(node) + "\n"

        for node in self.message_aliases:
            result += str(node) + "\n"

        for node in self.type_aliases:
            result += str(node) + "\n"

        for node in self.system:
            result += str(node) + "\n"

        return result


Connection = Union[Publisher, Subscriber, Service, Action, TFTransform]
