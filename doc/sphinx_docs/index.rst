.. pytest-helper documentation master file, created by
   sphinx-quickstart on Wed Jul 20 11:47:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. TODO
   .
   Consider what pytest will do with imports when it imports something from the
   middle of a package... that may not work with Python 3 style references.
   You are still calling pytest to run on the file and not importing the
   package...

===============================
pytest-helper
===============================

.. default-role:: code

The pytest-helper package provides several functions which make it easier to
set up and run unit tests in Python using the `pytest <http://pytest.org>`_
testing framework.  For example, there is a function to make files self-testing
whenever they are executed as scripts, and a function to simplify modifying the
search path.  One of the most useful features is that relative pathnames are
relative to the file in which they occur.  This package makes use of pytest but
is independent of the official pytest project.

Installation
============

The easiest way to install is to use `pip`, which works well with virtual
environments and allows for easy uninstallation.  Either download the zipped
directory from `the pytest-helper GitHub
<https://github.com/abarker/pytest-helper>`_ and unzip it, or else use `git` to
clone the GitHub repo.  Go to the root of the downloaded directory tree and run
this command:

.. code-block:: bash

   pip install .

Alternately, you can run the package's `setup.py` program directly with
`python setup.py install`.  Or, you can just add the `pytest_helper/src`
subdirectory to your `PYTHONPATH` environment variable.

.. _Introduction:

Introduction
============

Testing is an important part of software development, especially for a
dynamically typed language like Python.  The easier it is for people to set up
and run tests, the more likely they are to write their tests as they code
rather than waiting until later to do so (or perhaps not writing formal tests
at all).  This is especially true for beginners.

When developing a Python module it is nice to be able to quickly run some tests
specific to that module, without having to run all the tests for the full
package.  By using pytest-helper it is easy to make files self-testing whenever
they are run as scripts.  During development you can then just run the file,
say from your editor or IDE, to see the test results.

Below is a simple example to illustrate the idea.  This is a Python module
which is possibly part of a larger package.  It contains its own test functions
at the bottom.  Whenever the module is run as a script the tests will be run
with pytest; otherwise the module runs normally.  So as the module is being
written or modified the developer can execute the file and see the results of
the pytest tests for the module, as well as add tests to the file. ::

   import pytest_helper

   #
   # Run the tests, but only when the module is invoked as a script.
   #

   if __name__ == "__main__": # Guard conditional, optional but recommended.
       pytest_helper.script_run(self_test=True, pytest_args="-v")

   #
   # Regular imports and program code go here.
   #

   testing_var = "foo"

   #
   # Test functions are below; they can easily be moved to a separate module.
   #
   
   pytest_helper.autoimport()  # Do some basic imports automatically.

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

These are the main functions which simplify the invocation of pytest on a given
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
   `../test` and the parent directory to Python's `sys.path`::

      pytest_helper.sys_path("../test", add_parent=True)

   This line does the same thing as the line above::

      pytest_helper.sys_path(["..", "../test"])

* :ref:`pytest_helper.script_run<script_run>`

   The `script_run` function is used to actually invoke pytest on a test file or
   list of files.  It takes a path or a list of paths and, when called from a
   script, will run pytest on all those files.
   
   To include dotted Python package descriptors, use the `script_run` option
   `pyargs=True`.  Then if any of the names do not contain a slash
   (path-separator) character they are left unprocessed.  The `script_run`
   function will also set the pytest argument `--pyargs`.

   If `script_run` is not called from a script's `__main__` module then it
   returns without doing anything.  Any relative paths passed to the function
   are expanded relative to the directory of the module from which the
   `script_run` function is called.

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

   The example in the :ref:`Introduction` shows how to use `script_run` to run
   a self-test on a file.  The line below shows how the `script_run` function
   would be used to run pytest, with the `-v` verbose argument, on a test
   file named `test/test_foobar.py`::
   
      pytest_helper.script_run("test/test_foobar.py", pytest_args="-v")

   When the module that calls the above function is not run as a script the
   function call does nothing.

* :ref:`pytest_helper.init<init>`

   The `pytest_helper.init` function call is optional, but adds some
   functionality.  Perhaps the most useful added feature is the ability to use
   a configuration file.  See the section :ref:`Configuration` below.  This
   function should be called directly after importing `pytest_helper`::

      import pytest_helper
      pytest_helper.init()

   Using an early `init` call provides the additional benefit of making sure
   that the introspective lookup of the calling-module's path will continue to
   work even if some intervening command or module import changes the Python
   CWD (which is rare, but it happens).

See :ref:`help_running` for detailed documentation of these functions.

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
   test code.
   
   By default this function imports the `py.test` module as `pytest`.  From
   pytest-helper it imports `locals_to_globals`, and
   `clear_locals_from_globals`.  From pytest it imports `raises`, `fail`,
   `fixture`, `skip`, and `xskip`.

   This function is usually called without arguments::

      pytest_helper.autoimport()

   Note that some linters will complain about variables being used without
   being set.

See :ref:`help_writing` for detailed documentation of these functions.

