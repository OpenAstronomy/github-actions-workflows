import json
import re

import click
import yaml

MACHINE_TYPE = {
    "linux": "ubuntu-20.04",
    "macos": "macos-10.15",
    "windows": "windows-2019",
}

DEFAULT_PYTHON = "3.x"


@click.command()
@click.option("--envs", default="")
@click.option("--libraries", default="")
@click.option("--posargs", default="")
@click.option("--toxargs", default="")
@click.option("--pytest", default="")
def load_tox_targets(envs, libraries, posargs, toxargs, pytest):
    """Script to load tox targets for GitHub Actions workflow."""
    # Load envs config
    envs = yaml.load(envs, Loader=yaml.BaseLoader)
    print(json.dumps(envs, indent=2))

    # Load global libraries config
    global_libraries = {
        "brew": [],
        "brew-cask": [],
        "apt": [],
        "choco": [],
    }
    libraries = yaml.load(libraries, Loader=yaml.BaseLoader)
    if libraries is not None:
        global_libraries.update(libraries)
    print(json.dumps(global_libraries, indent=2))

    # Create matrix
    matrix = {"include": []}
    for env in envs:
        matrix["include"].append(
            get_matrix_item(env, global_libraries=global_libraries, global_posargs=posargs,
                            global_toxargs=toxargs, global_pytest=pytest)
        )

    # Output matrix
    print(json.dumps(matrix, indent=2))
    print(f"::set-output name=matrix::{json.dumps(matrix)}")


def get_matrix_item(env, global_libraries, global_posargs, global_toxargs, global_pytest):

    # define spec for each matrix include
    item = {
        "os": None,
        "toxenv": None,
        "python_version": None,
        "name": None,
        "pytest_flag": None,
        "toxargs": None,
        "posargs": None,
        "libraries_brew": None,
        "libraries_brew_cask": None,
        "libraries_apt": None,
        "libraries_choco": None,
    }

    # set os and toxenv
    for k, v in MACHINE_TYPE.items():
        if k in env:
            platform = k
            item["os"] = v
            item["toxenv"] = env[k]
    assert item["os"] is not None and item["toxenv"] is not None

    # set python_version
    m = re.search("^py(2|3)([0-9]+)", item["toxenv"])
    if m is not None:
        major, minor = m.groups()
        item["python_version"] = f"{major}.{minor}"
    else:
        item["python_version"] = DEFAULT_PYTHON

    # set name
    item["name"] = env.get("name", False) or item["toxenv"]

    # set pytest_flag
    env_pytest = env.get("pytest")
    pytest = global_pytest if env_pytest is None else env_pytest
    pytest = str(pytest).lower() == "true"
    if pytest:
        if platform == "windows":
            item["pytest_flag"] = (r"--junitxml=junit\test-results.xml "
                                   r"--cov-report=xml:${Env:GITHUB_WORKSPACE}\coverage.xml")
        else:
            item["pytest_flag"] = (r"--junitxml=junit/test-results.xml "
                                   r"--cov-report=xml:${GITHUB_WORKSPACE}/coverage.xml")
    else:
        item["pytest_flag"] = ""

    # set toxargs
    env_toxargs = env.get("toxargs")
    item["toxargs"] = global_toxargs if env_toxargs is None else env_toxargs

    # set posargs
    env_posargs = env.get("posargs")
    item["posargs"] = global_posargs if env_posargs is None else env_posargs

    # set libraries
    env_libraries = env.get("libraries")
    libraries = global_libraries if env_libraries is None else env_libraries
    item["libraries_brew"] = " ".join(libraries.get("brew", []))
    item["libraries_brew_cask"] = " ".join(libraries.get("brew_cask", []))
    item["libraries_apt"] = " ".join(libraries.get("apt", []))
    item["libraries_choco"] = " ".join(libraries.get("choco", []))

    return item


if __name__ == "__main__":
    load_tox_targets()
