#!/usr/bin/env python

"""

Test calling tests in a child directory.  This file is tested by a script
`test_in_child_dir.py` in the test directory.  No `__init__.py` in test
dir.

Call to script_run at bottom, but not recommended.

"""

from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper

# The line below is needed for the explicit relative import after it.
# The import fails without it.  This works, but the recommended alternative is do
# the script_run call at the top of the file, before the relative import.
pytest_helper.init()

# Below FAILS in the import from child dir; one possible fix is to import file as module.
# Better fix is to put script_run calls before such imports.
#from .dummy_module import test_string

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_child_dir"

##
## Run tests.
##

# Everything below can optionally be placed in an "if __name__ == '__main__'"
# conditional.  The call to script_run can optionally be placed near the top
# of the file, to avoid running the module initialization twice (for modules
# where that really matters).

if __name__ == "__main__":
    # Get this file's absolute dir path to test passing absolute pathnames in calls
    # to pytest_helper.
    this_files_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0)))
    path_to_second_test = os.path.join(this_files_dir, "test/test_second_in_child.py")

    # Use both relative and absolute pathnames in specifying the test file paths.
    # Also include the full directory in the list to check that that works.
    pytest_helper.script_run(testfile_paths=["test/test_in_child_dir.py",
                             path_to_second_test, "test"], pytest_args="-v", exit=False)

    # Try running as a package module.  Note it can start at package_subdir.
    # Doesn't need the path modification.
    #pytest_helper.sys_path("..")
    pytest_helper.script_run(testfile_paths="package_subdir.test_in_package_subdir",
                             pytest_args="-v", pyargs=True)


# Import works fine here; only called when imported.
from .dummy_module import test_string as dummy_test_string


