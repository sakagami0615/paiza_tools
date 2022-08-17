from typing import List, Tuple

import os
import json
import subprocess
from tools.config.file_config import FileConfig
from tools.common.file_exist_checker import check_file_exist


class ExecuteCode:
    def __init__(self, dirpath: str):
        self.dirpath = dirpath
        meta_file_path = os.path.join(dirpath, FileConfig.METADATA_FILE)
        check_file_exist(meta_file_path)
        with open(meta_file_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def _run_command(
        self, exec_cmd: List[str], input_file_path: str
    ) -> Tuple[int, str]:
        with open(input_file_path, "r", encoding="utf-8") as f:
            proc = subprocess.run(
                exec_cmd,
                stdin=f,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
        return proc.returncode, proc.stdout

    def _execute_one_case(self, case_id: int) -> None:
        script_file_path = os.path.join(self.dirpath, self.metadata["script_file"])
        check_file_exist(script_file_path)

        input_file_path = os.path.join(
            self.dirpath, self.metadata["input_file_format"].format(case_id)
        )
        output_file_path = os.path.join(
            self.dirpath, self.metadata["output_file_format"].format(case_id)
        )
        check_file_exist(input_file_path)
        check_file_exist(output_file_path)

        exec_cmd = ["python", script_file_path]
        returncode, stdout = self._run_command(exec_cmd, input_file_path)
        print(returncode)
        print(stdout)

    def execute_all_cases(self) -> None:
        for case_id in range(1, self.metadata["n_test_cases"] + 1):
            self._execute_one_case(case_id)
