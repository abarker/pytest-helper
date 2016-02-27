.. pytest_helper documentation master file, created by
   sphinx-quickstart on Sat Oct  3 12:36:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===============================
pytest-helper
===============================

.. default-role:: code

This package provides several functions which make it easier to set up and run
unit tests in Python using the `pytest <http://pytest.org>`_ testing framework.
It makes use of pytest but is not part of the official pytest project.

Installation
============

The easiest way to install is to use ``pip``, which also allows for easy
uninstallation.  Either download the zipped directory from GitHub and unzip it,
or else use `git` to clone the GitHub repo.  Then run:

.. code-block:: bash

   pip install file:///path/to/the/new/pytest_helper/dir

replacing the path with the one where you saved the directory.  (Run the
command with ``sudo`` or equivalent administrator privileges if installing as
a system Python package rather than as a local one.)

Alternately, you can run the package's ``setup.py`` program directly with
``python setup.py install``.  Or, you can just add the ``pytest_helper``
subdirectory to your ``PYTHONPATH`` environment variable.

.. _Introduction:

Introduction
============

Testing is an important part of software development, especially for a
dynamically typed language like Python.  The easier it is for people to set up
and run tests, the more likely they are to write their tests as they code
rather than waiting until later to do so (or perhaps not writing formal tests
at all).  This is especially true for beginners.

Below is a simple example to illustrate the idea.  This is a Python module
which is possibly part of a larger package.  It contains its own test functions
at the bottom.  Whenever the module is run as a script the tests will be run
with pytest; otherwise the module runs normally.  So as the module is being
written or modified the developer can execute the file and see the results of
the pytest tests for the module, as well as add tests to the file. ::

   import pytest_helper

   # Regular program code goes here.

   testing_var = "foo"

   # Run the tests, but only when the module is invoked as a script.

   if __name__ == "__main__":  # This guard conditional is optional.

       pytest_helper.script_run(self_test=True, pytest_args="-v")

   # Test functions are below; these can easily be moved to a separate module.
   
   pytest_helper.auto_import()  # Do some basic imports automatically.

   def my_setup(): # Could be a pytest fixture instead of a regular function.
       setup_var = "bar"
       locals_to_globals()  # Copies setup_var to the module's global namespace.

   def test_var_values():
       my_setup()  # Run the setup code.
       assert testing_var == "foo"  # Set in the regular code above.
       assert setup_var == "bar"    # Now in the global namespace.
       test_dict = {}
       with raises(KeyError):  # Pytest function raises was autoimported.
           test_dict[5]
   
There are more examples in the :ref:`Examples` section below, including the
case where tests to be run are in separate files and the case of a test file
itself, located in a separate test directory.  It is easy to move tests
originally written inside the module being tested to a separate test file.

Some of the provided helper functions are general-purpose, but several are
specific to the `pytest <http://pytest.org>`_ testing framework.  The functions
are independent of each other and can be used (or not used) as desired.  These
functions are compatible with the ordinary uses and invocations of pytest.

In order to simplify the functional interface, some of these helper functions
use very basic introspection look up the names of modules.  Others use
introspection to modify a module's global variables.  Some people might object
to the use of introspection "magic," but the level used by these functions is
far less than what pytest itself does already.  Where introspection is used, a
fallback is usually provided to do the task without introspection.

Two kinds of helper functions are provided.  The first kind are intended to
make it easier to run pytest on a test file or files, and the second kind are
meant to be used in writing tests inside test files.  The functions are briefly
described in the sections below.

Functions to help in running tests
==================================

These are the main functions which simplify the invocation pytest on a given
test file.

* :ref:`pytest_helper.sys_path<sys_path>`

   The function `sys_path` takes a directory path or a list of paths and
   inserts them into Python's `sys.path` list.  This is often necessary in
   order for Python to find the imports in test files.  A benefit of using this
   function is that relative paths are allowed, and all relative paths are
   expanded relative to the directory of the module which calls the function.
   This is in contrast to the default evaluation of relative paths in Python,
   which is relative to Python's current working directory (CWD).  The CWD can
   vary depending on the particular command used to invoke the Python
   interpreter.  Using relative imports within a project's directory structure
   makes it more portable.

   The line below shows how to use `sys_path` to add both the directory
   ``../test`` and the parent directory to Python's ``sys.path``::

      pytest_helper.sys_path("../test", add_parent=True)

   This line does the same thing as the line above::

      pytest_helper.sys_path(["..", "../test"])

