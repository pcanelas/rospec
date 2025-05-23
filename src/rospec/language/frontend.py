import copy
import logging
import os

from lark import Lark, Token
from lark.visitors import Interpreter, visit_children_decor

from rospec.language.nodes import (
    Program,
    ConfigurableInformation,
    Remapping,
    Identifier,
    Literal,
    FunctionCall,
    Expression,
    PolicyInstance,
    Message,
    PolicyAttached,
    Publisher,
    Subscriber,
    ServiceActionRole,
    Service,
    TFTransform,
    Action,
    NodeType,
    PluginType,
    PluginInstance,
    Array,
    NodeInstance,
    MessageAlias,
    TypeAlias,
    System,
    ConfigurationType,
    TransformType,
    Field,
    FieldType,
    ArrayAccess,
)

from rospec.language.ttypes import (
    t_bottom,
    TType,
    RefinedType,
    EnumType,
    ArrayType,
    BasicType,
    OptionalType,
    t_bool_bool,
    t_comparison_type,
    t_bool_bool_bool,
    t_float_float_float,
    t_string,
    StructType,
)
from rospec.language.utils import (
    convert_literal,
    filter_nodes_by_type,
    aux_node_plugin_fields_constructor,
    infer_qos_type,
    merge_and_dependencies,
    replace_empty_in_attributes,
)
from rospec.verification.substitution import inverse_substitution_expr_expr, inverse_expr_substitution_in_type


