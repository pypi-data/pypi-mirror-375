import os
import re
from typing import Union

from truefoundry.deploy._autogen.models import (
    PythonBuild,
)


def get_application_fqn_from_deployment_fqn(deployment_fqn: str) -> str:
    if not re.search(r":\d+$", deployment_fqn):
        raise ValueError(
            "Invalid `deployment_fqn` format. A deployment fqn is supposed to end with a version number"
        )
    application_fqn, _ = deployment_fqn.rsplit(":", 1)
    return application_fqn


def get_deployment_fqn_from_application_fqn(
    application_fqn: str, version: Union[str, int]
) -> str:
    return f"{application_fqn}:{version}"


def find_list_paths(data, parent_key="", sep="."):
    list_paths = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            list_paths.extend(find_list_paths(value, new_key, sep))
    elif isinstance(data, list):
        list_paths.append(parent_key)
        for i, value in enumerate(data):
            new_key = f"{parent_key}[{i}]"
            list_paths.extend(find_list_paths(value, new_key, sep))
    return list_paths


def _validate_file_path(project_root_path: str, file_path: str):
    file_absolute_path = os.path.join(project_root_path, file_path)
    if not os.path.exists(file_absolute_path):
        raise FileNotFoundError(
            f"file {file_path} not found. file path should be relative to your project root path: {project_root_path}."
        )


def validate_paths(python_build: PythonBuild, source_dir: str):
    if not python_build.python_dependencies:
        return

    if not os.path.exists(source_dir):
        raise ValueError(f"project root path {source_dir!r} of does not exist")
    if (
        python_build.python_dependencies.type == "pip"
        and python_build.python_dependencies.requirements_path
    ):
        _validate_file_path(
            source_dir,
            python_build.python_dependencies.requirements_path,
        )
    if python_build.python_dependencies.type == "uv":
        _validate_file_path(source_dir, "uv.lock")
        _validate_file_path(source_dir, "pyproject.toml")
    if python_build.python_dependencies.type == "poetry":
        _validate_file_path(source_dir, "pyproject.toml")
        _validate_file_path(source_dir, "poetry.lock")
