#!/bin/bash
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
   $1 # Run using the shebang.
   #python $1 # Run as an argument to python.
}

# =================================
# Run the child dir tests. 
# =================================

# Run from the code file with absolute path.
$testdir/test_dir_tree/project_root_t/package_dir/in_child_dir.py

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

