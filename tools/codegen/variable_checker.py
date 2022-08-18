import re


class VariableChecker:
    def __init__(self):
        pass

    def _check_datatype_enable(self, var_dict: dict):
        for var_list in var_dict.values():
            for var in var_list:
                if var.datatype not in ["int", "float", "str"]:
                    return False
        return True

    def _check_element_size_enable(self, var_dict: dict):

        for key, var_list in var_dict.items():
            begin_line, end_line = key

            # 要素数が定数の時のチェック
            if isinstance(begin_line, int) and isinstance(end_line, int):
                line_size = end_line - begin_line

            # 要素数に変数を使用しているの時のチェック
            else:
                end_line = str(end_line)
                pattern = re.sub("([+-])", r"[\1]", str(begin_line))
                match = re.search(f"^{pattern}", end_line)
                if match:
                    # <pattern> + [""|"+"|"-"] の文字を削除する
                    line_size = re.sub(pattern, "", end_line, 1).strip()
                    line_size = re.sub("([+-])", "", line_size, 1).strip()
                    line_size = line_size if not line_size.isdigit() else int(line_size)
                else:
                    line_size = end_line

            for var in var_list:
                if isinstance(line_size, int):
                    enable_flg = (
                        (var.size_2d == line_size)
                        if line_size == 1
                        else (var.size_1d == line_size)
                    )
                    if not enable_flg:
                        return False
                else:
                    if var.size_1d != line_size:
                        return False
        return True

    def _check_element_size_match(self, var_dict: dict):
        # 同じ列の入力データの変数の要素数が会っているかを確認
        # ex) x[0], y[0]
        #     ...   ...
        #     x[N], y[N] みたいに揃っているかを確認する
        for var_list in var_dict.values():
            if len(var_list) < 2:
                continue
            base_size_1d = var_list[0].size_1d
            for var in var_list:
                if var.size_1d != base_size_1d:
                    return False
        return True

    def _check_element_variable_match(self, var_dict: dict):
        # 要素指定に使われている変数が定義されているかを確認
        var_set = set()

        # size_Nd内にあるは変数を取得
        def get_var_list(var_size):
            var_list = []
            if isinstance(var_size, str):
                for elem in re.split(r"\s[+-]\s", var_size):
                    if not elem.isdigit():
                        var_list.append(elem)
            return var_list

        for var_list in var_dict.values():
            for var in var_list:
                var_set.add(var.name)
                for elem in get_var_list(var.size_1d) + get_var_list(var.size_2d):
                    if elem not in var_set:
                        return False
        return True

    def check_variable_dict(self, var_dict: dict) -> bool:
        results = [
            self._check_datatype_enable(var_dict),
            self._check_element_size_enable(var_dict),
            self._check_element_size_match(var_dict),
            self._check_element_variable_match(var_dict),
        ]
        return all(results)
