import re
from collections import OrderedDict
from typing import List, Tuple

from tools.codegen.variable_info import VariableInfo


class ExtractRenderParamError(Exception):
    pass


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
                        "begin": line_cnt,
                        "end": line_cnt + 1,
                        "var": VariableInfo(var_name, size_1d=size_1d, size_2d=size_2d),
                    }
                # 初回以降の登場変数の情報更新
                else:
                    table_dict[var_name]["end"] = line_cnt + 1
                    table_dict[var_name]["var"].size_1d = size_1d
                    table_dict[var_name]["var"].size_2d = size_2d
            line_cnt += 1

        # Update appear line
        update_dict = {}
        for value in table_dict.values():
            begin_line = value["begin"]
            end_line = value["end"]
            size_1d = value["var"].size_1d
            if begin_line + 1 < end_line:
                # 開始行の値がすでに辞書に登録されている場合は、更新値に反映させる
                # ex) 辞書が {6: 2 + N} で、(開始,終了,size_1d)が(6,10,M)の場合、{10: 2 + N + M} とする
                stack = "" if begin_line not in update_dict else update_dict[begin_line]
                if stack:
                    update_dict[end_line] = f"{stack} + {size_1d}"
                else:
                    update_dict[end_line] = f"{begin_line} + {size_1d}"

        for key in table_dict:
            if table_dict[key]["begin"] in update_dict:
                table_dict[key]["begin"] = update_dict[table_dict[key]["begin"]]
            if table_dict[key]["end"] in update_dict:
                table_dict[key]["end"] = update_dict[table_dict[key]["end"]]

        return table_dict

    def _create_variable_appear_dict(self, table_dict: dict) -> dict:
        appear_dict = OrderedDict()
        for value in table_dict.values():
            key = (value["begin"], value["end"])
            if key not in appear_dict:
                appear_dict[key] = []
            appear_dict[key].append(value["var"])
        return appear_dict

    def _create_variable_datatype_dict(
        self, appear_dict: dict, onecase_input_list: List[str]
    ) -> dict:
        var_datatype_dict = {}
        var_num_dict = {}

        def datatype(element: str) -> str:
            for func in [int, float]:
                try:
                    return type(func(element)).__name__
                except ValueError:
                    pass
            return "str"

        try:
            input_line = 0
            for key, var_list in appear_dict.items():
                begin_line, end_line = key
                # 複数行にまたがる変数がない場合
                if isinstance(begin_line, int) and isinstance(end_line, int):
                    input_tokens = onecase_input_list[input_line].split()
                    input_line += 1
                    token_idx = 0
                    for var in var_list:
                        # データ型格納
                        if token_idx < len(input_tokens):
                            var_num_dict[var.name] = input_tokens[token_idx]
                            var_datatype_dict[var.name] = datatype(
                                input_tokens[token_idx]
                            )
                        # 次の探索データまでインデックスを進める
                        if isinstance(var.size_1d, int):
                            token_idx += var.size_1d
                        else:
                            token_idx += int(var_num_dict[var.size_1d])
                # 複数行にまたがる変数がある場合
                else:
                    # 定数変数を数値に置き換える
                    begin_list = re.split(r"\s*[-+]\s*", str(begin_line))
                    end_list = re.split(r"\s*[-+]\s*", str(end_line))
                    begin_line = 0
                    for item in begin_list:
                        if datatype(item) == "int":
                            begin_line += int(item)
                        else:
                            begin_line += int(var_num_dict[item])
                    end_line = 0
                    for item in end_list:
                        if datatype(item) == "int":
                            end_line += int(item)
                        else:
                            end_line += int(var_num_dict[item])

                    input_tokens = onecase_input_list[input_line].split()
                    input_line += end_line - begin_line
                    token_idx = 0
                    for var in var_list:
                        # データ型格納
                        if token_idx < len(input_tokens):
                            var_num_dict[var.name] = input_tokens[token_idx]
                            var_datatype_dict[var.name] = datatype(
                                input_tokens[token_idx]
                            )
                        # 次の探索データまでインデックスを進める
                        if isinstance(var.size_2d, int):
                            token_idx += var.size_2d
                        else:
                            token_idx += int(var_num_dict[var.size_2d])
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
