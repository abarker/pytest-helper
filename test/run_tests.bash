#!/bin/bash
#
# These are tests run from the command line, to test the relative pathnames
# and the directory-location lookup when called from different working directories.
# This does not run all the tests, though, so py.test itself should still be run.
#
# Usage: run_tests
#
# Tree diagram of the test dir structure, generated with the Unix command:
#    tree -F --charset x | tr '|\-`' ' '
#
# test
#     test_dir_tree/
#         project_root_t/
#             package_dir/
#                 in_child_dir.py
#                 __init__.py
#                 in_same_dir.py
#                 in_same_file.py
#                 in_sibling_dir.py
#                 test/
#                     test_in_child_dir.py
#                 test_in_same_dir.py
#             test/
#                 test_in_sibling_dir.py

testdir="$(dirname $(readlink -f $0))" # Get this script's directory when run anywhere.

function run_test {
   # Run the test.  Can swap in running from python to make sure that works, too.
   #$1 # Run using the shebang.  This can mess up virtualenv, so don't use.
   echo "python \"$1\""
   python "$1" || { echo -e "\nFailed to run test..."; exit; }
   echo
   echo
   echo
}

# =================================
# Run the non-package test. 
# =================================

cd $testdir
run_test run_tests_not_in_package.py
cd test_dir_tree
run_test ../run_tests_not_in_package.py

# =================================
# Run the child dir tests. 
# =================================

cd $testdir

# Run from the code file with absolute path.
run_test $testdir/test_dir_tree/project_root_t/package_dir/in_child_dir.py

# Run from the code file with relative path from its own dir.
cd test_dir_tree/project_root_t/package_dir
run_test ./in_child_dir.py

# Run from the code file with relative path from its subdir.
cd test
run_test ../in_child_dir.py

# Run from the test file with absolute path.
run_test $testdir/test_dir_tree/project_root_t/package_dir/test/test_in_child_dir.py

# Run from the test file with relative path from its own dir.
run_test ./test_in_child_dir.py

# Run from the test file with relative path from its parent dir.
cd ..
run_test ./test/test_in_child_dir.py

# =================================
# Run the same dir tests.
# =================================

# =================================
# Run the sibling dir tests.
# =================================

# =================================
# Run the same file tests.
# =================================

