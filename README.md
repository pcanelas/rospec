# rospec

[![ruff](https://github.com/pcanelas/rospec/actions/workflows/ruff.yaml/badge.svg)](https://github.com/pcanelas/rospec/actions/workflows/ruff.yaml)
[![pytest](https://github.com/pcanelas/rospec/actions/workflows/pytest.yaml/badge.svg)](https://github.com/pcanelas/rospec/actions/workflows/pytest.yaml)

## Description

rospec is a domain specification language to specify configurations of ROS components and their integration.
Current approaches focus on runtime verification or require system execution to detect misconfigurations.
rospec allows component writer developers to express specifications for their ROS components, while component integrators
select their components and provide their configurations --- any mismatches are raised statically prior to execution.
By providing a formal way to describe the expected configuration and integration of ROS components, rospec helps identify
misconfigurations early in the development process, preventing costly errors during system execution.

The tool can be used to validate various aspects of ROS components configuration and integration, including but not only:

- Topic, service, and action connections between nodes;
- Parameter value constraints and dependencies;
- Component compatibility requirements.

## Installation

rospec can be installed using either pip or by building from source. We recommend
using a virtual environment to avoid conflicts with other Python packages.

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [uv (>=0.7.6)](https://docs.astral.sh/uv/getting-started/installation/)

### Setup

#### Option 1: Install from PyPI (when available)

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install rospec
uv add rospec
```

#### Option 2: Install from source

1. Clone the repository:

   ```bash
   git clone https://github.com/pcanelas/rospec.git
   cd rospec
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. Install in development mode (if you plan to contribute):

   ```bash
   uv sync --dev
   ```

## Usage

rospec offers a command line interface (CLI) for parsing and verifying specifications.
To run the CLI, you can use the following command:

```bash
rospec --specifications path/to/your/spec.rospec
```

Or if installed in development mode:

```bash
uv run rospec --specifications path/to/your/spec.rospec
```

### Basic Example

Here's a simple example of a rospec specification containing the specification for one component and its integration:

```
node type move_group_type {
   param elbow_joint/max_acceleration: double where {_ >= 0};
   optional param elbow_joint/max_velocity: double = 2.0;
   optional param elbow_joint/has_velocity_limits: bool = false;
   optional param elbow_joint/has_acceleration_limits: bool = false;
} where {
    exists(elbow_joint/max_acceleration) -> elbow_joint/has_acceleration_limits;
}

system {
   node instance move_group: move_group_type {
       param elbow_joint/max_acceleration = 0;
       param elbow_joint/max_velocity = 3.14;
       param elbow_joint/has_acceleration_limits = false;
       param elbow_joint/has_velocity_limits = false;
   }
}
```

To verify this specification:

```bash
rospec --specifications examples/evaluation/detectable-364801.rospec
```

## Development

For development setup and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Quick Development Setup

```bash
git clone https://github.com/pcanelas/rospec.git
cd rospec
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --dev
uv run pre-commit install
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run ruff format
uv run ruff check --fix
```

## Authors

This project is a research project within the [Software and Societal Systems Department](https://s3d.cmu.edu/) (S3D)
and the [Robotics Institute](https://www.ri.cmu.edu/) at Carnegie Mellon University, and [LASIGE](https://lasige.pt/)
at University of Lisbon, by:

- [Paulo Canelas](https://pcanelas.com/)
- [Bradley Schmerl](https://www.cs.cmu.edu/~schmerl/)
- [Alcides Fonseca](https://wiki.alcidesfonseca.com/)
- [Christopher S. Timperley](https://chris.timperley.info/)

## Acknowledgements

This work was supported by Fundação para a Ciência e Tecnologia (FCT) in the LASIGE Research Unit under the ref.
(UID/00408/2025 and EXPL/CCI-COM/1306/2021), and the CMU Portugal Dual PhD program (SFRH/BD/151469/2021).

## Publications

[The Usability Argument for ROS-based Robot Architectural Description Languages](https://acme.able.cs.cmu.edu/pubs/uploads/pdf/2024_plateau_rospecusabilityCanelas_RospecADL_2025.pdf),
at PLATEAU 2025.

[Understanding Misconfigurations in ROS: An Empirical Study and Current Approaches](https://doi.org/10.1145/3650212.3680350/),
at ISSTA 2024.
