# Centralized error messages for ROSpec

# CLI and file errors
SPEC_FILE_NOT_FOUND = "CLI: Specification file {spec} not found"
SPEC_READ_ERROR = "CLI: An error occurred while reading the specification file {spec}: {error}"

# Frontend parsing errors
DEFAULT_VALUE_NON_OPTIONAL = "Parsing: Non-optional variable {variable} was provided with a default value {value}"
MISSING_DEFAULT_OPTIONAL = "Parsing: Optional variable {variable} is missing a default value"
UNEXPECTED_TOPIC_TYPE = "Parsing: Unexpected type of expression ({type}) for topic name in connection"

# Expression Formation errors
LITERAL_NOT_SUBTYPE = "TypeMismatch: Literal {field} of type {ttype} is not a subtype of {expected_type}"
EXPRESSION_NOT_SUBTYPE = "TypeMismatch: Expression {expression} of type {ttype} is not a subtype of {expected_type}"
MESSAGE_NOT = "TypeMismatch: Message {message} of type {ttype} is not a message"
MESSAGE_NOT_BASIC_TYPE = "TypeMismatch: Message {message} of type {ttype} is not a standard message"
MESSAGE_EXPR_NOT_SUBTYPE = "TypeMismatch: Fields of the message expression {ttype} do not match the ones defined"
ARRAY_EXPECTED = "TypeMismatch: Expression {field} is not an array"
VARIABLE_NOT_FUNCTION = "TypeMismatch: Variable {variable} is not a function"
EXPRESSION_NOT_RECOGNIZED = (
    "ROSpecFormationError: Expression not found when checking the expression formation for {expr}"
)

# Statement Formation errors
VARIABLE_ALREADY_EXISTS = "VariableDefinitionError: Variable {variable} already defined with type {ttype}"
STATEMENT_NOT_RECOGNIZED = (
    "ROSpecFormationError: Statement not found when checking the statement formation for {statement}"
)

# Definition Formation errors
MESSAGE_FIELD_ERROR = (
    "MessageAliasError: Field {field} of type {ttype} is not present in the aliased message {expected_type}"
)
MESSAGE_FIELD_NOT_SUBTYPE = "MessageAliasError: Field {field} of type {ttype} is not subtype of {expected_type} from the field type in the aliased message"

POLICY_NOT_STRUCT = "ROSpecFormationError: Policy type {policy} does not exist"
POLICY_ALREADY_DEFINED = "ROSpecFormationError: Policy instance with name {policy} already defined"

POLICY_FIELD_NOT_FOUND = "ROSpecFormationError: Policy field {field} not found in policy type {policy_type}, expected one of the following fields:{fields}"
POLICY_FIELD_NOT_SUBTYPE = (
    "ROSpecFormationError: Policy field {field} defined with value {value} does not match defined type {ttype}"
)

PARAMETER_DEFAULT_INVALID = (
    "ParameterError: Default value {value} for parameter {parameter} does not match defined type {ttype}"
)

FIELDS_MISMATCH = "Subtyping: Fields in {fields} do not match {expected_fields}"
FIELD_NOT_SUBTYPE_POLICY = "Subtyping: Field {field} is not a subtype of {expected_type}"
NODE_ALREADY_DEFINED = "Node {name} already defined in context"
NODE_INSTANCE_NOT_SUBTYPE = "Node instance {name} is not subtype of {type} where {struct}"
DEPENDENCY_NOT_SATISFIED = "Dependency {dependency} not satisfied in {name}"
PLUGIN_ALREADY_DEFINED = "Plugin {name} already defined in context"
PLUGIN_INSTANCE_NOT_SUBTYPE = "Plugin instance {name} is not subtype of {type} where {struct}"
PUBLISHER_NOT_FOUND = "Publisher not found for subscriber {topic}"
PROVIDER_NOT_FOUND = "Provider not found for service {topic}"
REFINEMENT_NOT_SATISFIED = "Refinement {refinement} not satisfied in {context}"
STRUCT_FIELD_MISSING = "Struct {t} is not a subtype of {u}, because the field {key} is not present in {u}"
STRUCT_FIELD_EXTRA = "Struct {t} is not a subtype of {u}, because the field {key} is not present in {t}"
FIELD_TYPE_MISMATCH = "{key} has type {t_value} and is not subtype of {u_value}"
QOS_FIELDS_MISMATCH = "QoS fields do not match: {consumer_keys} != {provider_keys}"
QOS_RULE_NOT_SATISFIED = "QoS rule {field} not satisfied: {consumer_value} !< {provider_value}"
QOS_RULES_NOT_SATISFIED = "QoS rules not satisfied for subscriber and publisher"
POLICIES_NOT_FOUND = "Policies not found for consumer or provider"
POLICY_NOT_FOUND_CONSUMER = "Policy not found for consumer when publisher has policies"
POLICY_FOUND_NO_PUBLISHER = "Policy found for subscriber when publisher has no policies"
POLICIES_MISMATCH = "Policies do not match: {consumer_keys} != {provider_keys}"
COLOR_FORMAT_NOT_SATISFIED = "Color format not satisfied: {consumer} != {provider}"
UNSUPPORTED_TYPE = "Unsupported type: {type}"
UNSUPPORTED_EXPR_TYPE = "Unsupported expression type: {type}"
EXPR_NOT_SUPPORTED = "Expression {expr} of type {type} not supported"
