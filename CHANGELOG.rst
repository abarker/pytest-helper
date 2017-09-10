.. :changelog:

History
=======

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

