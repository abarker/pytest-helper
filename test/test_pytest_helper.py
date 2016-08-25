# -*- coding: utf-8 -*-
"""

These are tests of `locals_to_globals` and older tests of the techniques used
in pytest helper.  There are also a couple of early experimental approaches.
Mostly stuff related to locals_to_globals and alternatives.

"""

from __future__ import print_function, division, absolute_import
import sys

import pytest_helper
pytest_helper.script_run(self_test=True)
pytest_helper.autoimport()

#from py.test import raises, fail, fixture, skip  # Done by autoimport.

def dummy_fun(): pass # just to test function objects

@fixture
def set_up_test_copy_to_globals(request):
    """ """
    xx = 100
    x_str = "string in setup"
    monkey = 900
    df = dummy_fun

    locals_to_globals()
    def finalize():
        clear_locals_from_globals() # works but no clear is easier
    request.addfinalizer(finalize)

def test_copy_locals_to_globals(set_up_test_copy_to_globals):
    """In this method, all locals of the setup function are made global at the
    end of the setup function.  The test module can then access them.  It
    cannot modify them in the external scope, but it can assign to local
    variables with the same name AS LONG AS IT HAS NOT REFERENCED IT because
    when it references it first it assumes it is in module scope.  You can
    give it a global declaration somewhere before you assign to it if you need
    to modify it; that works."""
    test_var = 99
    print("locals in test() are: ", locals())
    assert xx == 100
    assert df is dummy_fun
    assert x_str == "string in setup"
    global monkey
    assert monkey == 900
    monkey = 4
    assert monkey == 4

def test_another_copy_locals_to_globals(set_up_test_copy_to_globals):
    """Another test, with same fixture as previous one."""
    assert xx == 100

@fixture
def setup_test_cleanup(request):
    b = 77
    locals_to_globals()
    def finalize(): clear_locals_from_globals()
    request.addfinalizer(finalize)

def test_cleanup(setup_test_cleanup):
    """Another test, with same fixture as previous one."""
    assert b == 77
    q = globals()["b"]
    with raises(KeyError):
        q = globals()["xx"]
    #show_globals() # import from pytest_helper to use this debug fun


############ Below is experimental, testing different methods. ###############

#
# Test return locals() function from setup and assign in test program (not used).
#

def set_up_returning_locals():
    localvar = 1000
    localstr = "setup string"
    x = {"k1":1, "k2":2}
    return locals()

def test_returning_locals():
    """Works in Python 2, fails in Python 3."""
    if sys.version_info[0] == 3: skip()
    for k, v in set_up_returning_locals().items():
        exec(k+"=v")
        #exec("{0}=v".format(k), globals(), locals())
    print(localvar)
    assert localvar == 1000
    assert localstr == "setup string"
    assert x["k2"] == 2

#
# Test call init from test, where init then calls test (not used).
#

def set_up_call_test_from_init():
    localvar = 1000
    localstr = "setup string"
    x = {"k1":1, "k2":2}
    test_call_test_from_init()
    raise StopIteration

def test_call_test_from_init():
    """Seems to work when run from a separate test file.  When run from the
    same file it thinks there is infinite recursion."""
    return ##################################### remove to work on
    try: set_up_call_test_from_init()
    except StopIteration: return # not the correct error
    
    print(localvar)
    assert localvar == 1000
    assert localstr == "setup string"
    assert x["k2"] == 2


