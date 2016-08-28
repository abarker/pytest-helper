.. default-role:: code

pytest-helper
=============

The pytest-helper package provides several functions which make it easier to
set up and run unit tests in Python using the `pytest <http://pytest.org>`_
testing framework.  For example, there is a function to make files self-testing
whenever they are executed as scripts, and a function to simplify modifying the
Python search path.  One of the most useful features is that relative pathnames
are relative to the file in which they occur.  This package makes use of pytest
but is independent of the official pytest project.

For examples and full documentation, see https://abarker.github.io/pytest-helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install is to install from PyPI using pip:

.. code-block:: bash

   pip install pytest-helper

