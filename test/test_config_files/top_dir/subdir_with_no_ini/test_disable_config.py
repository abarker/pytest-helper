"""

"""

from __future__ import print_function, division, absolute_import
import pytest_helper
pytest_helper.init(conf=False)

testing_var = "foo"

if __name__ == "__main__":
    pytest_helper.script_run(self_test=True, pytest_args="-v")

pytest_helper.autoimport()

def test_config_values():
    assert testing_var == "foo"
    clear_locals_from_globals() # Call this before locals_to_globals, make sure it works.
    locals_to_globals()

    # This is on the autoimport skip list in disabled ini file.
    # It should work with config files disabled.
    clear_locals_from_globals()