.. _Examples:

Examples
========

Below are examples of using the pytest-helper functions in different cases.

Whenever `script_run` is called from a module to run tests it is best to call
it from the beginning of the file, especially for files inside packages which
do intra-package imports.  This placement is more efficient and avoids some
potential headaches with imports.  I like put the import and `script_run` call
directly after any `__future__` import and before all the others, but it really
just needs to be before any imports which use package-style imports (since the
module is being run as a script).

.. note::

   It is traditional to run tests from the end of a Python module, but
   `script_run` is calling another program (pytest) to extract and run the
   tests.  The test functions themselves can be placed anywhere, but it is not
   recommended to place a `script_run` call near the end of a module.  In many
   cases it works, but it can cause problems with explicit relative
   imports.  Some such problems can be fixed by importing `pytest_helper` near
   the top of the module and, before any explicit relative imports, calling its
   `init` function with the `set_package` flag set.  Putting the `script_run`
   call near the end of the module is also less efficient, since the module's
   initialization code gets run twice.

Whenever `script_run` is called in the examples below the optional `if __name__
== "__main__"` guard conditional is used.  It can be left off, but it is
slightly more efficient to use it since without it the module's name has to be
looked up by introspection to see if anything should be done.  Using the
conditional also makes the code more explicit in what it is doing.

* **Running tests contained in separate test files and test directories.**

   This is an example of a module with its tests in separate test files and
   directories.  When invoked as a script it the module will run all the tests
   in the subdirectory `test` and then run only the test file `test_var_set.py`
   in a sibling-level test directory called `test2`::

      # Run test files below, but only when the module is invoked as a script.
      # The guard conditional is optional, but slightly more efficient.
      if __name__ == "__main__":
         import pytest_helper
         pytest_helper.script_run(["test", "../test2/test_var_set.py"],
                                  pytest_args="-v")

      # Regular imports and program code from here to the end.

      testing_var = "foo"

* **Using pytest-helper inside a separate test file.**

   In this example there is a separate file, containing only tests, which when
   run as a script executes pytest on itself.  This file is assumed to be
   inside a test subdirectory, and to import the file `do_things.py` from its
   parent directory.  That directory is added to Python's `sys.path` by a call
   to `sys_path` (the test directory is not in the package of the parent
   directory, since it is usually not recommended to have an `__init__.py` file
   in test directories).  The test file below can still be run from other files
   with `script_run` or via the usual invocation of pytest from the command
   line. ::

      import pytest_helper

      if __name__ == "__main__":
          pytest_helper.script_run(self_test=True, pytest_args="-v")

      # Put these pytest_helper calls AFTER the script_run call.
      pytest_helper.autoimport()  # Do some basic imports automatically.
      pytest_helper.sys_path(add_parent=True)
      # pytest_helper.sys_path("..")  # Does the same thing as the line above.
      # pytest_helper.sys_path([".."])  # Does the same as the two lines above.

      from do_things import *  # Since we're testing this module, import all.

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
   (like in the first example, in the :ref:`Introduction`).  You would basically
   do the following:

   1. Copy the Python file to the test directory with a new name.

   2. Delete the code from one file and delete the tests from the other.  Both
      still need to import pytest-helper if they use any of the helper functions.

   3. Add an import statement in the test file to import what it needs from the
      code file.  If necessary, `sys_path` can be called in the test file so
      that it can find the module or package to be tested.

   4. Change the pathname on the `script_run` call in the code file to point to
      the new test file.  Add a self-testing `script_run` call to the test file,
      if desired.
       
.. _Configuration:

Configuration files
===================

Several of the pytest-helper functions have arguments which can be overridden
by values in a configuration file.  The file must be named `pytest_helper.ini`,
and each module separately searches for and parses a file with that name.
(Config files are loaded per-module since many different modules across
different packages may import and use the pytest-helper functions.)  The search
is conducted from the directory of the module up to the root directory, taking
the first such file encountered.  Caching is used to speed up the process.
Locating and using config files can be disabled altogether by passing the
argument `conf=False` to the `init` function::

   import pytest_helper
   init(conf=False)

Below is an example `pytest_helper.ini` configuration, which sets a value for
all the options which are settable from the config file.  These are only
examples, not the default options.  Any other sections of the file or other
options are silently ignored.  Most of the option names are constructed from
the name of the pytest-helper function concatenated with the name of the
parameter of the function which they override.

::

   [pytest_helper]

   # A comment.

   init_set_package = True

   script_run_pytest_args = "-v -s"

   sys_path_add_gn_parent = 2

   autoimport_noclobber = False
   autoimport_skip = ["pytest", "locals_to_globals"]
   autoimport_imports = [("pytest", py.test),
                         ("raises", py.test.raises),
                         ("fail", py.test.fail),
                         ("fixture", py.test.fixture),
                         ("skip", py.test.skip),
                         ("xfail", py.test.xfail),
                         ("locals_to_globals", locals_to_globals),
                         ("clear_locals_from_globals", clear_locals_from_globals)
                        ]


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

