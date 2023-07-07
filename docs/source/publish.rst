Build and publish a Python package
----------------------------------

Build, test and publish a Python source distribution and collection of
platform-dependent wheels.

.. code:: yaml

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

Inputs
~~~~~~

targets
^^^^^^^

List of build targets for cibuildwheel. The list of targets must be
specified as demonstrated by the default value below. Each target is
built within a separate matrix job.

If the target is ``linux``, ``macos`` or ``windows``, cibuildwheel is
run on the latest version of that OS.

Any other target is assumed to be a value for the ``CIBW_BUILD``
environment variable (e.g. ``cp3?-macosx_x86_64``). In this case the OS
to run cibuildwheel on is extracted from the target.

Targets that end with ``aarch64``, ``arm64`` and ``universal2`` are also
supported without any additional configuration of cibuildwheel.

**Note:** ``targets`` is a *string* and must be specified as a
literal block scalar using the ``|``. (Without the ``|``, it must also
be valid YAML.)

Default is:

.. code:: yaml

   targets: |
     - linux
     - macos
     - windows

To not build any wheels:

.. code:: yaml

   targets: ''

sdist
^^^^^

Whether to build a source distribution. Default is ``true``.

sdist-runs-on
^^^^^^^^^^^^^

Choose an alternative image for the runner to use for building and
testing the source distribution. By default, this is ``ubuntu-latest``.

test_extras
^^^^^^^^^^^

Any ``extras_requires`` modifier that should be used to install the
package for testing. Default is none.
If not set, cibuildwheel will use any ``test-extras`` configured in ``pyproject.toml``.

test_command
^^^^^^^^^^^^

The command to run to test the package. Will be run in a temporary
directory. Default is no testing.
If not set, cibuildwheel will use any ``test-command`` configured in ``pyproject.toml``.

If you need quotes in the command, please use single quotes, not double quotes.

env
^^^

A map of environment variables to be available when building and
testing. Default is none.

Due to `GitHub Actions
limitations <https://docs.github.com/en/actions/using-workflows/reusing-workflows#limitations>`__
this is the only way to pass environment variables from your workflow
file into the publishing job.

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish.yml@v1
   with:
     env: |
       VAR1: test
       VAR2: |
         first line
         seconds line
       VAR3: testing

libraries
^^^^^^^^^

Packages needed to build the source distribution for testing. Must be a
string of space-separated apt packages. Default is install nothing
extra.

upload_to_pypi
^^^^^^^^^^^^^^

Whether to upload to PyPI after successful builds. The default is to
upload to PyPI when tags that start with ``v`` are pushed. A boolean can
be passed as ``true`` (always upload) or ``false`` (never upload) either
explicitly or as a boolean expression (``${{ <expression> }}``).

Alternatively, a string can be passed to match the start of a tag ref.
For example, ``'refs/tags/v'`` (default) will upload tags that begin
with ``v``, and ``'refs/tags/'`` will upload on all pushed tags.

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish.yml@v1
   with:
     upload_to_pypi: refs/tags/

repository_url
^^^^^^^^^^^^^^

The PyPI repository URL to use. Default is the main PyPI repository.

upload_to_anaconda
^^^^^^^^^^^^^^^^^^

Whether to upload to Anaconda.org after successful builds. The default
is to not upload. A boolean can be passed as ``true`` (always upload) or
``false`` (never upload) either explicitly or as a boolean expression
(``${{ <expression> }}``).

anaconda_user
^^^^^^^^^^^^^

Anaconda.org user or organisation. Required if ``upload_to_anaconda`` is
true.

anaconda_package
^^^^^^^^^^^^^^^^

Anaconda.org package. Required if ``upload_to_anaconda`` is true.

anaconda_keep_n_latest
^^^^^^^^^^^^^^^^^^^^^^

If specified, keep only this number of versions (starting from the most
recent) and remove older versions. This can be useful to prevent a
build-up of too many files when uploading developer versions.

fail-fast
^^^^^^^^^

Whether to cancel all in-progress jobs if any job fails. Default is
``false``.

timeout-minutes
^^^^^^^^^^^^^^^

The maximum number of minutes to let a build job run before GitHub
automatically cancels it. Default is ``360``.

submodules
^^^^^^^^^^

Whether to checkout submodules. Default is ``true``.

Secrets
~~~~~~~

pypi_token
^^^^^^^^^^

The authentication token to access the PyPI repository.

anaconda_token
^^^^^^^^^^^^^^

The authentication token to access the Anaconda.org repository. This
token should have the scope ``api:write`` (allow write access to the API site).
