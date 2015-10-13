# -*- coding: utf-8 -*-
"""

Description
-----------

In order to run a module inside a package as a script and have relative imports
work, the `__package__` attribute of the module should be set.  Importing this
module sets the `__package__` attribute of the module `__main__`.  This module
is intended to be imported by modules which might be run as a script inside a
package which uses relative imports.

To use the module, just import it before any of the non-system files, inside
any module that you want to possibly run as a script.  Nothing else is
required.  This module needs to be imported before any relative imports or
modules which use relative imports.  Any existing `__package__` attributes will
remain unchanged.

Further details
---------------

On initial import this module searches for the module `__main__` in
`sys.modules`.  If that module is not found then the current runtime was not
started from a script and nothing is done.  If module `__main__` is found then
the current runtime was started from a script.  In that case the `__package__`
attribute for the `__main__` module is computed and set in that module's
namespace.  (If there already was a `__package__` attribute in the namespace
then nothing is done.)  The package is then imported under the full package
name and the module is also added to `sys.modules` under the full package name.

In order for a script to find this module to import it obviously must be saved
somewhere which is in (or is added to) the Python path.  One such place is
(usually) in the same directory as the script.  This package cannot be imported
via a relative import.

.. seealso:: 

    This module is based on the basic method described in the answers on this
    StackOverflow page: http://stackoverflow.com/questions/2943847/

.. note::

    As of 2007 Guido van Rossum viewed running scripts that are inside packages
    as an anti-pattern (see
    https://mail.python.org/pipermail/python-3000/2007-April/006793.html).
    Nevertheless, it can be a convenient and useful pattern in certain
    situations.  He did later approve PEP 366 which defined the `__package__`
    attribute to handle the situation.]

"""

from __future__ import print_function, division, absolute_import
import os
import sys

# Get the module named __main__ from sys.modules.
main_found = True
try:
    main_module = sys.modules["__main__"]
except KeyError:
    main_found = False

# Do nothing unless the program was started from a script.
if main_found and main_module.__package__ is None:

    importing_file = main_module.__file__
    dirname, filename = os.path.split(
                           os.path.realpath(os.path.abspath(importing_file)))
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

