"""

"""

from __future__ import print_function, division, absolute_import
import pytest_helper

testing_var = "foo"

if __name__ == "__main__":
    pytest_helper.script_run(self_test=True, pytest_args="-v")

pytest_helper.autoimport()

def test_config_values():
    assert testing_var == "foo"
    locals_to_globals()
    with raises(NameError):
        clear_locals_from_globals() # This is on the autoimport skip list in ini file.

