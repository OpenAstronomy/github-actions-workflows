import json
import os
import re

import click
import yaml

MACHINE_TYPE = {
    "linux": "ubuntu-latest",
    "macos": "macos-12",
    "windows": "windows-latest",
}
M1_RUNNER = "macos-14"

CIBW_BUILD = os.environ.get("CIBW_BUILD", "*")
CIBW_ARCHS = os.environ.get("CIBW_ARCHS", "auto")


@click.command()
@click.option("--targets", default="")
def load_build_targets(targets):
    """Script to load cibuildwheel targets for GitHub Actions workflow."""
    # Load list of targets
    targets = yaml.load(targets, Loader=yaml.BaseLoader)
    print(json.dumps(targets, indent=2))

    # Create matrix
    matrix = {"include": []}
    for target in targets:
        matrix["include"].append(get_matrix_item(target))

    # Output matrix
    print(json.dumps(matrix, indent=2))
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"matrix={json.dumps(matrix)}\n")


def get_os(target):
    if "macos" in target:
        if get_cibw_archs(target) in {"arm64", "universal2"}:
            return M1_RUNNER
        else:
            return MACHINE_TYPE["macos"]
    if "win" in target:
        return MACHINE_TYPE["windows"]
    return MACHINE_TYPE["linux"]


def get_cibw_build(target):
    if target in {"linux", "macos", "windows"}:
        return CIBW_BUILD
    return target


def get_cibw_archs(target):
    for arch in ["aarch64", "arm64", "universal2"]:
        if target.endswith(arch):
            return arch
    return CIBW_ARCHS


def get_artifact_name(target):
    artifact_name = re.sub(r"[\\ /:<>|*?\"']", "-", target)
    artifact_name = re.sub(r"-+", "-", artifact_name)
    return artifact_name


def get_matrix_item(target):
    return {
        "target": target,
        "os": get_os(target),
        "CIBW_BUILD": get_cibw_build(target),
        "CIBW_ARCHS": get_cibw_archs(target),
        "artifact-name": get_artifact_name(target),
    }


if __name__ == "__main__":
    load_build_targets()
