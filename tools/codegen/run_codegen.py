import argparse
from typing import List

from tools.codegen.code_generator import CodeGenerator
from tools.codetest.execute_code import ExecuteCode, RunTimeError
from tools.scraping.skillcheck_content import PageNotFoundError, SkillcheckContent


class RunCodeGen:
    def __init__(self, root_dir: str, prog: str, args: List[str]):
        self.root_dir = root_dir
        self.args = self._get_cmdline_args(prog, args)

    def _get_cmdline_args(self, prog: str, args: List[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument(
            "-w",
            "--workspace",
            default="./",
            help="Path to question directory. (ex: A001)" "[Default] current path",
        )
        parser.add_argument(
            "-o",
            "--overwrite",
            type=bool,
            default=False,
            help="Whether to overwrite the environment if it already exists."
            "[Default] False (disable)",
        )
        return parser.parse_args(args)

    def run(self):
        try:
            # Code Gen
            content = SkillcheckContent().create_question_content()
            CodeGenerator(self.root_dir).generate_file(
                content, self.args.workspace, self.args.overwrite
            )
        except PageNotFoundError:
            print("PageNotFoundError")
            return
        except FileExistsError:
            print("FileExistsError")
            return
        except FileNotFoundError:
            print("FileNotFoundError")
            return

        try:
            # Check Gen Code RTE
            ExecuteCode(self.args.workspace).check_run_time_error()
        except RunTimeError:
            print("RunTimeError")
