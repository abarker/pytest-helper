.. default-role:: code

pytest-helper
=============

The pytest-helper package allows modules, both inside and outside of packages,
to be self-testing when the module itself is executed as a script.  The test
functions that are run can be in the same module or they can be in a module in
a separate test directory.  Standalone testing modules can also be made
self-testing when they are executed.

Several utility functions are also provided to make it easier to
set up and run unit tests using the `pytest <http://pytest.org>`_
testing framework.  For example, there is a function to make modules
self-testing whenever they are executed as scripts, and a function to simplify
making modifications to the Python search path.

One of the useful features is that relative pathnames are always relative to
the directory of the file in which they occur (i.e., not relative to the CWD).

For examples and full documentation, see https://abarker.github.io/pytest-helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install is to install from PyPI using pip:

.. code-block:: bash

   pip install pytest-helper

