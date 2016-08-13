#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper
#pytest_helper.init(set_package=True)
#pytest_helper.sys_path("..")
#import package_dir

# TODO
#from . import dummy_module # Fails!!!!!!!!!!!!!!!

"""

TODO: to fix above, may need to have a special "pyargs" argument.  It helps to
run script at top, too, since otherwise you need the set_package_attribute.
Basically, find the package root (like during setup file discovery), and then
add it to sys.path, and then the "pyargs" arguments do not get made into full
pathnames, they are kept the same.  Could also have options that automatically
build the package name for self-run tests on modules inside a package.
Similarly, you could have an option to do that for modules in current or
relative directories.

For --pyargs option, see:
   http://pytest.org/latest/example/pythoncollection.html#interpreting-cmdline-arguments-as-python-packages
    ...will check if NAME exists as an importable package/module and otherwise
    treat it as a filesystem path.
You can also permanently turn it on with pytest config file.

See also this page, talking about inlined tests and using __init__.py or not.
   http://pytest.org/latest/goodpractices.html
See the second note box, in particular, about how pytest discovers packages and
adds to sys.path.

Here's a possible rule: in script_run, look at all the testfile strings.  If it
1) has no slashes, and 2) does not end in .py, then assume it is a package name
and leave it unchanged and automatically add the --pyargs to the call string.
Still need to add to path by hand... except if it is inside the current package
you could probably tell from directory scan.

There are several ways to test if a module exists without actually importing it:
    http://stackoverflow.com/questions/14050281/how-to-check-if-a-python-module-exists-without-importing-it
Or you could just add it to sys.path if on the path up to package container dir.

"""

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_same_dir"

##
## Run tests.
##

# Everything below can optionally be placed in an "if __name__ == '__main__'"
# conditional.  The call to script_run can optionally be placed near the top
# of the file, to avoid running the module initialization twice (for modules
# where that really matters).

# Use both relative and absolute pathnames in specifying the test file paths.
# Also include the full directory in the list to check that that works.
pytest_helper.script_run("test_in_same_dir.py", pytest_args="-v --pyargs")

