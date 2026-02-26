# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click==8.2.1",
#     "peppyproject==1.0.2",
#     "requests==2.32.5",
#     "packaging==25.0",
# ]
# ///
import os
import warnings
from pathlib import Path

import click
import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from peppyproject import PyProjectConfiguration


@click.command()
@click.option("--package-source", default=None)
@click.option("--factors", default=None)
@click.option("--no-eoas", is_flag=True, default=False)
@click.option("--platforms", default=None)
def supported_python_envs_block(
    package_source: Path = None,
    factors: list[str] = None,
    no_eoas: bool = False,
    platforms: list[str] = None,
):
    """enumerate toxenvs for each Python version supported by package"""

    if platforms is None:
        platforms = ["linux"]
    elif isinstance(platforms, str):
        platforms = platforms.split(",")

    toxenvs = supported_python_toxenvs(package_source, factors, no_eoas)
    envs_block = "\\n".join(
        f"- {platform}: {toxenv}" for platform in platforms for toxenv in toxenvs
    )

    print(envs_block)
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"envs={envs_block}\n")


def supported_python_toxenvs(
    package_source: Path = None,
    factors: list[str] = None,
    no_eoas: bool = False,
) -> list[str]:
    if isinstance(factors, str):
        factors = factors.split(",")

    current_pythons = current_python_versions(no_eoas=no_eoas)

    if package_source is None or package_source == "":
        supported_pythons = current_pythons
    else:
        configuration = PyProjectConfiguration.from_directory(package_source)
        try:
            python_requirements = SpecifierSet(configuration["project"]["requires-python"])

            supported_pythons = [
                python for python in current_pythons if python in python_requirements
            ]
        except (KeyError, TypeError):
            warnings.warn(
                "could not find `requires-python` in metadata; falling back to current Python versions..."
            )
            supported_pythons = current_pythons

    return [
        f"py{str(python).replace('.', '')}{'-' + '-'.join(factors) if factors is not None and len(factors) > 0 else ''}"
        for python in supported_pythons
    ]


def current_python_versions(no_eoas: bool = False) -> list[Version]:
    url = "https://endoflife.date/api/v1/products/python"
    response = requests.get("https://endoflife.date/api/v1/products/python")
    if response.status_code == 200:
        return [
            Version(python["name"])
            for python in response.json()["result"]["releases"]
            if not python["isEoas" if no_eoas else "isEol"]
        ]
    else:
        raise ValueError(f"request to {url} returned status code {response.status_code}")


if __name__ == "__main__":
    supported_python_envs_block()
