from typing import List

import argparse

from tools.codegen.code_generator import CodeGenerator
from tools.scraping.skillcheck_content import SkillcheckContent

from tools.scraping.skillcheck_content import PageNotFoundError
from tools.common.file_exist_checker import FileNotExistsError


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
            content = SkillcheckContent().create_question_content()
            CodeGenerator(self.root_dir).generate_file(
                content, self.args.workspace, self.args.overwrite
            )

        except PageNotFoundError:
            print("ERROR1")
        except FileExistsError:
            print("ERROR2")
        except FileNotExistsError:
            print("ERROR3")
