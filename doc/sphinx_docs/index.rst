.. pytest-helper documentation master file, created by
   sphinx-quickstart on Wed Jul 20 11:47:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===============================
pytest-helper
===============================

.. default-role:: code

The pytest-helper package provides several functions which make it easier to
set up and run unit tests in Python using the `pytest <http://pytest.org>`_
testing framework.  For example, there is a function to make files self-testing
whenever they are executed as scripts, and a function to simplify modifying the
Python search path.  One of the most useful features is that relative pathnames
are relative to the file in which they occur.  This package makes use of pytest
but is independent of the official pytest project.

Two kinds of helper functions are provided.  The first kind are intended to
make it easier to run pytest on a test file or files, and the second kind are
meant to be used in writing tests, inside test files.  Some of the provided
helper functions are general-purpose, but several are specific to the `pytest
<http://pytest.org>`_ testing framework.  The functions are independent of each
other and can be used (or not used) as desired.  These functions are all
compatible with the ordinary uses and invocations of pytest.

.. _Introduction:

Introduction
============

Testing is an important part of software development, especially for a
dynamically-typed language like Python.  The easier it is for people to set up
and run tests, the more likely they are to write their tests as they code
rather than waiting until later to do so (or perhaps not writing formal tests
at all).

When developing a Python module it is nice to be able to quickly run some tests
specific to that module, without having to run all the tests for the full
package.  Using pytest-helper it is easy to make files self-testing whenever
they are run as scripts.  During development you can then just run the file,
say from your editor or IDE, to see the test results.

Below is a simple example to illustrate the idea.  This is a Python module
which is possibly part of a larger package.  It contains its own test functions
at the bottom.  Whenever the module is run as a script the tests will be run
with pytest; when the module is imported it runs normally.  So as the module is
being written or modified it can be executed to see the results of tests, and
new tests can be added as you go along.

.. code-block:: python

   import pytest_helper

   #
   # Run the tests, but only when the module is invoked as a script.
   #

   if __name__ == "__main__":  # Guard conditional, optional but recommended.
       pytest_helper.script_run(self_test=True, pytest_args="-v")

   #
   # Regular imports and program code go here.
   #

   code_var = "foo"

   #
   # Test functions are below; they can easily be moved to a separate module.
   #
   
   pytest_helper.autoimport()  # Do some basic imports automatically.

   def my_setup():  # Could be a pytest fixture instead of a regular function.
       setup_var = "bar"
       locals_to_globals()  # Copies setup_var to the module's global namespace.

   def test_var_values():
       my_setup()  # Run the setup code.
       assert code_var == "foo"  # Set in the regular code above.
       assert setup_var == "bar"    # Copied to the global namespace.
       test_dict = {}
       with raises(KeyError):  # Pytest function raises was autoimported.
           test_dict[5]
   
There are more examples in the :ref:`Examples` section below.  They include the
case where the tests to be run are in separate test files and the case of
making the separate test files themselves self-testing.  It is easy to move
tests originally written inside the module being tested to a separate test
file.

In order to simplify the functional interface, some of these helper functions
use very basic introspection look up the names of modules.  Other functions use
introspection to modify a module's global variables.  Some people might object
to the use of introspection "magic," but the level used by these functions is
less than what pytest itself does already.  Where introspection is used, a
fallback is usually provided to do the task without introspection.

Installation
============

The easiest way to install is to install from PyPI using pip:

.. code-block:: bash

   pip install pytest-helper

Alternately, you can download or clone the repository directory from `the
pytest-helper GitHub pages <https://github.com/abarker/pytest-helper>`_ and
then install using either `pip install .` or `python setup.py install` from the
root directory (pip is preferred).  In lieu of installing you can just add the
`pytest_helper/src` subdirectory to your `PYTHONPATH` environment variable.

Functions to help in running tests
==================================

These are short descriptions of the functions which simplify the invocation of
pytest on a given test file.  The links go to the more-detailed functional
interface descriptions.

* :ref:`pytest_helper.script_run<script_run>`

   The `script_run` function is used to actually invoke pytest on a test file or
   list of files.  It takes a path or a list of paths and, when called from a
   script, will run pytest on all those files.
   
   The `script_run` function is useful because it allows Python modules to be
   easily made self-testing when they are run as scripts.  When working on a
   module in, say, Vim you can invoke a command to run the current file as a
   script in order to verify that it still passes whatever tests are defined
   for it.  Those tests can be in the same file and/or in other files.  Test
   files themselves can similarly be made self-executing when run as a script,
   which can be useful when writing tests.

   One use of modules with self-contained tests, like in the example in the
   :ref:`Introduction`, is to quickly start writing a simple module while
   including a few tests.  As (or if) the module continues to evolve it is easy to
   extract those tests into a separate test module at some point.

   If `script_run` is not called from a script's `__main__` module then it
   returns without doing anything.  Any relative paths passed to the function
   are expanded relative to the directory of the module from which the
   `script_run` function is called.

   The example in the :ref:`Introduction` shows how to use `script_run` to run
   a self-test on a file.  The line below shows how the `script_run` function
   would be used to run pytest, with the `-v` verbose argument, on a test
   file named `test/test_foobar.py`::
   
      pytest_helper.script_run("test/test_foobar.py", pytest_args="-v")

   When the module that calls the above function is not run as a script the
   function call does nothing.

   If the pytest option `--pyargs` is used to include dotted Python package
   descriptors you should also use the `pyargs=True` option to `script_run`.
   Setting the pytest-helper argument automatically passes the argument to
   pytest.

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
   `../test` and the parent directory to Python's `sys.path`::

      pytest_helper.sys_path("../test", add_parent=True)

   This line does the same thing as the line above::

      pytest_helper.sys_path(["..", "../test"])

