import pytest_helper

testing_var1 = "tvar1"
testing_var2 = "tvar2"

# TODO: test some making things global and modifying, just to be sure
# that works.

if __name__ == "__main__":
    pytest_helper.script_run(self_test=True, pytest_args="-v")

pytest_helper.autoimport()  # Do some basic imports automatically.

def my_setup1():
    setup_var1 = "foo"
    setup_var2 = "bar"
    setup_var3 = "global"

    locals_to_globals(clear=True)
    testing_var2 = "overwrite"
    print("LocalsToGlobalsError  is", pytest_helper.LocalsToGlobalsError)
    with raises(pytest_helper.LocalsToGlobalsError):
        locals_to_globals()
    locals_to_globals(noclobber=False)

def my_setup2():
    setup_var1 = "foo"
    setup_var2 = "egg"
    global setup_var3
    setup_var3 = "modified"
    locals_to_globals()

def test_var_values():
    my_setup1()
    my_setup2()

    assert testing_var1 == "tvar1"
    assert testing_var2 == "overwrite"
    assert setup_var1 == "foo"
    assert setup_var2 == "egg"
    assert setup_var3 == "modified"

    test_dict = {}
    with raises(KeyError):
        test_dict[5]
    locals_to_globals(clear=True)

    # Note that clear above will also clear the globally modified setup_var3,
    # because it was first copied to globals by locals_to_globals and saved on
    # the list to delete.
    with raises(NameError):
        x = setup_var3

def test_unindent():
    assert "    Hello." == unindent(8, """
            Hello.
        """)
    assert "Hello." == unindent(12, """
            Hello.
        """)

    assert "unindented line 1\n    indented line 2\nunindented line 3" == unindent(8, """
        unindented line 1
            indented line 2
        unindented line 3
        """)

    with raises(pytest_helper.PytestHelperException):
        assert unindent(3, "   One line") == "FAIL"

    assert unindent(3, "   Two\nlines") == ""

    with raises(pytest_helper.PytestHelperException):
        assert unindent(3, "\n  Hello\nthere.") # Try to unindent non-whitespace.

    with raises(pytest_helper.PytestHelperException):
        assert unindent(1, "\nHello\nthere.\n") # Try to unindent non-whitespace.

    # Test handling trailing newlines.
    assert unindent(0, "\nHello\nthere.\n\n") == "Hello\nthere.\n"
    assert unindent(0, "\nHello\nthere.\n") == "Hello\nthere."
    assert unindent(0, "\nHello\nthere.") == "Hello"

