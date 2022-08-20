import os
from typing import Tuple

from tools.codetest.execute_result import ExecuteResult
from tools.common.color_code import ColorCode
from tools.common.file_function import check_file_exist, read_json, read_text
from tools.common.run_command import run_command
from tools.config.file_config import FileConfig


class ExecuteCode:
    def __init__(self, dirpath: str):
        self.dirpath = dirpath
        meta_file_path = os.path.join(dirpath, FileConfig.METADATA_FILE)
        check_file_exist(meta_file_path)
        self.metadata = read_json(meta_file_path)
        self._check_env_data()

    def _check_env_data(self) -> None:
        script_file_path = os.path.join(self.dirpath, self.metadata["script_file"])
        check_file_exist(script_file_path)
        for case_id in range(self.metadata["n_test_cases"]):
            input_file_path = os.path.join(
                self.dirpath, self.metadata["input_file_format"].format(case_id + 1)
            )
            output_file_path = os.path.join(
                self.dirpath, self.metadata["output_file_format"].format(case_id + 1)
            )
            check_file_exist(input_file_path)
            check_file_exist(output_file_path)

    def _run_one_case(self, case_id: int) -> Tuple[bool, str]:
        script_file_name = self.metadata["script_file"]
        script_file_path = os.path.join(self.dirpath, script_file_name)

        input_file_name = self.metadata["input_file_format"].format(case_id + 1)
        output_file_name = self.metadata["output_file_format"].format(case_id + 1)

        input_file_path = os.path.join(self.dirpath, input_file_name)
        output_file_path = os.path.join(self.dirpath, output_file_name)

        input_text = read_text(input_file_path)
        output_text = read_text(output_file_path)

        exec_cmd = ["python", script_file_path]
        returncode, stdout = run_command(exec_cmd, input_file_path)

        is_correct, result_state, result_message = ExecuteResult().output_result(
            input_file_name, input_text, output_text, returncode, stdout
        )
        return is_correct, result_state, result_message

    def execute_all_cases(self) -> None:
        script_file_name = self.metadata["script_file"]
        print(f"exec script: {script_file_name}")

        n_test_cases = self.metadata["n_test_cases"]
        n_corrects = 0
        for case_id in range(n_test_cases):
            is_correct, _, result_message = self._run_one_case(case_id)
            if is_correct:
                n_corrects += 1
            print(result_message)

        if n_corrects >= n_test_cases:
            result_message = "All test cases PASSED!"
            print(ColorCode.GREEN.format(result_message))
        else:
            result_message = (
                f"Some test cases FAILED (pass case {n_corrects} / {n_test_cases})"
            )
            print(ColorCode.RED.format(result_message))
