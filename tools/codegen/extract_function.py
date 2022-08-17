from typing import List, Tuple

import re
from collections import OrderedDict
from tools.codegen.variable_info import VariableInfo


class ExtractRenderParamError(Exception):
    pass


class ExtractFunction:
    @staticmethod
    def remove_blank_in_curly_brackets(line: str) -> str:
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

    @staticmethod
    def extract_varname_and_size(item: str) -> Tuple[str, str, str]:
        item_token = item.split("_", 1)
        if len(item_token) < 2:
            return item, "1", "1"
        var_name = item_token[0]
        elem_str = re.sub(r"[{}]", "", item_token[1])

        elem_token = elem_str.split(",")
        if len(elem_token) < 2:
            size_1d = elem_token[0]
            return var_name, size_1d, "1"
        else:
            size_1d = elem_token[0]
            size_2d = elem_token[1]
            return var_name, size_1d, size_2d

    @staticmethod
    def extract_variable_datatype(
        var_dict: dict, onecase_input_list: List[str]
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
            for key, vars in var_dict.items():
                begin_line, end_line = key
                # 複数行にまたがる変数がない場合
                if type(begin_line) == int and type(end_line) == int:
                    input_tokens = onecase_input_list[input_line].split()
                    input_line += 1
                    token_idx = 0
                    for var in vars:
                        # データ型格納
                        if token_idx < len(input_tokens):
                            var_num_dict[var.name] = input_tokens[token_idx]
                            var_datatype_dict[var.name] = datatype(
                                input_tokens[token_idx]
                            )
                        # 次の探索データまでインデックスを進める
                        if type(var.size_1d) == int:
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
                    for var in vars:
                        # データ型格納
                        if token_idx < len(input_tokens):
                            var_num_dict[var.name] = input_tokens[token_idx]
                            var_datatype_dict[var.name] = datatype(
                                input_tokens[token_idx]
                            )
                        # 次の探索データまでインデックスを進める
                        if type(var.size_2d) == int:
                            token_idx += var.size_2d
                        else:
                            token_idx += int(var_num_dict[var.size_2d])
        except KeyError:
            raise ExtractRenderParamError
        except IndexError:
            raise ExtractRenderParamError
        return var_datatype_dict

    @staticmethod
    def create_variable_dict(
        var_format_list: List[str], onecase_input_list: List[str]
    ) -> dict:
        # Extract variable info and appear line
        table_dict = OrderedDict()
        line_cnt = 0
        for line in var_format_list:
            for item in line.split():
                if "..." in item:
                    continue
                var_name, size_1d, size_2d = ExtractFunction.extract_varname_and_size(
                    item
                )
                # 日本語などの説明などは除外する
                if not var_name.isascii():
                    continue
                if var_name not in table_dict:
                    table_dict[var_name] = {
                        "begin": line_cnt,
                        "end": line_cnt + 1,
                        "var": VariableInfo(var_name, size_1d=size_1d, size_2d=size_2d),
                    }
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
            var_size_1d = value["var"].size_1d
            if begin_line + 1 < end_line:
                # 開始行の値がすでに辞書に登録されている場合は、更新値に反映させる
                # ex) 辞書が {6: 2 + N} で、(開始,終了,size_1d)が(6,10,M)の場合、{10: 2 + N + M} とする
                stack = "" if begin_line not in update_dict else update_dict[begin_line]
                if stack:
                    update_dict[end_line] = f"{stack} + {var_size_1d}"
                else:
                    update_dict[end_line] = f"{begin_line} + {var_size_1d}"

        for key in table_dict:
            if table_dict[key]["begin"] in update_dict:
                table_dict[key]["begin"] = update_dict[table_dict[key]["begin"]]
            if table_dict[key]["end"] in update_dict:
                table_dict[key]["end"] = update_dict[table_dict[key]["end"]]

        var_dict = OrderedDict()
        for value in table_dict.values():
            key = (value["begin"], value["end"])
            if key not in var_dict:
                var_dict[key] = []
            var_dict[key].append(value["var"])

        # Update variable datatype
        datatype_dict = ExtractFunction.extract_variable_datatype(
            var_dict, onecase_input_list
        )
        for key in var_dict:
            for i in range(len(var_dict[key])):
                var_dict[key][i].datatype = datatype_dict[var_dict[key][i].name]

        return var_dict

    @staticmethod
    def create_input_process_str(
        var_dict: dict, stdin_proc_code: str, tab_str: str = "    "
    ) -> str:
        input_proc_str = ""
        curr_indent = 1

        for vars in var_dict.values():
            # 配列初期化コード
            for var in vars:
                # scalar
                if var.size_1d == 1:
                    pass
                # 1d list
                elif var.size_2d == 1:
                    list_name = f"{var.name}_list"
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += f"{list_name} = [None] * {var.size_1d}\n"
                # 2d list
                else:
                    list_name = f"{var.name}_list"
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += (
                        f"{list_name} = [[] * i for i in range({var.size_1d})]\n"
                    )

            for_cnt = 0
            for var in vars:
                # scalar
                if var.size_1d == 1:
                    # inputコード
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += (
                        f"{var.name} = {var.datatype}({stdin_proc_code})\n"
                    )
                # 1d list
                elif var.size_2d == 1:
                    # for文コード
                    if for_cnt < 1:
                        input_proc_str += tab_str * curr_indent
                        input_proc_str += f"for i in range({var.size_1d}):\n"
                        curr_indent += 1
                        for_cnt = 1
                    # inputコード
                    list_name = f"{var.name}_list"
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += (
                        f"{var.name} = {var.datatype}({stdin_proc_code})\n"
                    )
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += f"{list_name}[i] = {var.name}\n"
                # 2d list
                else:
                    # for文コード
                    if for_cnt < 1:
                        input_proc_str += tab_str * curr_indent
                        input_proc_str += f"for i in range({var.size_1d}):\n"
                        curr_indent += 1
                        input_proc_str += tab_str * curr_indent
                        input_proc_str += f"for j in range({var.size_2d}):\n"
                        curr_indent += 1
                        for_cnt = 2
                    elif for_cnt < 2:
                        input_proc_str += tab_str * curr_indent
                        input_proc_str += f"for j in range({var.size_2d}):\n"
                        curr_indent += 1
                        for_cnt = 2

                    # inputコード
                    list_name = f"{var.name}_list"
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += (
                        f"{var.name} = {var.datatype}({stdin_proc_code})\n"
                    )
                    input_proc_str += tab_str * curr_indent
                    input_proc_str += f"{list_name}[i].append({var.name})\n"

            # for文のインデント数デクリメント
            curr_indent -= for_cnt
        return input_proc_str.strip()

    @staticmethod
    def create_solve_argument_str(var_dict: dict) -> str:
        varname = (
            lambda v: v.name if v.size_1d == 1 and v.size_2d == 1 else v.name + "_list"
        )
        solve_arg_str = ", ".join(
            [varname(value) for values in var_dict.values() for value in values]
        )
        return solve_arg_str
