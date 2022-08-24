import os
from collections import defaultdict
from typing import Optional, Tuple

from jinja2 import Environment, FileSystemLoader

from tools.codegen.extract_render_param import ExtractRenderParam
from tools.common.file_function import (
    check_file_exist,
    check_file_not_exist,
    read_json,
    read_text,
    read_yaml,
    write_text,
)
from tools.common.run_command import run_command
from tools.config.file_config import FileConfig
from tools.scraping.question_content import QuestionContent


class RunTimeError(Exception):
    def __init__(self):
        message = "There was a problem with the generated code."
        super().__init__(message)


class InputProcessingError(Exception):
    def __init__(self):
        message = "There was a problem with the generated code."
        super().__init__(message)


class CodeGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        config_file_path = os.path.join(self.root_dir, "user_config.yaml")
        check_file_exist(config_file_path)
        self.config = read_yaml(config_file_path)

    def _render_template(
        self,
        code_template_dir_path: str,
        code_template_file_name: str,
        render_param_dict: dict,
    ) -> str:
        template_env = Environment(
            loader=FileSystemLoader(code_template_dir_path, encoding="utf8")
        )
        code_template = template_env.get_template(code_template_file_name)
        return code_template.render(render_param_dict)

    def _check_runtime_error(
        self,
        code_script_file_path: str,
        render_code: str,
        n_test_cases: int,
        input_file_format: str,
    ) -> None:
        write_text(code_script_file_path, render_code)
        for case_id in range(n_test_cases):
            input_file_path = input_file_format.format(case_id + 1)

            exec_cmd = ["python", code_script_file_path]
            returncode, _ = run_command(exec_cmd, input_file_path)
            if returncode != 0:
                raise RunTimeError

    def _check_input_processing_error(
        self,
        test_file_path: str,
        test_code: str,
        n_test_cases: int,
        input_file_format: str,
        output_file_format: str,
    ) -> None:
        for case_id in range(n_test_cases):
            write_text(test_file_path, test_code)
            input_file_path = input_file_format.format(case_id + 1)
            output_text = read_text(output_file_format.format(case_id + 1))
            except_text = "\n".join(output_text.split())

            exec_cmd = ["python", test_file_path]
            _, actual_text = run_command(exec_cmd, input_file_path)
            os.remove(test_file_path)

            if actual_text != except_text:
                raise InputProcessingError

    def _confirm_env_dir(
        self, dirpath: str, is_overwrite: bool
    ) -> Optional[Tuple[int, str, str, str]]:
        # Load metadata
        meta_file_path = os.path.join(dirpath, FileConfig.METADATA_FILE)
        check_file_exist(meta_file_path)

        # Get script file path. In addition, check for existence only when is_overwrite is True.
        metadata = read_json(meta_file_path)
        code_script_file_path = os.path.join(dirpath, metadata["script_file"])
        if not is_overwrite:
            check_file_not_exist(code_script_file_path)

        test_script_file_path = os.path.join(dirpath, "test_" + metadata["script_file"])

        # Check testcase file exists
        input_file_format = os.path.join(dirpath, metadata["input_file_format"])
        output_file_format = os.path.join(dirpath, metadata["input_file_format"])
        n_test_cases = metadata["n_test_cases"]
        for case_id in range(n_test_cases):
            check_file_exist(input_file_format.format(case_id + 1))
            check_file_exist(output_file_format.format(case_id + 1))

        # Get template file path. In addition, check for existence.
        code_template_file_path = os.path.join(
            self.root_dir, self.config["Template"]["FilePath"]
        )
        check_file_exist(code_template_file_path)
        test_template_file_path = os.path.join(
            self.root_dir, "tools/codegen/input_test_template.txt"
        )
        check_file_exist(test_template_file_path)
        return (
            code_script_file_path,
            test_script_file_path,
            n_test_cases,
            input_file_format,
            output_file_format,
            code_template_file_path,
            test_template_file_path,
        )

    def generate_file(
        self, content: QuestionContent, dirpath: str, is_overwrite: bool
    ) -> None:
        (
            code_script_file_path,
            test_script_file_path,
            n_test_cases,
            input_file_format,
            output_file_format,
            code_template_file_path,
            test_template_file_path,
        ) = self._confirm_env_dir(dirpath, is_overwrite)

        # Get the necessary parameters for render from content and create a script
        render_param_dict = ExtractRenderParam(
            self.config, content
        ).extract_param_dict()

        (code_template_dir_path, code_template_file_name) = os.path.split(
            code_template_file_path
        )
        render_code = self._render_template(
            code_template_dir_path, code_template_file_name, render_param_dict
        )

        (test_template_dir_path, test_template_file_name) = os.path.split(
            test_template_file_path
        )
        test_code = self._render_template(
            test_template_dir_path, test_template_file_name, render_param_dict
        )

        self._check_runtime_error(
            code_script_file_path, render_code, n_test_cases, input_file_format
        )
        self._check_input_processing_error(
            test_script_file_path,
            test_code,
            n_test_cases,
            input_file_format,
            output_file_format,
        )

    def generate_file_empty_param(self, dirpath: str) -> None:
        (
            code_script_file_path,
            _,
            _,
            _,
            _,
            code_template_file_path,
            _,
        ) = self._confirm_env_dir(dirpath, True)

        (code_template_dir_path, code_template_file_name) = os.path.split(
            code_template_file_path
        )
        render_param_dict = defaultdict(str)

        render_code = self._render_template(
            code_template_dir_path, code_template_file_name, render_param_dict
        )
        write_text(code_script_file_path, render_code)
