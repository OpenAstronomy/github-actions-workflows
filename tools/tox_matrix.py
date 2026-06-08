# /// script
# requires-python = "==3.12"
# dependencies = [
#     "click==8.2.1",
#     "packaging==25.0",
#     "pyyaml==6.0.2",
# ]
# ///
import json
import os
import re
from copy import copy

import click
import yaml
from packaging.version import Version


@click.command()
@click.option("--envs", default="")
@click.option("--libraries", default="")
@click.option("--posargs", default="")
@click.option("--toxdeps", default="")
@click.option("--toxargs", default="")
@click.option("--pytest", default="true")
@click.option("--pytest-results-summary", default="false")
@click.option("--coverage", default="")
@click.option("--conda-packages")
@click.option("--conda-channels", default="conda-forge")
@click.option("--setenv", default="")
@click.option("--display", default="false")
@click.option("--cache-path", default="")
@click.option("--cache-key", default="")
@click.option("--cache-restore-keys", default="")
@click.option("--artifact-path", default="")
@click.option("--artifact-archive", default="true")
@click.option("--artifact-include-hidden-files", default="false")
@click.option("--artifact-if-no-files-found", default="warn")
@click.option("--runs-on", default="")
@click.option("--default-python", default="")
@click.option("--timeout-minutes", default="360")
@click.option("--supported-pythons", default='["3"]')
def load_tox_targets(
    envs,
    libraries,
    posargs,
    toxdeps,
    toxargs,
    pytest,
    pytest_results_summary,
    coverage,
    conda_packages,
    conda_channels,
    setenv,
    display,
    cache_path,
    cache_key,
    cache_restore_keys,
    artifact_path,
    artifact_archive,
    artifact_include_hidden_files,
    artifact_if_no_files_found,
    runs_on,
    default_python,
    timeout_minutes,
    supported_pythons,
):
    """Script to load tox targets for GitHub Actions workflow."""

    if not supported_pythons:
        supported_pythons = ['3']
    elif isinstance(supported_pythons, str):
        supported_pythons = json.loads(supported_pythons)

    # Load envs config
    envs = yaml.load(envs.replace("\\n", "\n"), Loader=yaml.BaseLoader)
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
    default_runs_on = {
        "linux": "ubuntu-latest",
        "macos": "macos-latest",
        "windows": "windows-latest",
    }
    custom_runs_on = yaml.load(runs_on, Loader=yaml.BaseLoader)
    if isinstance(custom_runs_on, dict):
        default_runs_on.update(custom_runs_on)
    print(json.dumps(default_runs_on, indent=2))

    # Default string parameters which can be overwritten by each env
    string_parameters = {
        "posargs": posargs,
        "toxdeps": toxdeps,
        "toxargs": toxargs,
        "pytest": pytest,
        "pytest-results-summary": pytest_results_summary,
        "coverage": coverage,
        "conda-packages": conda_packages,
        "conda-channels": json.dumps(conda_channels.split()),
        "setenv": setenv,
        "display": display,
        "cache-path": cache_path,
        "cache-key": cache_key,
        "cache-restore-keys": cache_restore_keys,
        "artifact-path": artifact_path,
        "artifact-archive": artifact_archive,
        "artifact-include-hidden-files": artifact_include_hidden_files,
        "artifact-if-no-files-found": artifact_if_no_files_found,
        "timeout-minutes": timeout_minutes,
    }

    # Create matrix
    matrix = {"include": []}
    for env in envs:
        matrix_item = get_matrix_item(
            env,
            global_libraries=global_libraries,
            global_string_parameters=string_parameters,
            runs_on=default_runs_on,
            default_python=default_python,
        )

        # check if we need to expand python versions from a glob (i.e. py*, py3*, py31*, etc.)
        toxenv = matrix_item["toxenv"]
        if toxenv.startswith("py") and "*" in toxenv.split("-")[0]:
            toxenvs = expand_python_versions(toxenv, python_versions=supported_pythons)

            for expanded_toxenv, python_version in toxenvs:
                expanded_matrix_item = copy(matrix_item)
                expanded_matrix_item["toxenv"] = expanded_toxenv
                expanded_matrix_item["name"] = expanded_matrix_item["name"].replace(
                    toxenv, expanded_toxenv
                )
                expanded_matrix_item["python_version"] = python_version
                matrix["include"].append(expanded_matrix_item)
        else:
            matrix["include"].append(matrix_item)

    # Output matrix
    print(json.dumps(matrix, indent=2))
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"matrix={json.dumps(matrix)}\n")


