#!albNotes

## TODO: update all the test scripts to use the import method, like test_RegexTrieDict
## TODO: update all the actual modules to delete commented-out older method using
##       subprocess

Adding the PYTHONPATH in the test files seemed to help some things, but
to use the package-relative addresses like wff_language.moduleName you
need to hav an
__init__.py in the tests dir.  Removing the
path relative things in the main modules fixes that, and now there is no
__init__.py in the tests dir.  But why is it designed that way, what is
failing or I am not fully grokking?

Note that Pytest recommends no __init__.py in the testing dir.
   http://pytest.org/latest/goodpractises.html

Here is one way to include the PYTHONPATH stuff, running from
within PYTHON rather than altering the environment:
   import sys, os
   filePath = os.path.dirname(os.path.abspath(__file__))
   sys.path.insert(0, filePath + '/../')

NOTE the new way of running tests from the test file (based on above) is now
used in test_RegexTrieDict, importing and not using subprocess.  Here is the
old way, for reference:

    # When this file is run as a script call py.test on it.
    import subprocess, sys, os
    os.environ["PYTHONPATH"] = "../"
    subprocess.call([sys.executable, "-m", "pytest", "-v", __file__])
    #subprocess.call(["py.test-2.7", "-v", __file__])
    sys.exit(0)

Here is the old way from the bottom of the actual modules of the package:

    import subprocess
    subprocess.call(["py.test-2.7", "-v", "tests/test_trie_dict.py"])
    #subprocess.call(["gnome-terminal", "-x", "py.test", "-v", "tests/test_trieDict.py"])
