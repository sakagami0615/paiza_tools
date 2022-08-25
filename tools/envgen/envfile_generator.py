import os

from tools.common.file_function import check_dir_not_exist, write_json, write_text
from tools.config.file_config import FileConfig
from tools.scraping.question_content import QuestionContent


class EnvFileGenerator:
    def __init__(self):
        pass

    def _create_metadata(self, content: QuestionContent) -> dict:
        metadata_dict = {}
        metadata_dict["ques_number"] = content.ques_number
        metadata_dict["n_test_cases"] = content.n_test_cases
        metadata_dict["metadata_file"] = FileConfig.METADATA_FILE
        metadata_dict["script_file"] = FileConfig.SCRIPT_FILE
        metadata_dict["question_file"] = FileConfig.QUESTION_FILE
        metadata_dict["input_file_format"] = FileConfig.INPUT_FILE_FORMAT
        metadata_dict["output_file_format"] = FileConfig.OUTPUT_FILE_FORMAT
        return metadata_dict

    def generate_file(
        self, content: QuestionContent, dir_path: str, is_overwrite: bool
    ) -> None:
        create_dir_path = os.path.join(dir_path, content.ques_number)
        if not is_overwrite:
            check_dir_not_exist(create_dir_path)

        os.makedirs(create_dir_path, exist_ok=True)

        metadata = self._create_metadata(content)

        meta_file_path = os.path.join(create_dir_path, metadata["metadata_file"])
        ques_file_path = os.path.join(create_dir_path, metadata["question_file"])
        input_file_format = os.path.join(create_dir_path, metadata["input_file_format"])
        output_file_format = os.path.join(
            create_dir_path, metadata["output_file_format"]
        )

        write_json(meta_file_path, metadata)
        write_text(ques_file_path, content.html)

        for i, (input_text, answer_text) in enumerate(
            zip(content.input_list, content.answer_list)
        ):
            input_file_path = input_file_format.format(i + 1)
            output_file_path = output_file_format.format(i + 1)
            write_text(input_file_path, input_text)
            write_text(output_file_path, answer_text)
