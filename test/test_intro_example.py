import pytest_helper

# Regular program code goes here.

testing_var = "foo"

# Test running below, but only when the module is invoked as a script.

if __name__ == "__main__":  # This guard conditional is optional.
   pytest_helper.script_run(self_test=True, pytest_args="-v")

pytest_helper.auto_import()  # Do some basic imports automatically.

def my_setup(): # Could be a pytest fixture instead of a regular function.
   setup_var = "bar"
   locals_to_globals(clear=True)  # Copies setup_var to the module's global namespace.

def test_var_values():
   my_setup()
   assert testing_var == "foo"  # Set in the regular code above.
   assert setup_var == "bar"  # Read from the global namespace.
   test_dict = {}
   with raises(KeyError):  # Pytest function raises was autoimported.
       test_dict[5]

