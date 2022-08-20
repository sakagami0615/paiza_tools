import argparse
import os
from typing import List

from tools.codegen.code_generator import CodeGenerator, RunTimeError
from tools.codegen.create_variable_dict import ExtractRenderParamError
from tools.common.color_code import ColorCode
from tools.envgen.envfile_generator import EnvFileGenerator
from tools.scraping.skillcheck_content import PageNotFoundError, SkillcheckContent


class RunEnvGen:
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
            print("[Info] Extract information from the skill check question text.")
            content = SkillcheckContent().create_question_content()

            # Env Gen
            print(
                f"[Info] Generate skillcheck environment folder '{self.args.workspace}'"
            )
            generator = EnvFileGenerator()
            generator.generate_file(content, self.args.workspace, self.args.overwrite)

            # Code Gen
            print(
                f"[Info] Generate skillcheck python script for No-{content.ques_number}."
            )
            ques_dirpath = os.path.join(self.args.workspace, content.ques_number)
            coder = CodeGenerator(self.root_dir)
            coder.generate_file(content, ques_dirpath, self.args.overwrite)
            print(
                ColorCode.GREEN.format(
                    "[Info] Environment folder generation is successful."
                )
            )

        except PageNotFoundError as e:
            print(
                ColorCode.RED.format(
                    f"[ERROR] {e} Please copy the HTML text of the skillcheck website to the clipboard."
                )
            )

        except FileExistsError as e:
            print(ColorCode.RED.format(f"[ERROR] {e}"))

        except FileNotFoundError as e:
            print(ColorCode.RED.format(f"[ERROR] {e}"))

        except ExtractRenderParamError as e:
            print(ColorCode.RED.format(f"[ERROR] {e}"))
            print(
                ColorCode.YELLOW.format(
                    "[WARNING] Generate skillcheck python script without extract data."
                )
            )
            coder.generate_file_empty_param(ques_dirpath)

        except RunTimeError as e:
            print(ColorCode.RED.format(f"[ERROR] {e}"))
            print(
                ColorCode.YELLOW.format(
                    "[WARNING] Generate skillcheck python script without extract data."
                )
            )
            coder.generate_file_empty_param(ques_dirpath)
