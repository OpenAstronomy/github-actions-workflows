Build and publish a pure Python package
---------------------------------------

This the workflow is similar to the ``publish.yml`` workflow, except,
instead of building wheels using cibuildwheel, a pure Python wheel and a
source distribution are build, tested and published instead.

.. code:: yaml

   jobs:
     publish:
       uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
       with:
         test_extras: test
         test_command: pytest --pyargs test_package
       secrets:
         pypi_token: ${{ secrets.pypi_token }}

Inputs
~~~~~~

runs-on
^^^^^^^

Choose an alternative image for the runner to use for building and
testing the source distribution and wheel. By default, this is
``ubuntu-latest``.

test_extras
^^^^^^^^^^^

Any ``extras_requires`` modifier that should be used to install the
package for testing. Default is none.

test_command
^^^^^^^^^^^^

The command to run to test the package. Will be run in a temporary
directory. Default is no testing.

env
^^^

A map of environment variables to be available when building and
testing. Default is none.

Due to `GitHub Actions
limitations <https://docs.github.com/en/actions/using-workflows/reusing-workflows#limitations>`__
this is the only way to pass environment variables from your workflow
file into the publishing job.

.. code:: yaml

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
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

python-version
^^^^^^^^^^^^^^

The version of Python used to test and build the package. By default,
this is ``3.x``.

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

   uses: OpenAstronomy/github-actions-workflows/.github/workflows/publish_pure_python.yml@v1
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

timeout-minutes
^^^^^^^^^^^^^^^

The maximum number of minutes to let the workflow run before GitHub
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
token should have the scope
```api:write`` <https://docs.anaconda.com/anaconda-repository/2.23/user/managing-account/#generating-tokens>`__
(allow write access to the API site).
