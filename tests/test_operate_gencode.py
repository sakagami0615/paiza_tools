import os
import sys
from typing import Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.test_codegen import create_dummy_config
from tests.test_codetest import create_codetest_env, create_dummy_script_code
from tools.codegen.extract_render_param import ExtractRenderParam
from tools.codetest.execute_code import ExecuteCode
from tools.codetest.execute_result import ResultType
from tools.common.file_function import read_json, write_text
from tools.envgen.envfile_generator import EnvFileGenerator
from tools.scraping.question_content import QuestionContent

TAB = "    "


def generate_dummy_env(ques_number: str, var_format: str, input_text: str, tmpdir: str) -> Tuple[str, QuestionContent]:
    answer_text = "\n".join(input_text.split())
    content = QuestionContent('dummy_html', ques_number, 'dummy_sentence',
                              var_format, 'dummy_output', 'dummy_condition',
                              1, [input_text], [answer_text])
    EnvFileGenerator().generate_file(content, tmpdir, True)
    return os.path.join(tmpdir, ques_number), content


class TestOperateGenCode:

    def test_scalar_var(self, tmpdir):
        # Env Generation
        var_format = "a b c"
        input_text = "1 1.1 abc"
        dir_path, content = generate_dummy_env("T001", var_format, input_text, tmpdir)
        metadata_file_path = os.path.join(dir_path, "_metadata.json")
        metadata = read_json(metadata_file_path)

        # Code Generation
        config = create_dummy_config()
        render_param_dict = ExtractRenderParam(config, content).extract_param_dict()

        script_file_path = os.path.join(dir_path, metadata["script_file"])
        render_code = create_dummy_script_code(render_param_dict["solve_argument"],
                                               render_param_dict["input_process"])
        write_text(script_file_path, render_code)

        # Test
        is_correct, result_state, _ = ExecuteCode(dir_path)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == True


    def test_list_horizontal_1d_var(self, tmpdir):
        # Env Generation
        var_format = ("N\n"
                      "a_1 a_2 ... a_N\n"
                      "b_1 b_2 ... b_N\n"
                      "c_1 c_2 ... c_N")
        input_text = ("4\n"
                      "1 2 3 4\n"
                      "1.1 2.2 3.3 4.4\n"
                      "a bb ccc dddd")
        dir_path, content = generate_dummy_env("T002", var_format, input_text, tmpdir)
        metadata_file_path = os.path.join(dir_path, "_metadata.json")
        metadata = read_json(metadata_file_path)

        # Code Generation
        config = create_dummy_config()
        render_param_dict = ExtractRenderParam(config, content).extract_param_dict()

        script_file_path = os.path.join(dir_path, metadata["script_file"])
        render_code = create_dummy_script_code(render_param_dict["solve_argument"],
                                               render_param_dict["input_process"])
        write_text(script_file_path, render_code)

        # Test
        is_correct, result_state, _ = ExecuteCode(dir_path)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == True


    def test_list_vertical_1d_var(self, tmpdir):
        # Env Generation
        var_format = ("N\n"
                      "a_1 ... a_N\n"
                      "b_1 ... b_N\n"
                      "c_1 ... c_N")
        input_text = ("2\n"
                      "1\n2\n"
                      "1.1\n2.2\n"
                      "a\nbb")
        dir_path, content = generate_dummy_env("T003", var_format, input_text, tmpdir)
        metadata_file_path = os.path.join(dir_path, "_metadata.json")
        metadata = read_json(metadata_file_path)

        # Code Generation
        config = create_dummy_config()
        render_param_dict = ExtractRenderParam(config, content).extract_param_dict()

        script_file_path = os.path.join(dir_path, metadata["script_file"])
        render_code = create_dummy_script_code(render_param_dict["solve_argument"],
                                               render_param_dict["input_process"])
        write_text(script_file_path, render_code)

        # Test
        is_correct, result_state, _ = ExecuteCode(dir_path)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == True


    def test_list_2d_var(self, tmpdir):
        # Env Generation
        var_format = ("M N\n"
                      "a_{1,1} ... a_{1,M}\n"
                      "...\n"
                      "a_{N,1} ... a_{N,M}\n"
                      "b_{1,1} ... b_{1,M}\n"
                      "...\n"
                      "b_{N,1} ... b_{N,M}\n"
                      "c_{1,1} ... c_{1,M}\n"
                      "...\n"
                      "c_{N,1} ... c_{N,M}")
        input_text = ("4 2\n"
                      "1 2 3 4\n"
                      "5 6 7 8\n"
                      "1.1 2.2 3.3 4.4\n"
                      "5.5 6.6 7.7 8.8\n"
                      "a bb ccc dddd\n"
                      "aa bbb cccc ddddd")

        dir_path, content = generate_dummy_env("T004", var_format, input_text, tmpdir)
        metadata_file_path = os.path.join(dir_path, "_metadata.json")
        metadata = read_json(metadata_file_path)

        # Code Generation
        config = create_dummy_config()
        render_param_dict = ExtractRenderParam(config, content).extract_param_dict()

        script_file_path = os.path.join(dir_path, metadata["script_file"])
        render_code = create_dummy_script_code(render_param_dict["solve_argument"],
                                               render_param_dict["input_process"])
        write_text(script_file_path, render_code)
        # Test
        is_correct, result_state , _= ExecuteCode(dir_path)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == True


    def test_string_with_spaces_failure(self, tmpdir):
        # ※空白を含む文字列は本ツールの対象外
        # ※コード生成失敗として、空のmain.pyを生成する仕掛けにしている
        # Env Generation
        var_format = ("M N\n"
                      "S")
        input_text = ("4 1\n"
                      "a bb ccc dddd")
        dir_path, content = generate_dummy_env("T001", var_format, input_text, tmpdir)
        metadata_file_path = os.path.join(dir_path, "_metadata.json")
        metadata = read_json(metadata_file_path)

        # Code Generation
        config = create_dummy_config()
        render_param_dict = ExtractRenderParam(config, content).extract_param_dict()

        script_file_path = os.path.join(dir_path, metadata["script_file"])
        render_code = create_dummy_script_code(render_param_dict["solve_argument"],
                                               render_param_dict["input_process"])
        write_text(script_file_path, render_code)

        # Test
        is_correct, result_state, _ = ExecuteCode(dir_path)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == False
