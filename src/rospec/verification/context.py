import copy
from dataclasses import dataclass, field
from typing import Any

from rospec.language.nodes import Connection
from rospec.language.ttypes import TType


@dataclass
class Context:
    typing: dict[str, TType] = field(default_factory=dict)
    aliases: dict[TType, TType] = field(default_factory=dict)
    connections: dict[str, list[Connection]] = field(default_factory=dict)

    # This is extra information that we use for during the verification
    # This information is useful for the interpretation and error collection
    errors: list[str] = field(default_factory=list)
    values: dict[str, Any] = field(default_factory=dict)

    def add_typing(self, name: str, ttype: TType) -> "Context":
        copy_ctx = copy.deepcopy(self)
        copy_ctx.typing[name] = ttype
        return copy_ctx

    def add_alias(self, ttype: TType, alias: TType) -> "Context":
        copy_ctx = copy.deepcopy(self)
        copy_ctx.aliases[ttype] = alias
        return copy_ctx

    def add_connections(self, name: str, connections: list[Connection]) -> "Context":
        copy_ctx = copy.deepcopy(self)
        copy_ctx.connections[name] = connections
        return copy_ctx

    def get_typing(self, name: str) -> TType:
        return self.typing[name]

    def get_alias(self, ttype: TType) -> TType:
        return self.aliases[ttype]

    def add_error(self, error: str) -> "Context":
        self.errors.append(error)
        return self

    def add_value(self, name: str, value: Any) -> "Context":
        copy_ctx = copy.deepcopy(self)
        copy_ctx.values[name] = value
        return copy_ctx

    def copy_context(self) -> "Context":
        return Context(
            typing=copy.deepcopy(self.typing),
            aliases=copy.deepcopy(self.aliases),
            connections=copy.deepcopy(self.connections),
            errors=list(self.errors),
            values=copy.deepcopy(self.values),
        )

    def __str__(self):
        result = "Context(\n"
        for key, value in self.typing.items():
            result += f"{key}: {value}, "
        for key, value in self.aliases.items():
            result += f"{key} = {value}, "
        for key, value in self.connections.items():
            result += f"{key} |-> {value}, "
        for key, value in self.values.items():
            result += f"{key} := {value}, "
        result += ")"
        return result
