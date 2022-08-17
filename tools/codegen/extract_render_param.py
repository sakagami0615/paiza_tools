from typing import Tuple

import re
from collections import defaultdict
from tools.codegen.extract_function import ExtractFunction
from tools.codegen.variable_checker import VariableChecker
from tools.scraping.question_content import QuestionContent

from tools.codegen.extract_function import ExtractRenderParamError


class ExtractRenderParam:
    def __init__(self, config: dict, content: QuestionContent):
        self.config = config
        self.content = content

    def _extract_const_yes(self) -> Tuple[bool, str]:
        match_result = re.search(r"yes", self.content.excepted_output, re.IGNORECASE)
        if match_result:
            return True, match_result.group(0)
        return False, ""

    def _extract_const_no(self) -> Tuple[bool, str]:
        match_result = re.search(r"no", self.content.excepted_output, re.IGNORECASE)
        if match_result:
            return True, match_result.group(0)
        return False, ""

    def _extract_code(self):
        # 変数抽出用の入力を用意
        var_format = ExtractFunction.remove_blank_in_curly_brackets(
            self.content.var_format
        )
        var_format_list = var_format.split("\n")

        # 変数情報を格納した辞書を作成
        onecase_input_list = (
            []
            if self.content.n_test_cases == 0
            else self.content.input_list[0].split("\n")
        )
        var_dict = ExtractFunction.create_variable_dict(
            var_format_list, onecase_input_list
        )

        # 変数情報の不整合確認
        if not VariableChecker().check_variable_dict(var_dict):
            raise ExtractRenderParamError

        # 標準入力取得処理コードとsolve関数の引数コードを取得
        solve_arg_str = ExtractFunction.create_solve_argument_str(var_dict)
        input_process_str = ExtractFunction.create_input_process_str(
            var_dict, self.config["Template"]["StdinProcCode"], self.config["TabString"]
        )
        return input_process_str, solve_arg_str

    def extract_param_dict(self) -> dict:
        try:
            is_yes_str, yes_str = self._extract_const_yes()
            is_no_str, no_str = self._extract_const_no()
            input_process, solve_args = self._extract_code()

            render_param_dict = {
                "extract_success": True,
                "is_yes_str": is_yes_str,
                "is_no_str": is_no_str,
                "yes_str": yes_str,
                "no_str": no_str,
                "input_process": input_process,
                "solve_argument": solve_args,
            }
            return render_param_dict

        except ExtractRenderParamError:
            return defaultdict(str)