* :ref:`pytest_helper.init<init>`

   Calling the `pytest_helper.init` function is optional, but sometimes it is
   useful.  This function should be called directly after importing
   `pytest_helper`::

      import pytest_helper
      pytest_helper.init()

   The main benefit of using an early `init` call is to make sure that the
   introspective lookup of the calling-module's path continues to work even if
   some intervening command or module import changes the Python CWD (which is
   rare, but it happens).  This function can also be used to disable the use of
   configuration files (:ref:`see below<Configuration>`).

Functions to help in writing tests
==================================

These convenience functions are used to help in writing the tests themselves.
They are good for quickly setting up tests.  They can always be replaced by
their more-conventional (non-magic) equivalents.

* :ref:`pytest_helper.locals_to_globals<locals_to_globals>`

   The `locals_to_globals` function is intended to be run from a fixture (i.e.,
   from a test setup function) in the same module as the tests.  It mimics the
   effect of declaring all the local variables in the setup function global in
   order to access them from the test functions that use the setup.  By default
   it never overwrites an existing global variable unless that variable was set
   by a previous run of `locals_to_globals`.  Can optionally clear any
   variables set on previous calls so that they do not accidentally affect the
   current tests.

   This function is usually called without arguments, near the end of a setup
   function or fixture.  If `autoimport` is used then it is automatically
   imported into the module's global namespace.
   
   Note that some linters will complain about variables being used without
   being set.

* :ref:`pytest_helper.clear_locals_from_globals<clear_locals_from_globals>`

   The `clear_locals_from_globals` function is called by `locals_to_globals`
   when `clear` is set true.  This function can also be explicitly called to do
   the clearing.

* :ref:`pytest_helper.autoimport<autoimport>`

   The `autoimport` function is a convenience function that automatically
   imports certain pytest-helper and pytest functions into the calling module's
   global namespace.  The names can then be used essentially as builtins in the
   test code.  By default an exception is raised if the imports shadow any
   existing variables.
   
   This function imports the `pytest` module as `pytest`.  From pytest-helper
   it imports `locals_to_globals`, `clear_locals_from_globals`, and `unindent`.
   From pytest it imports `raises`, `fail`, `fixture`, `skip`, `xfail`, and
   `approx`.

   This function is usually called without arguments::

      pytest_helper.autoimport()

   Note that some linters will complain about variables being used without
   being set.

* :ref:`pytest_helper.unindent<unindent>`

   The `unindent` function allows for cleaner formatting of multi-line strings,
   for example to compare with in a pytest assertion.  The first argument,
   `unindent_level`, gives the number of characters to unindent.  The second
   argument is the string (typically a triple-quote string).  The string is
   split into lines, keeping all empty lines, and then the first and last line
   are discarded.  Each line is then unindented by the `unindent_level` argument
   number of characters and the lines are re-joined with newlines.  An exception
   is raised on trying to unindent non-whitespace on a line or if there are
   fewer than two lines.
 
   Here is a simple example usage, comparing a parse result with an expression
   tree of tokens in a multi-line string.  The ``unindent`` function is assumed
   to be called from inside a pytest testing function (already indented four
   spaces), and the parse result is assumed to start on the first column::
 
      assert result_tree.tree_repr() == unindent(12, """
              <k_plus,'+'>
                  <k_identifier,'x'>
                  <k_float,'0.22'>
              """)
 
.. _Examples:

Examples
========

The :ref:`Introduction` gives an example of a self-testing module, which
contains both the code to be tested as well as pytest test functions for that
code.  Below are some examples of using the pytest-helper functions in other
common cases.

Whenever `script_run` is called from a module to run tests it is best to call
it from the beginning of the file, especially for files inside packages which
do intra-package imports.  This placement is more efficient and avoids some
potential headaches with imports.  I like to put the import of pytest-helper
and the call to `script_run` directly after any `__future__` import and before
all the others, but it really just needs to be before any imports which use
intra-package imports (since the module is being run as a script when
`script_run` executes).

Whenever `script_run` is called in the examples below the optional `if __name__
== "__main__"` guard conditional is used.  It can be left off, but it is
slightly more efficient to use it since without it the module's name has to be
looked up by introspection to see if anything should be done.  Using the
conditional also makes the code more explicit in what it is doing.

