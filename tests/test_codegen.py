import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collections import defaultdict

import pytest

from tools.codegen.code_generator import CodeGenerator
from tools.codegen.extract_render_param import ExtractRenderParam
from tools.common.file_function import write_json
from tools.scraping.question_content import QuestionContent

TAB = '    '


def create_dummy_config() -> dict:
    return {
        'TabString': '    ',
        'Template': {
            'FilePath': 'tests/template_default.py',
            'StdinProcCode': 'next(iter_var)'
        }
    }


class TestCodeGen:

    def test_enable_datatype(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content = QuestionContent('', '', '',
                                  'L M N', '', '',
                                  1, ['1 2.0 "hello"'], ['3'])
        result = ExtractRenderParam(config, content).extract_param_dict()
        assert (result['is_yes_str'], result['yes_str']) == (False, '')
        assert (result['is_no_str'], result['no_str']) == (False, '')
        assert result['solve_argument'] == 'L, M, N'

        expected_code  = f"L = int({proc_code})\n{TAB}"
        expected_code += f"M = float({proc_code})\n{TAB}"
        expected_code += f"N = str({proc_code})"
        assert result['input_process'] == expected_code


    def test_enable_const_yesy_no(self):
        config = create_dummy_config()
        content_1 = QuestionContent('', '', '',
                                    '', '"yes" or "no"', '',
                                    1, [''], [''])
        result_1 = ExtractRenderParam(config, content_1).extract_param_dict()
        assert (result_1['is_yes_str'], result_1['yes_str']) == (True, 'yes')
        assert (result_1['is_no_str'], result_1['no_str']) == (True, 'no')

        content_2 = QuestionContent('', '', '',
                                    '', '"Yes"、"No"', '',
                                    1, [''], [''])
        result_2 = ExtractRenderParam(config, content_2).extract_param_dict()
        assert (result_2['is_yes_str'], result_2['yes_str']) == (True, 'Yes')
        assert (result_2['is_no_str'], result_2['no_str']) == (True, 'No')

        content_3 = QuestionContent('', '', '',
                                    '', 'A出ない場合"YES"、そうでない場合"NO"としてください。', '',
                                    1, [''], [''])
        result_3 = ExtractRenderParam(config, content_3).extract_param_dict()
        assert (result_3['is_yes_str'], result_3['yes_str']) == (True, 'YES')
        assert (result_3['is_no_str'], result_3['no_str']) == (True, 'NO')


    def test_disable_const_yesy_no(self):
        config = create_dummy_config()
        content = QuestionContent('', '', '',
                                  '', '"y e s" or "n o"', '',
                                  1, [''], [''])
        result = ExtractRenderParam(config, content).extract_param_dict()
        assert (result['is_yes_str'], result['yes_str']) == (False, '')
        assert (result['is_no_str'], result['no_str']) == (False, '')


    def test_exist_list_single_col(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content_1 = QuestionContent('', '', '',
                                    'a_3', '', '',
                                    1, ['1 2 3'], ['3'])
        result_1 = ExtractRenderParam(config, content_1).extract_param_dict()
        expected_code_1  = f"a_list = [None] * 3\n{TAB}"
        expected_code_1 += f"for i in range(3):\n{TAB*2}"
        expected_code_1 += f"a = int({proc_code})\n{TAB*2}"
        expected_code_1 +=  "a_list[i] = a"
        assert result_1['solve_argument'] == 'a_list'
        assert result_1['input_process'] == expected_code_1

        content_2 = QuestionContent('', '', '',
                                    'N\na_N', '', '',
                                    1, ['5\n1.0 2.0 3.0 4.0 5.0'], ['3'])
        result_2 = ExtractRenderParam(config, content_2).extract_param_dict()
        expected_code_2  = f"N = int({proc_code})\n{TAB}"
        expected_code_2 += f"a_list = [None] * N\n{TAB}"
        expected_code_2 += f"for i in range(N):\n{TAB*2}"
        expected_code_2 += f"a = float({proc_code})\n{TAB*2}"
        expected_code_2 +=  "a_list[i] = a"

        assert result_2['solve_argument'] == 'N, a_list'
        assert result_2['input_process'] == expected_code_2


    def test_exist_scalar_and_list_in_line(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content = QuestionContent('', '', '',
                                  'M\nN a_M', '', '',
                                  1, ['3\n0 1 2 3'], ['3'])
        result = ExtractRenderParam(config, content).extract_param_dict()
        expected_code  = f"M = int({proc_code})\n{TAB}"
        expected_code += f"a_list = [None] * M\n{TAB}"
        expected_code += f"N = int({proc_code})\n{TAB}"
        expected_code += f"for i in range(M):\n{TAB*2}"
        expected_code += f"a = int({proc_code})\n{TAB*2}"
        expected_code +=  "a_list[i] = a"

        assert result['solve_argument'] == 'M, N, a_list'
        assert result['input_process'] == expected_code


    def test_exist_list_single_row(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content_1 = QuestionContent('', '', '',
                                    'a_3', '', '',
                                    1, ['1\n2\n3'], ['3'])
        result_1 = ExtractRenderParam(config, content_1).extract_param_dict()
        expected_code_1  = f"a_list = [None] * 3\n{TAB}"
        expected_code_1 += f"for i in range(3):\n{TAB*2}"
        expected_code_1 += f"a = int({proc_code})\n{TAB*2}"
        expected_code_1 +=  "a_list[i] = a"
        assert result_1['solve_argument'] == 'a_list'
        assert result_1['input_process'] == expected_code_1

        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content_2 = QuestionContent('', '', '',
                                    'M\na_M', '', '',
                                    1, ['1\n2\n3'], ['3'])
        result_2 = ExtractRenderParam(config, content_2).extract_param_dict()
        expected_code_2  = f"M = int({proc_code})\n{TAB}"
        expected_code_2 += f"a_list = [None] * M\n{TAB}"
        expected_code_2 += f"for i in range(M):\n{TAB*2}"
        expected_code_2 += f"a = int({proc_code})\n{TAB*2}"
        expected_code_2 +=  "a_list[i] = a"
        assert result_2['solve_argument'] == 'M, a_list'
        assert result_2['input_process'] == expected_code_2


    def test_exist_list_multi_row_single_unit(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content_1 = QuestionContent('', '', '',
                                    'a_3 b_3', '', '',
                                    1, ['1 11\n2 22\n3 33'], ['3'])
        result_1 = ExtractRenderParam(config, content_1).extract_param_dict()
        expected_code_1  = f"a_list = [None] * 3\n{TAB}"
        expected_code_1 += f"b_list = [None] * 3\n{TAB}"
        expected_code_1 += f"for i in range(3):\n{TAB*2}"
        expected_code_1 += f"a = int({proc_code})\n{TAB*2}"
        expected_code_1 += f"a_list[i] = a\n{TAB*2}"
        expected_code_1 += f"b = int({proc_code})\n{TAB*2}"
        expected_code_1 +=  "b_list[i] = b"
        assert result_1['solve_argument'] == 'a_list, b_list'
        assert result_1['input_process'] == expected_code_1

        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content_2 = QuestionContent('', '', '',
                                    'M\na_M b_M', '', '',
                                    1, ['3\n1 11\n2 22\n3 33'], ['3'])
        result_2 = ExtractRenderParam(config, content_2).extract_param_dict()
        expected_code_2  = f"M = int({proc_code})\n{TAB}"
        expected_code_2 += f"a_list = [None] * M\n{TAB}"
        expected_code_2 += f"b_list = [None] * M\n{TAB}"
        expected_code_2 += f"for i in range(M):\n{TAB*2}"
        expected_code_2 += f"a = int({proc_code})\n{TAB*2}"
        expected_code_2 += f"a_list[i] = a\n{TAB*2}"
        expected_code_2 += f"b = int({proc_code})\n{TAB*2}"
        expected_code_2 +=  "b_list[i] = b"
        assert result_2['solve_argument'] == 'M, a_list, b_list'
        assert result_2['input_process'] == expected_code_2


    def test_exist_list_multi_row_double_unit(self):
        config = create_dummy_config()
        proc_code = config['Template']['StdinProcCode']
        content = QuestionContent('', '', '',
                                  'q_3 w_3\nM\na_M b_M', '', '',
                                  1, ['1 11\n2 22\n3 33\n3\n1 11\n2 22\n3 33'], ['3'])
        result = ExtractRenderParam(config, content).extract_param_dict()
        expected_code  = f"q_list = [None] * 3\n{TAB}"
        expected_code += f"w_list = [None] * 3\n{TAB}"
        expected_code += f"for i in range(3):\n{TAB*2}"
        expected_code += f"q = int({proc_code})\n{TAB*2}"
        expected_code += f"q_list[i] = q\n{TAB*2}"
        expected_code += f"w = int({proc_code})\n{TAB*2}"
        expected_code += f"w_list[i] = w\n{TAB}"
        expected_code += f"M = int({proc_code})\n{TAB}"
        expected_code += f"a_list = [None] * M\n{TAB}"
        expected_code += f"b_list = [None] * M\n{TAB}"
        expected_code += f"for i in range(M):\n{TAB*2}"
        expected_code += f"a = int({proc_code})\n{TAB*2}"
        expected_code += f"a_list[i] = a\n{TAB*2}"
        expected_code += f"b = int({proc_code})\n{TAB*2}"
        expected_code +=  "b_list[i] = b"
        assert result['solve_argument'] == 'q_list, w_list, M, a_list, b_list'
        assert result['input_process'] == expected_code


    def test_not_find_config_file(self, tmpdir):
        is_file_exist = False
        with pytest.raises(FileNotFoundError) as e:
            CodeGenerator(tmpdir)
            is_file_exist = True

        assert is_file_exist == False
        config_file_path = os.path.join(tmpdir, "user_config.yaml")
        assert str(e.value) == f"This file('{config_file_path}') not found"


    def test_not_find_metadata_file(self, tmpdir, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(CodeGenerator, '__init__', lambda arg, root_dir: None)

        is_file_exist = False
        with pytest.raises(FileNotFoundError) as e:
            generator = CodeGenerator(None)
            generator.generate_file(None, tmpdir, False)
            is_file_exist = True

        assert is_file_exist == False
        metadata_file_path = os.path.join(tmpdir, "_metadata.json")
        assert str(e.value) == f"This file('{metadata_file_path}') not found"


    def test_not_find_template_script_file(self, tmpdir, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(CodeGenerator, '__init__', lambda arg, root_dir: None)
        dummy_metadata = {"script_file": "main.py"}
        metadata_file_path = os.path.join(tmpdir, "_metadata.json")
        write_json(metadata_file_path, dummy_metadata)

        is_file_exist = False
        with pytest.raises(FileNotFoundError) as e:
            generator = CodeGenerator(None)
            generator.root_dir = tmpdir
            generator.config = create_dummy_config()
            generator.generate_file(None, tmpdir, False)
            is_file_exist = True

        assert is_file_exist == False
        template_file_path = os.path.join(tmpdir, generator.config['Template']['FilePath'])
        assert str(e.value) == f"This file('{template_file_path}') not found"
