Developer Guide
$$$$$$$$$$$$$$$

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - f174b0cdec6b482daa2878c8cc0d02c3

This section contains everything that a StrictDoc developer/contributor should
know to get the job done.

StrictDoc is based on Python and maintained as any other Python package on
GitHub: with linting, tests, and hopefully enough best practice put into the
codebase.

The instructions and conventions described below are a summary of what is
considered to be the currently preferred development style for StrictDoc.

Any feedback on this development guide is appreciated.

.. _DEVGUIDE_GETTING_STARTED:

Getting started
===============

System dependencies
-------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - df2e1de12c6b456898c48a36650813d4

StrictDoc itself mostly depends on other Python Pip packages, so there is nothing special to be installed.

You may need to install ``libtidy`` if you want to run the integration tests. The HTML markup validation tests depend on libtidy.

On Linux Ubuntu:

.. code:: bash

    sudo apt install tidy

From the core Python packages, StrictDoc needs Invoke, Tox and TOML:

.. code:: bash

    pip install invoke tox toml

Windows-specific: Long Path support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 8591cf6dece04244824c3ac2a8666ba3

As `reported <https://github.com/strictdoc-project/strictdoc/issues/1118>`_ by a user, Windows Long Path support has to be enabled on a Windows system.

You can find information on how to enable the long paths support at https://pip.pypa.io/warnings/enable-long-paths.

Installing StrictDoc from GitHub (developer mode)
-------------------------------------------------

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 2407bb186b274a58b97b54b99ba6e86f

**Note:** Use this way of installing StrictDoc only if you want to make changes
in StrictDoc's source code. Otherwise, install StrictDoc as a normal Pip package by running ``pip install strictdoc``.

.. code-block::

    git clone https://github.com/strictdoc-project/strictdoc.git && cd strictdoc
    python developer/pip_install_strictdoc_deps.py
    python3 strictdoc/cli/main.py

The ``pip_install_strictdoc_deps.py`` installs all dependencies of StrictDoc, but not StrictDoc itself.

Invoke for development tasks
============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 452b3c24463446a497ed6b8fcdb31fef

All development tasks are managed using
`Invoke <https://www.pyinvoke.org/>`_ in the ``tasks.py`` file. On macOS and
Linux, all tasks run in dedicated virtual environments. On Windows, invoke uses
the parent pip environment, which can be a system environment or a user's virtual
environment.

Make sure to familiarize yourself with the available developer tasks by running:

.. code-block:: bash

    invoke --list

Main "Check" task
=================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 09258e99cabb4455904b0e2c6687d492

Before doing anything else, run the main ``check`` command to make sure that StrictDoc passes all tests on your system:

.. code:: bash

    invoke check

The ``check`` command runs all StrictDoc lint and test tasks with the only exception of end-to-end Web tests that are run with a separate task (see below).

.. _DEVGUIDE_PYTHON_CODE:

Python code
===========

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 3012a69ef5d244d49fcb90c088d4523b

- The version of Python is set to be as low as possible given some constraints
  of StrictDoc's dependencies. Ideally, the lowest Python version should only be
  raised when it is consistently deprecated by major software platforms like
  Ubuntu or GitHub Actions.

- All developer tasks are collected in the ``tasks.py`` which is run by Invoke tool. Run the ``invoke --list`` command to see the list of available commands.

- Formatting is governed by ``black`` which reformats the code automatically
  when the ``invoke check`` command is run.

  - If a string literal gets too long, it should be split into a multiline
    literal with each line being a meaningful word or a subsentence.

- Avoid shortening variable names unnecessarily. For example, use 'buffer' instead of 'buf', 'document' instead of 'doc', 'function' instead of 'func', 'length' instead of 'len', etc. Note: While some older parts of StrictDoc may not adhere to this guideline, they are planned to be refactored in the future.

- For "element is non-None" checks, a full form shall be used, for example: ``if foo is not None`` instead of ``if foo``. This helps to avoid any confusion with all sorts of strings (empty or non-empty ``str``, ``Optional[str]``) that are used extensively in StrictDoc's codebase. The non-None and non-empty string check shall therefore be as follows: ``if foo is not None and len(foo) > 0``. The explicit check also applies to any other kinds of objects besides strings: ``if foo is not None`` instead of ``if foo``. Rationale: ``if foo`` makes it unclear whether the intention is to check ``is not None`` or also ``len(foo) > 0``.

