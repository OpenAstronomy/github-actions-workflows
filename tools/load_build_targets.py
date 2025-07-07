# /// script
# requires-python = "==3.12"
# dependencies = [
#     "click==8.2.1",
#     "pyyaml==6.0.2",
# ]
# ///
import json
import os
import re

import click
import yaml

MACHINE_TYPE = {
    "linux": "ubuntu-latest",
    "macos": "macos-latest",
    "windows": "windows-latest",
}

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
        return MACHINE_TYPE["macos"]
    if "win" in target:
        return MACHINE_TYPE["windows"]
    return MACHINE_TYPE["linux"]


def get_cibw_build(target):
    if target in {"linux", "macos", "windows"}:
        return CIBW_BUILD
    return target


def get_cibw_archs(target):
    """
    Handle non-native architectures

    cibw allows running non-native builds on various platforms:
    https://cibuildwheel.pypa.io/en/stable/options/#archs

    This logic overrides the "auto" flag based on OS and a list of supported
    non-native arch if a non-native arch is given for a particular platform in
    targets, rather than the user having to do this manually.
    """
    platform_archs = {
        # We now cross compile x86_64 on arm64 by default
        "macos": ["universal2", "x86_64"],
        # This is a list of supported eumulated arches on linux
        "linux": ["aarch64", "ppc64le", "s390x", "armv7l"],
    }
    for platform, archs in platform_archs.items():
        if platform in target:
            for arch in archs:
                if target.endswith(arch):
                    return arch

    # If no explict arch has been specified build both arm64 and x86_64 on macos
    if "macos" in target:
        return os.environ.get("CIBW_ARCHS", "arm64 x86_64")

    return CIBW_ARCHS


def get_artifact_name(target):
    artifact_name = re.sub(r"[\\ /:<>|*?\"']", "-", target)
    artifact_name = re.sub(r"-+", "-", artifact_name)
    return artifact_name


def get_matrix_item(target):
    extra_target_args = {}
    if isinstance(target, dict):
        extra_target_args = target
        target = extra_target_args.pop("target")
    return {
        "target": target,
        "runs-on": get_os(target),
        "CIBW_BUILD": get_cibw_build(target),
        "CIBW_ARCHS": get_cibw_archs(target),
        "artifact-name": get_artifact_name(target),
        **extra_target_args,
    }


if __name__ == "__main__":
    load_build_targets()
