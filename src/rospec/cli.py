import sys
import argparse

from loguru import logger
from typing import Optional

from rospec.language.frontend import parse_program
from rospec.language.nodes import Program
from rospec.types_database.ttypes_loader import get_ros_types, get_native_types
from rospec.verification.context import Context
from rospec.verification.definition_formation import program_formation


def process_errors(errors: list[str], output: str) -> None:
    """
    Process and print errors based on the output type.
    """
    if output == "stdout":
        for err in errors:
            logger.error(err)
    else:
        with open(output, "w") as f:
            for err in errors:
                f.write(f"{err}\n")
        logger.info(f"Errors written to {output}")


def verify_program(context: Context, parsed_program: Program) -> list[str]:
    """
    Verify the parsed program and return a list of errors.
    """
    return program_formation(context, parsed_program)


def load_context() -> Context:
    context: Context = Context()
    context = get_ros_types(context)
    context = get_native_types(context)
    logger.info("Successfully loaded ROS types into context")
    return context


def merge_specifications(specifications: list[str]) -> str:
    """
    Merge multiple specification files into a single string.
    """
    merged_specification = ""
    for spec in specifications:
        try:
            with open(spec, "r") as f:
                merged_specification += f.read() + "\n"
                logger.info(f"Successfully read specification from {spec}")
        except FileNotFoundError:
            logger.error(f"Specification file {spec} not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"An error occurred while reading {spec}: {str(e)}")
            sys.exit(1)
    return merged_specification


def main(args: Optional[list[str]] = None) -> None:
    logger.enable("rospec")
    parser = argparse.ArgumentParser(description="specification and verification of ROS-based robot software")

    parser.add_argument(
        "--specifications",
        "--name-list",
        nargs="+",
        help="file path to the specification files written in rospec (.rospec)",
        required=True,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="type of output expected (stdout or filename.txt)",
        default="stdout",
    )
    args = parser.parse_args(args)

    program: str = merge_specifications(args.specifications)
    parsed_program: Program = parse_program(program)
    context: Context = load_context()
    errors: list[str] = verify_program(context, parsed_program)
    process_errors(errors, args.output)


if __name__ == "__main__":
    main()
