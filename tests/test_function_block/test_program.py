#!/usr/bin/env python3
import os
import sys

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from base import TestCase

if __name__ == "__main__":
    test_case = TestCase("test_function_block", os.path.realpath(__file__))
    test_case.initialize_paths("test_function_input.z80", "test_function_expected.z80")
    test_case.run_test()