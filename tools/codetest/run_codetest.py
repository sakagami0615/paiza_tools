import argparse
import os
from typing import List

from tools.codetest.execute_code import ExecuteCode
from tools.common.color_code import ColorCode


class RunCodeTest:
    def __init__(self, root_dir: str, prog: str, args: List[str]):
        self.root_dir = root_dir
        self.args = self._get_cmdline_args(prog, args)

    def _get_cmdline_args(self, prog: str, args: List[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument(
            "-w",
            "--workspace",
            default="./",
            help="Path to create the environment." "[Default] current path",
        )
        return parser.parse_args(args)

    def run(self):
        try:
            tester = ExecuteCode(self.args.workspace)

            script_file_path = os.path.join(
                tester.dir_path, tester.metadata["script_file"]
            )
            print(f"[INFO] Python exec file: {script_file_path}")

            tester.execute_all_cases()

        except FileNotFoundError as e:
            print(ColorCode.RED.format(f"[ERROR] {e}"))