* **Running tests contained in separate test files and test directories.**

   This is an example of a module with its tests in separate test files and
   directories.  When invoked as a script it the module will run all the tests
   in the subdirectory `test` and then run only the test file `test_var_set.py`
   in a sibling-level test directory called `test2`:

   .. code-block:: python

      #
      # Run the specified test files, but only when invoked as a script.
      #

      if __name__ == "__main__":
         import pytest_helper
         pytest_helper.script_run(["test", "../test2/test_var_set.py"],
                                  pytest_args="-v")

      #
      # Regular imports and program code from here to the end.
      #

      code_var = "foo"

* **Using pytest-helper inside a separate test file.**

   In this example there is a separate file, containing only tests, which when
   run as a script executes pytest on itself.  This file is assumed to be
   inside a test subdirectory, and imports the file `do_things.py` from its
   parent directory.  That directory is added to Python's `sys.path` by a call
   to `sys_path` (the test directory is not in the package of the parent
   directory, since it is usually not recommended to have an `__init__.py` file
   in test directories).  The test file below can still be run from other files
   with `script_run` or via the usual invocation of pytest from the command
   line.

   .. code-block:: python

      import pytest_helper

      #
      # Run the test file with pytest when invoked as a script.
      #

      if __name__ == "__main__":
          pytest_helper.script_run(self_test=True, pytest_args="-v")

      #
      # Put calls to these pytest_helper functions AFTER the script_run call.
      #

      pytest_helper.autoimport()  # Do some basic imports automatically.

      pytest_helper.sys_path(add_parent=True)
      # pytest_helper.sys_path("..")  # Does the same thing as the line above.
      # pytest_helper.sys_path([".."])  # Does the same as the two lines above.

      #
      # Test code below.
      #

      from do_things import *  # Since we're testing this module, import all.

      @fixture
      def my_fixture():
          fixture_var = "bar"
          locals_to_globals()  # Copies fixture_var to the module's global namespace.

      def test_var(my_fixture):
          assert code_var == "foo"  # Assumed to be set in do_things.py.
          assert fixture_var == "bar"  # Now in the module's global namespace.
          test_dict = {}
          with raises(KeyError): test_dict[5]  # The raises function was autoimported.
      
      def test_skipped():
          skip()  # The skip function was also autoimported.

Notice from these examples that very little needs to be changed in order to
extract a separate test module from the testing part of a module which
initially contains its own tests (like in the first example, in the
:ref:`Introduction`).  You would basically do the following:

1. Copy the Python file to the test directory with a new name.

2. Delete the code from one file and delete the tests from the other.  (Both
   still need to import pytest-helper if they use any of the helper functions.)

3. Add an import statement in the test file to import what it needs from the
   code file.  If necessary, `sys_path` can be called in the test file so
   that it can find the module or package to import.

4. Change the pathname on the `script_run` call in the code file to point to
   the new test file.  If desired, a self-testing `script_run` call can also be
   added to the test file.

.. note::

   It is traditional to run tests from the end of a Python module, but
   `script_run` is calling another program (pytest) to extract and run the
   tests.  The test functions themselves can be placed anywhere, but it is not
   recommended to place a `script_run` call near the end of a module.  In many
   cases it works, but it can cause problems with explicit relative imports.
   Some such problems can be fixed by running the script as module -- either
   with `python -m` or by importing `pytest_helper` near the top of the module
   and, before any explicit relative imports, calling its `init` function with
   the `set_package` flag set.  Running the script as a module may cause pytest
   to complain about modules being defined twice.  Putting the `script_run`
   call near the end of the module is also less efficient, since the module's
   initialization code gets run twice.

.. _Configuration:

Configuration files
===================

Several of the pytest-helper functions have arguments which can be overridden
by values in a configuration file.  The file must be named `pytest_helper.ini`,
and each module separately searches for and parses a file with that name
The files are cached by filename, so each one is only read once.
Config files are loaded per-module (since many different modules across
different packages may import and use the pytest-helper functions).

The search is conducted from the directory of the module up to the root
directory, taking the first such file encountered.  Locating and using config
files can be disabled altogether by passing the argument `conf=False` to the
`init` function::

   import pytest_helper
   init(conf=False)

Below is an example `pytest_helper.ini` configuration, which sets a value for
all the options which are currently settable from the config file.  These are
only examples, not the default options.  Any other sections of the file or
other options are silently ignored.  Most of the option names are constructed
from the name of the pytest-helper function concatenated with the name of the
parameter of the function which they override.

.. code-block:: ini

   [pytest_helper]

   # A comment.

   init_set_package = True

   script_run_pytest_args = "-v -s" # These override any pytest_args setting.
   script_run_extra_pytest_args = "-v -s" # Appended to pytest_args setting.

   autoimport_noclobber = False
   autoimport_skip = ["pytest", "locals_to_globals"]


Package contents
================

.. toctree::
   :maxdepth: 4

   pytest_helper

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

