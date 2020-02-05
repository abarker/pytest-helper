.. :changelog:

History
=======

0.2.3 (2019-??-??)
------------------

New features:

* Added an option ``ignore_params`` to ``locals_to_globals``.  Setting it false
  (default is true) causes the function's parameters to be copied to globals
  along with the rest of its locals.  Also, keyword arguments are now included
  as parameters (to be ignored or not).

* Try to workaround cases where no `__file__` attribute is present on `__main__`.
  Works in vim pymode for self-tests, at least.

0.2.2 (2019-05-30)
------------------

New features:

* Added a new option ``pskip`` to ``script_run`` which is the same as ``skip`` but
  it first calls ``set_package_attribute`` to cause the script to run as a package.
  Useful normally-running a script inside a package.

Changes:

* Removed the ``set_package`` options to ``script_run`` and ``init`` because they
  did not interact well with pytest.  It handles package initialization itself.

0.2.1 (2019-05-27)
------------------

New features:

* Now pytest > 3.1 version is required.
 
* The new ``modify_syspath`` argument is passed to the ``init`` of
  ``set_package_attribute`` if it is called to implement ``set_package``.
  The defaults for ``modify_syspath`` in both ``script_run`` and 
  ``init`` are now to apply it when run from inside a package, but not
  otherwise.

* The ``sys_path`` function now takes an argument ``insert_position`` that
  determines where in ``sys.path`` the paths are inserted.

* If ``modify_syspath`` was chosen and ``exit=False`` the system path is no
  longer automatically restored after the exit.

0.2.0 (2017-10-11)
------------------

New features:

* Added the ``unindent`` function for unindenting multi-line strings.  The
  function is also made a default import for ``autoimport``.

* The ``approx`` function of pytest is now autoimported by default.

* The ``script-run`` function now passes all the test files to a single run of
  pytest by default.  For the old behavior of looping over them separately use
  ``single_run=False``.

* New keyword option ``skip`` to temporarily turn off ``script_run``.

Bug fixes:

* Fixed handling of arguments to command-line arguments passed to
  ``script_run`` as a string.

0.1.1 (2016-07-11)
------------------

New Features: None.

Bug Fixes:

* Fixed a bug in handling default ``pytest_args`` to ``script_run``.
  
* Cleaned up imports in test cases.

Other Changes:

* Converted to pass lists to `pytest.main` since passing strings is now
  deprecated.

* Edited documentation.

0.1.0 (2016-06-11)
------------------

Initial release.

