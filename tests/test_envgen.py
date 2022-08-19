import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest

from tools.envgen.envfile_generator import EnvFileGenerator
from tools.scraping.question_content import QuestionContent


class TestEnvGen:

    def test_generate_new_env(self, tmpdir):
        content = QuestionContent('dummy_html', 'dummy_number', 'dummy_sentence',
                                  'dummy_format', 'dummy_output', 'dummy_condition',
                                  2, ['dummy_input_1', 'dummy_input_2'], ['dummy_answer_1, dummy_answer_2'])
        EnvFileGenerator().generate_file(content, tmpdir, True)

        dirpath = os.path.join(tmpdir, 'dummy_number')
        is_dir = True if os.path.isdir(dirpath) else False
        assert is_dir == True


    def test_generate_overwrite_env(self, tmpdir):
        content = QuestionContent('dummy_html', 'dummy_number', 'dummy_sentence',
                                  'dummy_format', 'dummy_output', 'dummy_condition',
                                  2, ['dummy_input_1', 'dummy_input_2'], ['dummy_answer_1, dummy_answer_2'])
        EnvFileGenerator().generate_file(content, tmpdir, True)
        EnvFileGenerator().generate_file(content, tmpdir, True)

        dirpath = os.path.join(tmpdir, 'dummy_number')
        is_dir = True if os.path.isdir(dirpath) else False
        assert is_dir == True


    def test_restrict_overwrite_env_generation(self, tmpdir):
        content = QuestionContent('dummy_html', 'dummy_number', 'dummy_sentence',
                                  'dummy_format', 'dummy_output', 'dummy_condition',
                                  2, ['dummy_input_1', 'dummy_input_2'], ['dummy_answer_1, dummy_answer_2'])
        EnvFileGenerator().generate_file(content, tmpdir, False)

        is_success = False
        with pytest.raises(FileExistsError) as e:
            EnvFileGenerator().generate_file(content, tmpdir, False)
            is_success = True

        assert is_success == False
        env_dir_path = os.path.join(tmpdir, 'dummy_number')
        assert str(e.value) == f"This folder('{env_dir_path}') already exists"