- For lambdas and short for loops, the recent convention is to add ``_`` to the variables of a for loop or a lambda to visually highlight their temporary use within the current scope which is done to counter the fact that these variables can leak and be used outside of the scope of the loop. Example:

.. code-block:: python

    for a_, b_ in foo:
        # use a_, b_ within the loop.

- The function arguments with the default values shall be avoided. This convention improves the visibility of the function interfaces at the coast of increased verbosity which is the price that StrictDoc development is willing to pay, maintaining the software long-term. The all-explicit function parameters indication is especially useful when the large code refactorings are made.

- StrictDoc has been making a gradual shift towards a stronger type system. Although type annotations haven't been added everywhere in the codebase, it is preferred to include them for all new code that is written.

- If a contribution includes changes in StrictDoc's code, at least the
  integration-level tests should be added to the ``tests/integration``. If the
  contributed code needs a fine-grained control over the added behavior, adding
  both unit and integration tests is preferred. The only exception where a
  contribution can contain no tests is "code climate" which is work which
  introduces changes in code but no change to the functionality.

.. _DEVGUIDE_GIT_WORKFLOW:

Git workflow
============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 0e916453596b460b84a89f722354a825

- The preferred Git workflow is "1 commit per 1 PR". If the work truly deserves
  a sequence of commits, each commit shall be self-contained and pass all checks
  from the ``invoke check`` command. The preferred approach: split the work into
  several independent Pull Requests to simplify the work of the reviewer.

- The branch should be always rebased against the main branch. The
  ``git fetch && git rebase origin/main`` is preferred over
  ``git fetch && git merge main``.

- The Git commit message should follow the format:

.. code-block::

    context: description

where the context can be a major feature being added or a folder. A form of  ``context: subcontext: description`` is also an option. Typical examples:

``docs: fix links to the grammar.py``

``reqif: native: export/import roundtrip for multiline requirement fields``

``backend/dsl: switch to dynamic fields, with validation``

``Poetry: add filecheck as a dependency``

- Use comma-separated contexts, if the committed work is dedicated to more than one topic. Example:

.. code-block::

    server, UI: update to new requirement styles

- When a contribution is simply an improvement of existing code without a change
  in the functionality, the commit should be named: ``Code climate: description``. Example:

.. code-block::

    Code climate: fix all remaining major Pylint warnings

Frontend development
====================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - d818aad87db54985b8933f98528808ab

The shortest path to run the server when the StrictDoc's source code is cloned:

.. code-block:: bash

    invoke server

Running End-to-End Web tests
============================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - da3cbcd69b0545988daeb0f42098830d

.. code:: bash

    invoke test-end2end

Running integration tests
=========================

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 4e307b3b950840bbbe455c1ae3238a6e

The integration tests are run using Invoke:

.. code-block:: bash

    invoke test-integration

The ``--focus`` parameter can be used to run only selected tests that match a given substring. This helps to avoid running all tests all the time.

.. code-block:: bash

    invoke test-integration --focus <keyword>

See `How to test command-line programs with Python tools: LIT and FileCheck <https://stanislaw.github.io/2020-11-20-how-to-test-command-line-programs-with-python.html>`_ to learn more about LIT and FileCheck, which enable the StrictDoc integration tests.

Documentation
=============

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - d1f5fde86ebc4103bc4eb0334b1ec919

- Every change in the functionality or the infrastructure should be documented.
- Every line of documentation shall be no longer than 80 characters. StrictDoc's
  own documentation has a few exceptions, however, the latest preference is
  given to 80 characters per line. Unfortunately, until there is automatic
  support for mixed SDoc/RST content, all long lines shall be edited and
  split by a contributor manually.
- The ``invoke docs`` task should be used for re-generating documentation on a
  developer machine.

Conventions
===========

.. list-table::
    :align: left
    :header-rows: 0

    * - **MID:**
      - 49b7349a3bee478cbe81d8ef25f6245c

- ``snake_case`` everywhere, no ``kebab-case``.

  - This rule applies everywhere where applicable: file and folder names, HTML attributes.
  - Exception: HTML data-attributes and ``testid`` identifiers.
