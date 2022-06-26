#!/usr/bin/env python3
import os
import sys
import subprocess

class TestCase:
    def __init__(self):
        self._root_path = ""
        self._preprocessor_path = os.path.join("scripts", "rgbpre.py")
        self._build_path = ""
        self._rgbpre_path = ""
        self._include_path = ""
        self._test_input_path = ""
        self._test_output_path = ""
        self._process_output = []

    def run_test(self):
        result = self.run_rgbpre()
        print(f"return code {result}")

    def run_rgbpre(self) -> int:
        process = subprocess.run(["python3", self._rgbpre_path, "-i", self._test_input_path, "-o",
                                self._test_output_path, "-I", self._include_path],
                                capture_output=True,  text=True)
        self._process_output = process.stdout
        return process.returncode

    def initialize_paths(self, test_input: str):
        self._root_path = sys.argv[1]
        self._rgbpre_path = os.path.join(self._root_path, self._preprocessor_path)
        self._include_path = os.path.join(self._root_path, "inc")
        self._test_input_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    test_input)
        self._test_output_path =  os.path.join(self._root_path, "build")
        self._output_file_name = test_input.split('.')[0] + ".pre.z80"
        self._test_output_path = os.path.join(self._test_output_path, self._output_file_name)

if __name__ == "__main__":
    test_case = TestCase()
    test_case.initialize_paths("test_program_input.z80")
    test_case.run_test()