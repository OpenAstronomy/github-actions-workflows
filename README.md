# github-actions-workflows

Reusable workflows for GitHub Actions.

- [Test a Python package using tox](#test-a-python-package-using-tox)
- [Build and publish a Python package](#build-and-publish-a-python-package)
- [Build and publish a pure Python package](#build-and-publish-a-pure-python-package)

## Test a Python package using tox

This workflow makes it easy to map tox environments to GitHub Actions jobs.
To use this template, your repository will need to have a `tox.ini` file.
[Read the workflow documentation.](https://github-actions-workflows.openastronomy.org/en/stable/tox.html)

```yaml
jobs:
  test:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/tox.yml@v1
    with:
      posargs: '-n 4'
      envs: |
        - linux: pep8
          pytest: false
        - macos: py310
        - windows: py39-docs
          libraries:
            choco:
              - graphviz
      coverage: 'codecov'
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Build and publish a Python package

Build, test and publish a Python source distribution and collection of platform-dependent wheels.
[Read the workflow documentation.](https://github-actions-workflows.openastronomy.org/en/stable/publish.html)

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish.yml@v1
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
      targets: |
        - linux
        - cp3?-macosx_x86_64
    secrets:
      pypi_token: ${{ secrets.pypi_token }}
```

## Build and publish a pure Python package

This the workflow is similar to the `publish.yml` workflow, except, instead of building wheels using cibuildwheel, a pure Python wheel and a source distribution are build, tested and published instead.
[Read the workflow documentation.](https://github-actions-workflows.openastronomy.org/en/stable/publish_pure_python.html)

```yaml
jobs:
  publish:
    uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
    with:
      test_extras: test
      test_command: pytest --pyargs test_package
    secrets:
      pypi_token: ${{ secrets.pypi_token }}
```
