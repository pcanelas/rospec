import os
import glob

import pytest

from rospec.language.frontend import parse_program
from rospec.types_database.ttypes_loader import get_ros_types, get_native_types
from rospec.verification.context import Context
from rospec.verification.definition_formation import program_formation


# Gather all matching test file pairs
def get_test_cases(test_type: str):
    evaluation_dir = "examples/evaluation"
    expected_dir = "examples/expected"

    cases = []
    for rospec_path in glob.glob(os.path.join(evaluation_dir, f"{test_type}-*.rospec")):
        filename = os.path.basename(rospec_path)
        case_id = filename.replace(f"{test_type}-", "").replace(".rospec", "")
        expected_path = os.path.join(expected_dir, f"expected-{case_id}.txt")

        if test_type == "detectable" and os.path.exists(expected_path):
            cases.append((rospec_path, expected_path, case_id))
        elif test_type == "documentation":
            cases.append((rospec_path, expected_path, case_id))
        else:
            raise FileNotFoundError(f"Expected file for {filename} not found!")

    return cases


@pytest.fixture(scope="module")
def ros_context() -> Context:
    """Create the ROS types context once per module."""
    return get_native_types(get_ros_types(Context()))


@pytest.mark.parametrize("rospec_path, expected_path, case_id", get_test_cases("detectable"))
def test_detectable(rospec_path, expected_path, case_id, ros_context):
    with open(rospec_path, "r") as r_file:
        program = r_file.read()

    with open(expected_path, "r") as e_file:
        expected_output = e_file.read().strip().split("\n")

    errors = []

    try:
        errors = program_formation(ros_context, parse_program(program))
    except Exception as e:
        pytest.fail(f"Exception in case {case_id}: {e}")

    assert errors == expected_output, f"Mismatch in case {case_id}"


@pytest.mark.parametrize("rospec_path, expected_path, case_id", get_test_cases("documentation"))
def test_documentation(rospec_path, expected_path, case_id, ros_context):
    with open(rospec_path, "r") as r_file:
        program = r_file.read()

    errors = []

    try:
        errors = program_formation(ros_context, parse_program(program))
    except Exception as e:
        pytest.fail(f"Exception in case {case_id}: {e}")

    assert len(errors) == 0, f"Mismatch in case {case_id} - expected no errors"
