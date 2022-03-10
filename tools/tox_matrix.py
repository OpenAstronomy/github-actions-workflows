import json
import re

import click
import yaml


@click.command()
@click.option("--envs", default="")
@click.option("--libraries", default="")
@click.option("--posargs", default="")
@click.option("--toxdeps", default="")
@click.option("--toxargs", default="")
@click.option("--pytest", default="true")
@click.option("--coverage", default="")
@click.option("--conda", default="auto")
@click.option("--display", default="false")
@click.option("--runner", default="")
@click.option("--default-python", default="")
def load_tox_targets(envs, libraries, posargs, toxdeps, toxargs, pytest,
                     coverage, conda, display, runner, default_python):
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

    # Default images to use for runners
    runners = {
        "linux": "ubuntu-latest",
        "macos": "macos-latest",
        "windows": "windows-latest",
    }
    custom_runners = yaml.load(runner, Loader=yaml.BaseLoader)
    if isinstance(custom_runners, dict):
        runners.update(custom_runners)
    print(json.dumps(runners, indent=2))

    # Default string parameters which can be overwritten by each env
    string_parameters = {
        "posargs": posargs,
        "toxdeps": toxdeps,
        "toxargs": toxargs,
        "pytest": pytest,
        "coverage": coverage,
        "conda": conda,
        "display": display,
    }

    # Create matrix
    matrix = {"include": []}
    for env in envs:
        matrix["include"].append(get_matrix_item(
            env,
            global_libraries=global_libraries,
            global_string_parameters=string_parameters,
            runners=runners,
            default_python=default_python,
        ))

    # Output matrix
    print(json.dumps(matrix, indent=2))
    print(f"::set-output name=matrix::{json.dumps(matrix)}")


def get_matrix_item(env, global_libraries, global_string_parameters,
                    runners, default_python):

    # define spec for each matrix include (+ global_string_parameters)
    item = {
        "os": None,
        "toxenv": None,
        "python_version": None,
        "name": None,
        "pytest_flag": None,
        "libraries_brew": None,
        "libraries_brew_cask": None,
        "libraries_apt": None,
        "libraries_choco": None,
    }
    for string_param, default in global_string_parameters.items():
        env_value = env.get(string_param)
        item[string_param] = default if env_value is None else env_value

    # set os and toxenv
    for k, v in runners.items():
        if k in env:
            platform = k
            item["os"] = env.get("runner", v)
            item["toxenv"] = env[k]
    assert item["os"] is not None and item["toxenv"] is not None

    # set python_version
    m = re.search("^py(2|3)([0-9]+)", item["toxenv"])
    if m is not None:
        major, minor = m.groups()
        item["python_version"] = f"{major}.{minor}"
    else:
        item["python_version"] = env.get("default_python") or default_python

    # set name
    item["name"] = env.get("name") or item["toxenv"]

    # set pytest_flag
    if item["pytest"] == "true":
        sep = "\\" if platform == "windows" else "/"
        item["pytest_flag"] = (
            rf"--junitxml=junit{sep}test-results.xml "
            rf"--cov-report=xml:${{GITHUB_WORKSPACE}}{sep}coverage.xml")
    else:
        item["pytest_flag"] = ""

    # set libraries
    env_libraries = env.get("libraries")
    if isinstance(env_libraries, str) and len(env_libraries.strip()) == 0:
        env_libraries = {}  # no libraries requested for environment
    libraries = global_libraries if env_libraries is None else env_libraries
    for manager in ["brew", "brew_cask", "apt", "choco"]:
        item[f"libraries_{manager}"] = " ".join(libraries.get(manager, []))

    # set "auto" conda value
    if item["conda"] == "auto":
        item["conda"] = "true" if "conda" in item["toxenv"] else "false"

    # inject toxdeps for conda
    if item["conda"] == "true" and "tox-conda" not in item["toxdeps"].lower():
        item["toxdeps"] = ("tox-conda " + item["toxdeps"]).strip()

    # verify values
    assert item["pytest"] in {"true", "false"}
    assert item["conda"] in {"true", "false"}
    assert item["display"] in {"true", "false"}

    return item


if __name__ == "__main__":
    load_tox_targets()