* :ref:`pytest_helper.script_run<script_run>`

   The `script_run` function is used to actually invoke pytest on a test file or
   list of files.  It takes a path or list of paths and, when called from a
   script, will run pytest on all those files.  If it is not called from a
   script's `__main__` module then it returns without doing anything.  Any
   relative paths passed to the function are expanded relative to the directory of
   the module from which the `script_run` function is called.

   The `script_run` function is useful because it allows Python modules to be
   easily made self-testing when they are run as scripts.  When working on a
   module in, say, Vim you can invoke a command to run the current file as a
   script in order to see if it still passes whatever tests are defined for it.
   Those tests can be in the same file and/or in other files.  Test files
   themselves can similarly be made self-executing when run as a script, which can
   be useful when writing tests.

   One use of modules with self-contained tests, like in the example in the
   :ref:`Introduction`, is to quickly start writing a simple module while
   including a few tests.  As (or if) the module continues to evolve it is easy to
   extract those tests into a separate test module at some point.

   The example in the :ref:`Introduction` shows how to use `script_run` to run
   a self-test on a file.  The line below shows how the `script_run` function
   would be used to run pytest, with the ``-v`` verbose argument, on a test
   file named ``test/test_foobar.py``::
   
      pytest_helper.script_run("test/test_foobar.py", pytest_args="-v")

   When the module that calls the above function is not run as a script the
   function call does nothing.

* :ref:`pytest_helper.init<init>`

   The `pytest_helper.init` function call is optional, but adds some
   functionality.  Perhaps the most useful added feature is the ability to use a
   configuration file.  See the section :ref:`Configuration` below.  This
   function should be called directly after importing `pytest_helper`::

      import pytest_helper
      pytest_helper.init()

   Using an early `init` call provides the additional benefit of making sure
   that the introspective lookup of the calling-module's path will continue to
   work even if some intervening command or module import changes the Python
   CWD (which is rare, but it happens).

* :ref:`set_package_attribute<set_package_attribute>`

   The pytest-helper package provides a module called `set_package_attribute`.
   Simply importing this module before any relative imports allows those
   relative imports to continue working when the module is invoked as a script.
   (This is done by setting the `__package__` attribute for `__main__`, but
   requires some other steps, too.)  So to use the module, you would make this
   import before any relative imports::

      import set_package_attribute

   An alternate way to do the same thing is to call the optional pytest-helper
   initialization function just after importing `pytest_helper`, as described
   above, using the keyword argument `set_package=True`.

See :ref:`help_running` for detailed documentation of these functions.

Functions to help in writing tests
==================================

These functions are used to help in writing the tests themselves.

* :ref:`pytest_helper.auto_import<auto_import>`

   The `auto_import` function is a convenience function that automatically imports
   certain pytest-helper and pytest functions into the calling module's global
   namespace.  The names can then be used like builtins in the test code.
   
   By default this function imports the `py.test` module as `pytest`.  From
   pytest-helper it imports `locals_to_globals`, and
   `clear_locals_from_globals`.  From pytest it imports `raises`, `fail`,
   `fixture`, `skip`, and `xskip`.

   This function is usually called without arguments::

      pytest_helper.auto_import()

* :ref:`pytest_helper.locals_to_globals<locals_to_globals>`

   The `locals_to_globals` function is intended to be run from a fixture (i.e.,
   from a test setup function) in the same module as the tests.  It mimics the
   effect of declaring all the local variables in the setup function global in
   order to access them from the test functions that use the setup.  By default
   it never overwrites an existing global variable unless that variable was set
   by a previous run of `locals_to_globals`.  It also clears any variables set
   on its previous call so they do not accidentally affect the current tests.

   This function is usually called without arguments, near the end of a setup
   function or fixture.  If `auto_import` is used then it is automatically
   imported into the module's global namespace.

