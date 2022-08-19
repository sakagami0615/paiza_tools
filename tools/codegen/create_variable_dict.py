import re
from collections import OrderedDict
from typing import List, Tuple, Union

from tools.codegen.variable_info import VariableInfo


class ExtractRenderParamError(Exception):
    def __init__(self):
        message = "Failed to extract data required for code generation."
        super().__init__(message)


class CreateVariableDict:
    def __init__(self):
        pass

    def _extract_varname_and_size(self, item: str) -> Tuple[str, str, str]:
        item_token = item.split("_", 1)
        if len(item_token) < 2:
            return item.strip(), "1", "1"
        var_name = item_token[0].strip()
        elem_str = re.sub(r"[{}]", "", item_token[1])

        elem_token = elem_str.split(",")
        if len(elem_token) < 2:
            size_1d = elem_token[0].strip()
            return var_name, size_1d, "1"

        size_1d = elem_token[0].strip()
        size_2d = elem_token[1].strip()
        return var_name, size_1d, size_2d

    def _create_variable_table_dict(self, var_format_list: List[str]) -> dict:
        # Extract variable info and appear line
        table_dict = OrderedDict()
        line_cnt = 0
        for line in var_format_list:
            for item in line.split():
                if "..." in item:
                    continue
                var_name, size_1d, size_2d = self._extract_varname_and_size(item)
                # 日本語などの説明などは除外する
                if not var_name.isascii():
                    continue
                # 初回登場の変数登録
                if var_name not in table_dict:
                    table_dict[var_name] = {
                        "appear_cnt": 1,
                        "format_line_begin": line_cnt,
                        "format_line_end": line_cnt + 1,
                        "var": VariableInfo(var_name, size_1d=size_1d, size_2d=size_2d),
                    }
                # 初回以降の登場変数の情報更新
                else:
                    table_dict[var_name]["appear_cnt"] += 1
                    table_dict[var_name]["format_line_end"] = line_cnt + 1
                    table_dict[var_name]["var"].size_1d = size_1d
                    table_dict[var_name]["var"].size_2d = size_2d
            line_cnt += 1

        return table_dict

    def _create_variable_appear_dict(self, table_dict: dict) -> dict:
        var_size_info_dict = OrderedDict()
        update_key_dict = OrderedDict()
        for value in table_dict.values():
            key = (value["format_line_begin"], value["format_line_end"])
            if key not in var_size_info_dict:
                var_size_info_dict[key] = []

            var_size_info_dict[key].append(
                {
                    "var_name": value["var"].name,
                    "var_size_1d": value["var"].size_1d,
                    "var_size_2d": value["var"].size_2d,
                }
            )
            update_key_dict[key] = {
                "update_begin": value["format_line_begin"],
                "update_end": value["format_line_end"],
                "n_lines": value["format_line_end"] - value["format_line_begin"],
            }

        # 配列の要素数(定数)の情報をキーに反映
        # ex) {(0, 1), [a[3], b[3]} の時に {(0, 3), [a[3], b[3]} のように更新する
        stack_line_cnt = 0
        for key, var_list in var_size_info_dict.items():
            # begin の更新
            update_key_dict[key]["update_begin"] += stack_line_cnt

            # 変数が一つの場合は、行を跨いで入力を取得しない配列のため対象外となる
            # ex) {(0, 1), [a[3]} の時は "1 2 3" のように1行からデータを取得するため
            curr_n_lines = var_list[0]["var_size_1d"]
            prev_n_lines = update_key_dict[key]["n_lines"]
            if (
                isinstance(curr_n_lines, int)
                and len(var_list) > 1
                and curr_n_lines != prev_n_lines
            ):
                # stack値と n_lines の更新
                stack_line_cnt += curr_n_lines - prev_n_lines
                update_key_dict[key]["n_lines"] = curr_n_lines

            # end の更新
            update_key_dict[key]["update_end"] += stack_line_cnt

        # 配列の要素数(変数)の情報をキーに反映
        # ex) {(0, 1), [a[M], b[M]} の時に {(0, M), [a[M], b[M]} のように更新する
        stack_elem = ""
        for key, var_list in var_size_info_dict.items():
            # begin の更新
            if stack_elem:
                update_key_dict[key]["update_begin"] = stack_elem

            # stack_elem がなく、現在見ている変数(配列)の要素数が定数の場合は、対象外となる
            # stack_elem がない場合は、最初に登場する変数要素を探している状態。
            # stack_elem に変数を候補した要素が格納されたら、以降に登場する配列の要素数を更新していく。
            size_1d = var_list[0]["var_size_1d"]
            if stack_elem or isinstance(size_1d, str):
                curr_begin = update_key_dict[key]["update_begin"]
                stack_elem = f"{curr_begin} + {size_1d}"
                # end と n_lines の更新
                update_key_dict[key]["update_end"] = stack_elem
                update_key_dict[key]["n_lines"] = size_1d

        appear_dict = OrderedDict()
        for value in table_dict.values():
            prev_key = (value["format_line_begin"], value["format_line_end"])
            update_key = (
                update_key_dict[prev_key]["update_begin"],
                update_key_dict[prev_key]["update_end"],
                update_key_dict[prev_key]["n_lines"],
            )

            if update_key not in appear_dict:
                appear_dict[update_key] = []
            appear_dict[update_key].append(value["var"])

        return appear_dict

    def _get_datatype(self, element: str) -> str:
        for func in [int, float]:
            try:
                return type(func(element)).__name__
            except ValueError:
                pass
        return "str"

    def _replace_var_str2int(self, line: str, var_num_dict: dict) -> int:
        # 定数変数を数値に置き換える
        item_list = re.split(r"\s*[-+]\s*", line)
        value = 0
        for item in item_list:
            if self._get_datatype(item) == "int":
                value += int(item)
            else:
                value += int(var_num_dict[item])
        return value

    def _create_variable_datatype_dict(
        self, appear_dict: dict, onecase_input_list: List[str]
    ) -> dict:
        var_datatype_dict = {}
        var_num_dict = {}

        # 辞書にデータ型を格納
        def update_var_dict(
            input_tokens: List[str], token_idx: int, var_name: str
        ) -> int:
            # データ型格納
            if token_idx < len(input_tokens):
                var_num_dict[var_name] = input_tokens[token_idx]
                var_datatype_dict[var_name] = self._get_datatype(
                    input_tokens[token_idx]
                )

        # 変数データをint型数値として返却
        def get_var_integer(var_data: Union[int, str]) -> int:
            if isinstance(var_data, int):
                return var_data
            return int(var_num_dict[var_data])

        try:
            input_line = 0
            for key, var_list in appear_dict.items():
                begin_line, end_line, n_lines = key
                token_idx = 0

                # 複数行にまたがる変数がない場合
                if n_lines == 1:
                    for var in var_list:
                        # 該当の入力データを取得
                        input_tokens = onecase_input_list[input_line].split()
                        # 更新
                        update_var_dict(input_tokens, token_idx, var.name)
                        token_idx += get_var_integer(var.size_1d)
                        if token_idx >= len(input_tokens):
                            input_line += token_idx - len(input_tokens) + 1

                # 複数行にまたがる変数がある場合
                else:
                    # 該当の入力データを取得
                    begin_line = self._replace_var_str2int(
                        str(begin_line), var_num_dict
                    )
                    end_line = self._replace_var_str2int(str(end_line), var_num_dict)
                    input_tokens = onecase_input_list[input_line].split()
                    input_line += end_line - begin_line
                    # 更新
                    for var in var_list:
                        update_var_dict(input_tokens, token_idx, var.name)
                        token_idx += get_var_integer(var.size_2d)

        except KeyError as exc:
            raise ExtractRenderParamError from exc
        except IndexError as exc:
            raise ExtractRenderParamError from exc
        return var_datatype_dict

    def _update_datatype_in_variable_appear_dict(
        self, appear_dict: dict, datatype_dict: dict
    ) -> None:
        # Update variable datatype
        for key in appear_dict:
            for i in range(len(appear_dict[key])):
                appear_dict[key][i].datatype = datatype_dict[appear_dict[key][i].name]
        return appear_dict

    def create_dict(
        self, var_format_list: List[str], onecase_input_list: List[str]
    ) -> dict:
        table_dict = self._create_variable_table_dict(var_format_list)
        appear_dict = self._create_variable_appear_dict(table_dict)
        datatype_dict = self._create_variable_datatype_dict(
            appear_dict, onecase_input_list
        )
        self._update_datatype_in_variable_appear_dict(appear_dict, datatype_dict)
        return appear_dict
