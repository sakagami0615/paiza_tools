import os
import json
from tools.config.file_config import FileConfig
from tools.scraping.question_content import QuestionContent


class EnvFileGenerator:

    def __init__(self):
        pass

    def __check_env_exist(self, dirpath) -> None:
        if os.path.isdir(dirpath):
            raise FileExistsError

    def __create_metadata(self, content: QuestionContent) -> dict:
        metadata_dict = {}
        metadata_dict['ques_number'] = content.ques_number
        metadata_dict['n_test_cases'] = content.n_test_cases
        metadata_dict['metadata_file'] = FileConfig.METADATA_FILE
        metadata_dict['script_file'] = FileConfig.SCRIPT_FILE
        metadata_dict['question_file'] = FileConfig.QUESTION_FILE
        metadata_dict['input_file_format'] = FileConfig.INPUT_FILE_FORMAT
        metadata_dict['output_file_format'] = FileConfig.OUTPUT_FILE_FORMAT
        return metadata_dict

    def generate_file(self, content: QuestionContent, dirpath: str, is_overwrite: bool) -> None:
        create_dirpath = os.path.join(dirpath, content.ques_number)
        if not is_overwrite:
            self.__check_env_exist(create_dirpath)

        os.makedirs(create_dirpath, exist_ok=True)

        metadata = self.__create_metadata(content)

        meta_file_path = os.path.join(create_dirpath, metadata['metadata_file'])
        ques_file_path = os.path.join(create_dirpath, metadata['question_file'])
        input_file_format = os.path.join(create_dirpath, metadata['input_file_format'])
        output_file_format = os.path.join(create_dirpath, metadata['output_file_format'])

        with open(meta_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        with open(ques_file_path, 'w') as f:
            f.write(content.html)

        for i, (input_text, answer_text) in enumerate(zip(content.input_list, content.answer_list)):
            with open(input_file_format.format(i + 1), 'w') as f:
                f.write(input_text)
            with open(output_file_format.format(i + 1), 'w') as f:
                f.write(answer_text)