class TreeToROSpec(Interpreter):
    def __init__(self):
        self.logger = logging.getLogger()
        super().__init__()

    @visit_children_decor
    def rospec(self, args):
        """Parses the top-level rospec file and returns the first parsed component."""
        return args[0]

    @visit_children_decor
    def program(self, args):
        """Parses the top-level rospec file and returns the first parsed component."""
        return Program(
            policy_instances=filter_nodes_by_type(PolicyInstance, args),
            node_types=filter_nodes_by_type(NodeType, args),
            node_instances=filter_nodes_by_type(NodeInstance, args),
            plugin_types=filter_nodes_by_type(PluginType, args),
            plugin_instances=filter_nodes_by_type(PluginInstance, args),
            message_aliases=filter_nodes_by_type(MessageAlias, args),
            type_aliases=filter_nodes_by_type(TypeAlias, args),
            system=filter_nodes_by_type(System, args),
        )

    @visit_children_decor
    def system(self, args):
        node_instances = filter_nodes_by_type(NodeInstance, args)
        plugin_instances = filter_nodes_by_type(PluginInstance, args)
        return System(node_instances=node_instances, plugin_instances=plugin_instances, dependency=None)

    @visit_children_decor
    def policy_instance(self, args):
        name: Identifier = args[0]
        policy_name: Identifier = args[1]
        parameters: list[ConfigurableInformation] = args[2:]
        return PolicyInstance(instance_name=name, policy_name=policy_name, parameters=parameters, dependency=None)

    @visit_children_decor
    def setting_instance(self, args):
        setting_name: Identifier = args[0]
        setting_value = args[1]
        return ConfigurableInformation(
            configuration_ttype=ConfigurationType("setting"),
            identifier=setting_name,
            ttype=infer_qos_type(setting_name),
            value=setting_value,
        )

    @visit_children_decor
    def plugin_type(self, args):
        name: Identifier = args[0]
        attributes, dependencies = aux_node_plugin_fields_constructor(args[1:], name.name)
        dependency: Expression = merge_and_dependencies(dependencies)
        dependency = inverse_substitution_expr_expr(old="_", new=name, expr=dependency)
        attributes = replace_empty_in_attributes(attributes, name.name)
        return PluginType(
            name=name,
            configurable_information=attributes[ConfigurableInformation],
            publishers=attributes[Publisher],
            subscribers=attributes[Subscriber],
            services=attributes[Service],
            actions=attributes[Action],
            frames=attributes[TFTransform],
            dependency=dependency,
        )

    @visit_children_decor
    def plugin_instance(self, args):
        name: Identifier = args[0]
        plugin_ttype = args[1]
        attributes, dependencies = aux_node_plugin_fields_constructor(args[2:], name.name)
        return PluginInstance(
            name=name,
            plugin_ttype=plugin_ttype,
            configurable_information=attributes[ConfigurableInformation],
            publishers=attributes[Publisher],
            subscribers=attributes[Subscriber],
            services=attributes[Service],
            actions=attributes[Action],
            frames=attributes[TFTransform],
            remaps=attributes[Remapping],
            dependency=None,
        )

    @visit_children_decor
    def node_type(self, args):
        name: Identifier = args[0]
        attributes, dependencies = aux_node_plugin_fields_constructor(args[1:], name.name)
        dependency: Expression = merge_and_dependencies(dependencies)
        dependency = inverse_substitution_expr_expr(old="_", new=name, expr=dependency)
        attributes = replace_empty_in_attributes(attributes, name.name)
        return NodeType(
            name=name,
            configurable_information=attributes[ConfigurableInformation],
            publishers=attributes[Publisher],
            subscribers=attributes[Subscriber],
            services=attributes[Service],
            actions=attributes[Action],
            frames=attributes[TFTransform],
            dependency=dependency,
        )

    @visit_children_decor
    def node_type_statement(self, args):
        return args[0]

    @visit_children_decor
    def node_instance(self, args):
        name: Identifier = args[0]
        node_type: Identifier = args[1]
        attributes, dependencies = aux_node_plugin_fields_constructor(args[2:], name.name)
        attributes = replace_empty_in_attributes(attributes, name.name)
        return NodeInstance(
            name=name,
            node_type=node_type,
            configurable_information=attributes[ConfigurableInformation],
            publishers=attributes[Publisher],
            subscribers=attributes[Subscriber],
            services=attributes[Service],
            actions=attributes[Action],
            frames=attributes[TFTransform],
            remaps=attributes[Remapping],
            dependency=None,
        )

    @visit_children_decor
    def node_instance_statements(self, args):
        return args[0]

    @visit_children_decor
    def message_alias(self, args):
        new_ttype: TType = args[0]
        old_ttype: TType = args[1]
        fields: list[ConfigurableInformation] = filter_nodes_by_type(Field, args[2:])
        dependencies: list[Expression] = args[2 + len(fields) :]
        dependency: Expression = merge_and_dependencies(dependencies)
        return MessageAlias(new_ttype=new_ttype, old_ttype=old_ttype, fields=fields, dependency=dependency)

    # message_type: "message" ttype "{" fields+ "}" ("where" "{" (expression ";")+ "}")?
    @visit_children_decor
    def message_type(self, args):
        new_ttype: BasicType = args[0]
        fields: list[ConfigurableInformation] = filter_nodes_by_type(Field, args[1:])
        dependency: Expression = merge_and_dependencies(args[1 + len(fields) :])
        ttype = StructType(fields={field.identifier.name: field.ttype for field in fields})
        return TypeAlias(new_ttype=new_ttype, old_ttype=ttype, dependency=dependency)

    @visit_children_decor
    def fields(self, args):
        field_type = FieldType(args[0]) if isinstance(args[0], Token) else None
        args = args[1:] if field_type is not None else args
        return Field(field_type=field_type, identifier=args[0], ttype=args[1])

    @visit_children_decor
    def type_alias(self, args):
        new_ttype: BasicType = args[0]
        old_ttype: TType = args[1]
        return TypeAlias(new_ttype=new_ttype, old_ttype=old_ttype, dependency=None)

    @visit_children_decor
    def policy_attach(self, args):
        return PolicyAttached(policy_type=args[0], policy_instance=args[1])

    @visit_children_decor
    def configurable_type(self, args):
        is_optional: bool = isinstance(args[0], Token) and args[0].type == "OPTIONAL"

        # This ensures that we always have the right number of arguments
        if len(args) == 4:
            if not is_optional:
                raise ValueError("Attempted to provide default value for non-optional.")
            else:
                raise ValueError(f"Missing default value for optional {args}.")

        if is_optional:
            args = args[1:]

        configuration_type = ConfigurationType(args[0].value)
        identifier: Identifier = args[1]
        ttype: TType = args[2]
        ttype = inverse_expr_substitution_in_type("_", identifier, ttype)
        default_value = args[3] if len(args) > 3 else None
        if default_value is not None:
            ttype = OptionalType(ttype, default_value)

        identifier = Identifier(name=identifier.name, ttype=ttype)

        return ConfigurableInformation(
            configuration_ttype=configuration_type,
            identifier=identifier,
            ttype=ttype,
            value=None,
        )

    @visit_children_decor
    def configurable_instance(self, args):
        configuration_type: ConfigurationType = ConfigurationType(args[0].value)
        identifier: Identifier = args[1]
        ttype: TType = t_bottom
        value = args[2]
        return ConfigurableInformation(
            configuration_ttype=configuration_type,
            identifier=identifier,
            ttype=ttype,
            value=value,
        )

    @visit_children_decor
    def connection(self, args):
        topic, ttype = args[1], args[2]
        ttype = inverse_expr_substitution_in_type("_", topic, ttype)

        if isinstance(topic, Identifier):
            topic = Identifier(name=topic.name, ttype=ttype)
        elif isinstance(topic, FunctionCall):
            topic = FunctionCall(operator=topic.operator, operands=copy.deepcopy(topic.operands), ttype=ttype)
        else:
            raise ValueError(f"Unexpected topic type: {type(topic)}")
        connection_constructor = {
            "publishes to": Publisher,
            "subscribes to": Subscriber,
        }[args[0].value]
        return connection_constructor(node=Identifier(name="_", ttype=t_bottom), topic=topic, policies=None)

    @visit_children_decor
    def service_action(self, args):
        role: ServiceActionRole = ServiceActionRole(args[0].value)
        service_action_constructor = {"service": Service, "action": Action}[args[1].value]
        expr: Identifier = args[2]
        topic_ttype = args[3]

        if isinstance(expr, Identifier):
            topic = Identifier(name=expr.name, ttype=topic_ttype)
        elif isinstance(expr, FunctionCall):
            topic = FunctionCall(operator=expr.operator, operands=copy.deepcopy(expr.operands), ttype=topic_ttype)
        else:
            raise ValueError(f"Unexpected topic type: {type(expr)}")
        return service_action_constructor(
            role=role, node=Identifier(name="_", ttype=t_bottom), topic=topic, policies=None
        )

    @visit_children_decor
    def frames(self, args):
        return TFTransform(
            transform=TransformType(args[0].value),
            parent_frame=args[1],
            child_frame=args[2],
            node=Identifier(name="_", ttype=t_bottom),
            policies=None,
        )

    @visit_children_decor
    def remapping(self, args):
        return Remapping(node=Identifier(name="_", ttype=t_bottom), remap_from=args[0], remap_to=args[1])

    @visit_children_decor
    def ttype(self, args):
        assert isinstance(args, TType)
        return args

    @visit_children_decor
    def basic_type(self, args):
        return BasicType(args[0].value)

    @visit_children_decor
    def refined_type(self, args):
        return RefinedType(name=Identifier(name="_", ttype=args[0]), ttype=args[0], refinement=args[1])

    @visit_children_decor
    def enum_type(self, args):
        args = [Identifier(name=arg.name, ttype=t_string) for arg in args]
        return EnumType(args)

    @visit_children_decor
    def array_type(self, args):
        basic_type: BasicType = BasicType(args[0].value)
        literals: list[tuple] = [convert_literal(x.value, x.type) for x in args[1:]]

        if len(literals) == 0:
            return ArrayType(basic_type, 0)
        result: ArrayType = ArrayType(basic_type, literals[0][0])
        for literal in literals[1:]:
            result = ArrayType(result, literal[0])
        return result

    @visit_children_decor
    def condition(self, args):
        return args[0]

    @visit_children_decor
    def parens_exr(self, args):
        return args[0]

    @visit_children_decor
    def expr(self, args):
        return args[0]

    @visit_children_decor
    def expression_name(self, args):
        return Identifier(name=args[0].value, ttype=t_bottom)

    @visit_children_decor
    def literal_expr(self, args):
        value, ttype = convert_literal(args[0].value, args[0].type)
        return Literal(value=value, ttype=ttype)

    @visit_children_decor
    def boolean_expr(self, args):
        left = args[0] if not isinstance(args[0], list) else args[0][0]
        right = args[2] if not isinstance(args[2], list) else args[2][0]
        return FunctionCall(
            operator=Identifier(name=args[1].value, ttype=t_bool_bool_bool),
            operands=[left, right],
            ttype=t_bool_bool_bool,
        )

    @visit_children_decor
    def compare_expr(self, args):
        return FunctionCall(
            operator=Identifier(name=args[1].value, ttype=t_comparison_type),
            operands=[args[0], args[2]],
            ttype=t_comparison_type,
        )

    @visit_children_decor
    def not_expr(self, args):
        operand = Identifier(name=args[0].value, ttype=t_bool_bool)
        return FunctionCall(operator=operand, operands=[args[1]], ttype=t_bool_bool)

    @visit_children_decor
    def minus_expr(self, args):
        if isinstance(args[1], Literal):
            return Literal(value=-args[1].value, ttype=args[1].ttype)
        return FunctionCall(operator=args[0], operands=[args[1]], ttype=args[1].ttype)

    @visit_children_decor
    def arithmetic_expr(self, args):
        return FunctionCall(
            operator=Identifier(name=args[1].value, ttype=t_float_float_float),
            operands=[args[0], args[2]],
            ttype=t_float_float_float,
        )

    @visit_children_decor
    def invocation_expr(self, args):
        expressions = [args[1]] if len(args) > 1 else []
        return FunctionCall(operator=args[0], operands=expressions, ttype=t_bottom)

    @visit_children_decor
    def variable_expr(self, args):
        return args[0]

    @visit_children_decor
    def msg_fields_expr(self, args):
        fields = dict()
        for i in range(1, len(args), 2):
            fields[args[i]] = args[i + 1]
        return Message(ttype=BasicType(args[0].name), fields=fields)

    @visit_children_decor
    def array_expr(self, args):
        return Array(elements=args, ttype=t_bottom)

    @visit_children_decor
    def access_array_expr(self, args):
        return ArrayAccess(target=args[0], indexes=args[1:], ttype=t_bottom)


# =============================================================================
# Creation of the parser for the entire program
def parse_program(program: str):
    # Get the directory of the current file (frontend.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(current_dir, "grammar.lark")

    parse_tree = Lark.open(
        grammar_path,
        parser="lalr",
        start="start",
        cache=True,
    ).parse(program)
    return TreeToROSpec().visit(parse_tree)


def parse_expression(expression: str, start: str):
    # Get the directory of the current file (frontend.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    grammar_path = os.path.join(current_dir, "grammar.lark")

    parse_tree = Lark.open(
        grammar_path,
        parser="lalr",
        start=start,
        cache=True,
    ).parse(expression)
    return TreeToROSpec().visit(parse_tree)
