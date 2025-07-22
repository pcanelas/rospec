import os
import glob
import pytest

from rospec.language.frontend import parse_program

# Gather all .rospec files under examples/
def get_rospec_files():
    rospec_files = []
    for root, _, files in os.walk("examples/"):
        for file in files:
            if file.endswith(".rospec"):
                rospec_files.append(os.path.join(root, file))
    return rospec_files

@pytest.mark.parametrize("rospec_path", get_rospec_files())
def test_parsing(rospec_path):
    with open(rospec_path, "r") as r_file:
        program = r_file.read()
    try:
        parse_program(program)
    except Exception as e:
        pytest.fail(f"Parsing failed for {rospec_path}: {e}")
