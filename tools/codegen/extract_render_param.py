import re
from collections import defaultdict
from typing import Tuple

from tools.codegen.create_process_code import CreateProcessCode
from tools.codegen.create_variable_dict import (
    CreateVariableDict,
    ExtractRenderParamError,
)
from tools.codegen.variable_checker import VariableChecker
from tools.scraping.question_content import QuestionContent


class ExtractRenderParam:
    def __init__(self, config: dict, content: QuestionContent):
        self.content = content
        self.coder = CreateProcessCode(config)

    def _remove_blank_in_curly_brackets(self, line: str) -> str:
        result_line = ""
        in_curly_bracket = False
        for s in line:
            if s == "{":
                in_curly_bracket = True
            elif s == "}":
                in_curly_bracket = False
            if in_curly_bracket and (s == " "):
                continue
            result_line += s
        return result_line

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

    def _extract_variable_dict(self) -> dict:
        """問題文の入力フォーマットから変数情報を抽出し、辞書を作成する

        Example:
            この関数で作成する variable_dict は以下のようなデータ型となっている
            ================================================================
            var_dict = OrderedDict([
                ((0, 1),                 [<tools.codegen.variable_info.VariableInfo object at 0x10b4ca700>,
                                          <tools.codegen.variable_info.VariableInfo object at 0x10b4ca6d0>]),
                ((1, 2),                 [<tools.codegen.variable_info.VariableInfo object at 0x10b4ca910>,
                                          <tools.codegen.variable_info.VariableInfo object at 0x10b4ca8e0>]),
                ((2, '2 + M'),           [<tools.codegen.variable_info.VariableInfo object at 0x10b4ca820>]),
                (('2 + M', '2 + M + N'), [<tools.codegen.variable_info.VariableInfo object at 0x10b4ca8b0>,
                                          <tools.codegen.variable_info.VariableInfo object at 0x10b4caa30>])
            ])
            ================================================================
            key情報: (変数が登場する行, 変数が登場しなくなる行)
            value情報: [登場する変数の情報, ...]

        Raises:
            ExtractRenderParamError: _description_

        Returns:
            dict: _description_
        """
        # 変数抽出用の入力を用意
        var_format = self._remove_blank_in_curly_brackets(self.content.var_format)
        var_format_list = var_format.split("\n")

        # 変数情報を格納した辞書を作成
        onecase_input_list = (
            []
            if self.content.n_test_cases == 0
            else self.content.input_list[0].split("\n")
        )
        var_dict = CreateVariableDict().create_dict(var_format_list, onecase_input_list)

        # 変数情報の不整合確認
        if not VariableChecker().check_variable_dict(var_dict):
            raise ExtractRenderParamError

        return var_dict

    def extract_param_dict(self) -> dict:
        try:
            is_yes_str, yes_str = self._extract_const_yes()
            is_no_str, no_str = self._extract_const_no()
            var_dict = self._extract_variable_dict()
            solve_args = self.coder.create_solve_argument_code(var_dict)
            input_process = self.coder.create_input_process_code(var_dict)

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
