# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import os
import sys

"""

In order to run modules inside packages as scripts and have relative imports
work, the `__package__` attribute of the module should be set.  This module is
intended to be imported by modules which are run as scripts inside a package
and which also might need to do relative imports.  

To use the module, just import it before any of the non-system files, inside
any module that you want to possibly run as a script.  Nothing else is
required.  Any existing `__package__` attributes will remain unchanged.

More details: If the program was not run from a script then nothing is done.
If the module actually was run as a script then `__main__` is key in
`sys.modules`.  In that case the `__package__` attribute for that module will
be set.  The module needs to be imported before any relative imports or modules
which use relative imports.  Note that successive imports will not re-run the
module initialization, it is only run once.

In order for a script to find this module to import, this module should either
1) be saved somewhere which is guaranteed to be in the Python path, or else 2)
a copy should be placed in the same directory as the script (which will usually
be found, except perhaps in interactive sessions).  To be completely sure the
script is found when it is in the same directory, even from interactive
sessions, you can put these lines before the import:

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

This module is based on the basic method described in the answers on this
StackOverflow page: http://stackoverflow.com/questions/2943847/

[Side note: As of 2007 Guido van Rossum viewed running scripts that are inside
packages as an anti-pattern:
    https://mail.python.org/pipermail/python-3000/2007-April/006793.html
Nevertheless, I find it to be a convenient and useful pattern in certain
situations.  GvR did later approve PEP 366, defining `__package__`.]

"""

# Get the module named __main__ from sys.modules.
main_found = True
try:
    main_module = sys.modules["__main__"]
except KeyError:
    main_found = False

# Do nothing unless the program was started from a script.
if main_found and main_module.__package__ is None:

    importing_file = main_module.__file__
    dirname, filename = os.path.split(os.path.abspath(importing_file))
    filename = os.path.splitext(filename)[0]
    parent_dirs = [] # A reverse list of package name parts to build up.

    # Go up the dirname tree to find the top-level package dirname.
    while os.path.exists(os.path.join(dirname, "__init__.py")):
        dirname, name = os.path.split(dirname) 
        parent_dirs.append(name)

    if parent_dirs: # Do nothing if no __init__.py file was found.

        # Get the package name and set the __package__ variable.
        full_package_name = ".".join(reversed(parent_dirs))
        main_module.__package__ = full_package_name

        # Now do the actual import of the full package.
        try:
            package_module = __import__(full_package_name)
        except ImportError:
            # Failure; insert dirname in sys.path, then try the import again.
            sys.path.insert(0, dirname)
            package_module = __import__(full_package_name)

        # Add the package's module to sys.modules.
        sys.modules[full_package_name] = package_module