def get_matrix_item(env, global_libraries, global_string_parameters, runs_on, default_python):

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
        "conda-packages": None,
        "cache-path": None,
        "cache-key": None,
        "cache-restore-keys": None,
        "artifact-name": None,
        "artifact-path": None,
        "artifact-archive": None,
        "artifact-include-hidden-files": None,
        "artifact-if-no-files-found": None,
        "timeout-minutes": None,
    }
    for string_param, default in global_string_parameters.items():
        env_value = env.get(string_param)
        item[string_param] = default if env_value is None else env_value

    # set os and toxenv
    for k, v in runs_on.items():
        if k in env:
            platform = k
            item["os"] = env.get("runs-on", v)
            item["toxenv"] = env[k]
    assert item["os"] is not None and item["toxenv"] is not None

    # set python_version
    python_version = env.get("python-version")
    m = re.search("^py(2|3)([0-9]+t?)", item["toxenv"])
    if python_version is not None:
        item["python_version"] = python_version
    elif m is not None:
        major, minor = m.groups()
        item["python_version"] = f"{major}.{minor}"
    else:
        item["python_version"] = env.get("default_python") or default_python

    # set name
    item["name"] = env.get("name") or f"{item['toxenv']} ({item['os']})"

    # set artifact-name (replace invalid path characters)
    item["artifact-name"] = re.sub(r"[\\ /:<>|*?\"']", "-", item["name"])
    item["artifact-name"] = re.sub(r"-+", "-", item["artifact-name"])

    # set pytest_flag
    item["pytest_flag"] = ""
    sep = r"\\" if platform == "windows" else "/"
    if item["pytest"] == "true":
        if item["pytest-results-summary"] == "true":
            item["pytest_flag"] += rf"--junitxml ${{GITHUB_WORKSPACE}}{sep}results.xml "

    env_conda_channels = env.get("conda-channels")
    if isinstance(env_conda_channels, str) and len(env_conda_channels.strip()) == 0:
        item["conda-channels"] = json.dumps(env_conda_channels.split())

    # set libraries
    env_libraries = env.get("libraries")
    if isinstance(env_libraries, str) and len(env_libraries.strip()) == 0:
        env_libraries = {}  # no libraries requested for environment
    libraries = global_libraries if env_libraries is None else env_libraries
    for manager in ["brew", "brew_cask", "apt", "choco"]:
        item[f"libraries_{manager}"] = " ".join(libraries.get(manager, []))

    # make timeout-minutes a number
    item["timeout-minutes"] = int(item["timeout-minutes"])

    # verify values
    assert item["pytest"] in {"true", "false"}
    assert item["display"] in {"true", "false"}

    return item


def expand_python_versions(toxenv: str, python_versions: list[Version | str]) -> list[(str, str)]:
    """
    expand `py3*` into `py311`, `py312`, `py313`, etc. based on currently-supported Python versions

    :param version_glob: can be `py*`, `py3*`, `py30*`, `py31*` etc.
    """

    python_versions = [Version(version) for version in python_versions]

    toxenv_factors = toxenv.split("-")
    py_version_glob = toxenv_factors[0]
    if not py_version_glob.startswith("py"):
        raise ValueError(
            f'input "{py_version_glob}" is not a Python version Tox factor (must start with `py`)'
        )

    if "*" not in py_version_glob:
        return [py_version_glob]

    if not py_version_glob.endswith("*"):
        raise NotImplementedError(
            "Python version glob must end with a `*`; suffixes such as `t` are not yet supported"
        )

    major_version = py_version_glob[2]
    if major_version != "*":
        python_versions = [
            python_version
            for python_version in python_versions
            if python_version.major == int(major_version)
        ]

        minor_version = py_version_glob[3:]
        if minor_version_specifier := minor_version.split("*")[0] != "*":
            minor_version_base = int(minor_version_specifier) * 10
            python_versions = [
                python_version
                for python_version in python_versions
                if minor_version_base <= python_version.minor < minor_version_base + 10
            ]

    return [
        (
            f"py{python_version.major}{python_version.minor}"
            + (f"-{'-'.join(toxenv_factors[1:])}" if len(toxenv_factors) > 1 else ""),
            str(python_version),
        )
        for python_version in python_versions
    ]


if __name__ == "__main__":
    load_tox_targets()
