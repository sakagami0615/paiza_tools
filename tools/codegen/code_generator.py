import os
import json
import yaml
from jinja2 import Environment, FileSystemLoader

from tools.config.file_config import FileConfig
from tools.codegen.extract_render_param import ExtractRenderParam
from tools.scraping.question_content import QuestionContent


class FileNotExistsError(Exception):
    pass


class CodeGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        config_filepath = os.path.join(self.root_dir, "user_config.yml")
        self._check_file_not_exist(config_filepath)
        with open(config_filepath) as f:
            self.config = yaml.safe_load(f)

    def _check_file_exist(self, filepath: str) -> None:
        if os.path.isfile(filepath):
            raise FileExistsError

    def _check_file_not_exist(self, filepath: str) -> None:
        if not os.path.isfile(filepath):
            raise FileNotExistsError

    def _render_template(
        self, template_dir_path: str, template_file_name: str, render_param_dict: dict
    ) -> str:
        template_env = Environment(
            loader=FileSystemLoader(template_dir_path, encoding="utf8")
        )
        code_template = template_env.get_template(template_file_name)
        return code_template.render(render_param_dict)

    def generate_file(
        self, content: QuestionContent, dirpath: str, is_overwrite: bool
    ) -> None:
        # Load metadata
        meta_file_path = os.path.join(dirpath, FileConfig.METADATA_FILE)
        self._check_file_not_exist(meta_file_path)

        # Get script file path. In addition, check for existence only when is_overwrite is True.
        with open(meta_file_path, "r") as f:
            metadata = json.load(f)
            script_file_path = os.path.join(dirpath, metadata["script_file"])
        if not is_overwrite:
            self._check_file_exist(script_file_path)

        # Get template file path. In addition, check for existence.
        template_file_path = os.path.join(
            self.root_dir, self.config["Template"]["FilePath"]
        )
        self._check_file_not_exist(template_file_path)

        # Get the necessary parameters for render from content and create a script
        (template_dir_path, template_file_name) = os.path.split(template_file_path)
        render_param_dict = ExtractRenderParam(
            self.config, content
        ).extract_param_dict()
        render_code = self._render_template(
            template_dir_path, template_file_name, render_param_dict
        )
        with open(script_file_path, "w") as f:
            f.write(render_code)