* :ref:`pytest_helper.clear_locals_from_globals<clear_locals_from_globals>`

   By default the `clear_locals_from_globals` function is always called by
   `locals_to_globals` in order to clear any previously-set globals.  This
   function can also be explicitly called to do the clearing, such as when
   `locals_to_globals` is run with `auto_clear` set false.

See :ref:`help_writing` for detailed documentation of these functions.

.. _Examples:

Examples
========

Below are examples of using the pytest-helper functions in different cases.
Note that when `script_run` is called from a regular module (one which contains
code which is being tested) it is invoked near the end of the file.  This is
only because it is traditional and convenient to put testing code near the end.
It is actually more efficient to put calls to `script_run` near the beginning
of such a module, since otherwise the module's initialization code is run
twice.  This is usually insignificant in interactive user-testing scenarios,
but for some modules (such as modules with a long setup time) it can make a
difference.

Whenever `script_run` is called in the examples below the optional `if __name__
== "__main__"` guard conditional is not used.  This is slightly less efficient
(including in ordinary code runs) since the module's name then has to be looked
up by introspection to see if anything should be done.  The guard conditional
can always be explicitly used around calls to `script_run`.

* **Running tests in separate test files and test directories.**

   This example is a module with tests in separate test files and directories.
   When invoked as a script it runs all the tests in the subdirectory ``test`` and
   then runs only the test file ``test_var_set.py`` in a sibling-level test
   directory called ``test2``::

      # Regular program code goes here.

      testing_var = "foo"

      # Run test files below, but only when the module is invoked as a script.
      # The guard conditional is optional, but slightly more efficient.

      if __name__ == "__main__":
         import pytest_helper
         pytest_helper.script_run(["test", "../test2/test_var_set.py"],
                                  pytest_args="-v")


* **Using pytest-helper inside a separate test file.**

   The next example is separate tests-only file, which when run as a script
   executes pytest on itself.  This file is assumed to be inside a test
   subdirectory, and to import the file ``do_things.py`` from its parent
   directory.  That directory is added to Python's `sys.path` by a call to
   `sys_path` (the test directory is not in the package of the parent directory,
   since it is usually not recommended to have an ``__init__.py`` file in test
   directories).  The test file below can still be run from other files with
   `script_run` or via the usual invocation of pytest from the command line. ::

      import pytest_helper

      pytest_helper.script_run(self_test=True, pytest_args="-v")
      pytest_helper.auto_import()  # Do some basic imports automatically.
      pytest_helper.sys_path(add_parent=True)
      # pytest_helper.sys_path("..")  # Does the same thing as the line above.
      # pytest_helper.sys_path([".."])  # Does the same as the two lines above.

      from do_things import *  # Since we're testing that module, import all.

      @fixture
      def my_fixture():
          fixture_var = "bar"
          locals_to_globals()  # Copies fixture_var to the module's global namespace.

      def test_var(my_fixture):
          assert testing_var == "foo"  # Assumed to be set in do_things.py.
          assert fixture_var == "bar"  # Now in the module's global namespace.
          test_dict = {}
          with raises(KeyError): test_dict[5]  # The raises function was autoimported.
      
      def test_skipped():
          skip()  # The skip function was also autoimported.

Notice that very little needs to be changed in order to extract a separate test
module from the testing part of a module which initially contains its own tests
(like in the first example, in the :ref:`Introduction`).  A `sys_path` function
call would be added so the new test file can import the file to be tested, and
then the actual import of the code is done.  If desired, the call to
`script_run` in the original module can be modified to run pytest on the new
test file when the original module is invoked as a script, as in the earlier
example.  Just remove the `self_test` option and pass `script_run` the new
pathname.

.. _Configuration:

Configuration files
===================

The use of `init` is required.

Module contents
===============

.. toctree::
   :maxdepth: 4

   pytest_helper
   set_package_attribute

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

