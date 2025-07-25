# Custom Error Exception that receives a message
class ROSpecError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


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
VARIABLE_ALREADY_DEFINED = "ROSpecFormationError: Variable {variable} already defined in the program"
CONFIGURABLE_INFORMATION_NOT_FOUND = "ParameterError: Configurable information {configurable_information} instanced in {node_instance} was not found in the node type {node_type}"
DEPENDENCY_NOT_SATISFIED = "ParameterDependencyError: {component_instance_type} instance configurations for {name} do not respect the dependency defined in the {component_instance_type} type: {dependency}"
CONNECTION_REFINEMENT_NOT_SATISFIED = "ConnectionError: Connection property {refinement} not satisfied in: {connection}"
CONNECTION_NOT_SUBTYPE = (
    "ConnectionError: Message type for {connection} does not match the expected type {expected_type}"
)
PROVIDER_NOT_FOUND = "ConnectionError: Provider not found for {connection} in {component}"
BROADCASTER_NOT_FOUND = "TFError: Broadcaster not found for listener {listener} in {component}"
BROADCASTER_MULTIPLE_PARENTS = "TFError: Broadcast {child_frame} to {parent_frame} has multiple parents: {parents}"
BROADCASTER_CYCLIC = "TFError: Broadcast {child_frame} to {parent_frame} is cyclic"
PUBLISHER_NOT_FOUND = "ConnectionError: Publisher not found for subscriber {topic} in {component}"

# Subtyping errors
STRUCT_FIELD_MISSING = "ParameterError: The configuration {key}: {ttype} is missing from the component instance"
STRUCT_FIELD_EXTRA = "ParameterError: The configuration {key}: {ttype} is not defined in the component type, expected one of the following configurations: {fields}"
REFINEMENT_NOT_SATISFIED = "Refinement {refinement} not satisfied in {context}"

# Utils errors
QOS_FIELDS_MISMATCH = "QoSError: QoS fields do not match: {consumer_keys} != {provider_keys}"
QOS_RULE_NOT_SATISFIED = "QoSError: Mismatch in quality of service for {qos_field}, consumer value {consumer_value} does not match provider value {provider_value}"

POLICIES_NOT_FOUND = "ROSpecFormationError: Policies for either consumer or provider are set to None"
POLICY_NOT_FOUND_CONSUMER = (
    "PolicyError: Policy not found for consumer, publisher defines the following policies: {policies}"
)
POLICY_FOUND_NO_PUBLISHER = (
    "PolicyError: Policy not found for provider, consumer defines the following policies: {policies}"
)
POLICIES_MISMATCH = (
    "PolicyError: Provider and consumer do not provide the same set of policies: {consumer_keys} != {provider_keys}"
)
COLOR_FORMAT_NOT_SATISFIED = (
    "PolicyError: Color format policy for consumer ({consumer}) does not match the format for provider ({provider})"
)
UNSUPPORTED_TYPE = "Unsupported type: {type}"

# Other errors
EXPR_NOT_SUPPORTED = "Expression {expr} of type {type} not supported"
