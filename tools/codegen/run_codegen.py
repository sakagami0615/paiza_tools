import argparse
from typing import List

from tools.codegen.code_generator import CodeGenerator, RunTimeError
from tools.codegen.create_variable_dict import ExtractRenderParamError
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
            coder = CodeGenerator(self.root_dir)
            coder.generate_file(content, self.args.workspace, self.args.overwrite)

        # TODO: 成功/失敗のメッセージを作成する
        except PageNotFoundError:
            print("PageNotFoundError")

        except FileExistsError:
            print("FileExistsError")

        except FileNotFoundError:
            print("FileNotFoundError")

        except ExtractRenderParamError:
            coder.generate_file_empty_param(self.args.workspace)
            print("ExtractRenderParamError")

        except RunTimeError:
            coder.generate_file_empty_param(self.args.workspace)
            print("RunTimeError")
