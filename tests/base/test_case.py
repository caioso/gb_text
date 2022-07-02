import os
import sys
import subprocess

from termcolor import colored

sys.tracebacklimit = 0

class TestCase:
    def __init__(self, test_name: str, path: str):
        self._base_path = path
        self._test_name = test_name
        self._root_path = ""
        self._preprocessor_path = os.path.join("scripts", "rgbpre.py")
        self._build_path = ""
        self._rgbpre_path = ""
        self._include_path = ""
        self._test_input_path = ""
        self._test_output_path = ""
        self._expected_path = ""
        self._process_output = []

    def run_test(self) -> None:
        print(f"Running test {self._get_test_name()}...")
        self._run_rgbpre()
        self._check_results()
        print(f"             {self._get_test_name()} {self.get_pass_text()}\n")

    def initialize_paths(self, test_input: str, test_expectation: str) -> None:
        self._root_path = sys.argv[1]
        self._rgbpre_path = os.path.join(self._root_path, self._preprocessor_path)
        self._include_path = os.path.join(self._root_path, "inc")
        self._test_input_path = os.path.join(os.path.dirname(self._base_path),
                                    test_input)
        self._expected_path = os.path.join(os.path.dirname(self._base_path),
                                    test_expectation)
        self._test_output_path =  os.path.join(self._root_path, "build")
        self._output_file_name = test_input.split('.')[0] + ".pre.z80"
        self._test_output_path = os.path.join(self._test_output_path, self._output_file_name)

    def _run_rgbpre(self) -> None:
        process = subprocess.run(["python3", self._rgbpre_path, "-i", self._test_input_path, "-o",
                                 self._test_output_path, "-I", self._include_path],
                                 capture_output=True, text=True)
        self._process_output = process.stdout
        self._test_assert(0, process.returncode, "internal application error")

    def _check_results(self) -> None:
        test_result = []
        with open(self._expected_path) as f:
            test_result = f.readlines()

        expected_result = []
        with open(self._test_output_path) as f:
            expected_result = f.readlines()

        test_failed = False
        failure_cause = ""
        for idx, _ in enumerate(expected_result):
            if expected_result[idx] != test_result[idx]:
                test_failed = True
                failure_cause = f"mismatch in line: {idx + 1}\n"
                failure_cause += f"{colored('-', 'red')} {colored(expected_result[idx][:-1], 'red', attrs=['bold'])}\n"
                failure_cause += f"{colored('+', 'green')} {colored(test_result[idx][:-1], 'green', attrs=['bold'])}"
                self._test_assert(False, test_failed, failure_cause)

    def _test_assert(self, expected_value, test_value, failure_cause : str) :
        if expected_value != test_value:
            error_message = f"             {self._get_test_name()} {self.get_fail_text()}\n"
            error_message += f"\nCause: {failure_cause}\n"
            print(error_message)
            raise RuntimeError("Test failed", )

    def _get_test_name(self) -> str:
        return colored(self._test_name, 'cyan')

    def get_pass_text(self) -> str:
        return colored("PASS", 'green')

    def get_fail_text(self) -> str:
        return colored("FAIL", 'red')
