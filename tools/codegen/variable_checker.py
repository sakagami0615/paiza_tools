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
            n_lines = key[-1]
            for var in var_list:
                if isinstance(n_lines, int):
                    enable_flg = (
                        (var.size_2d == n_lines)
                        if n_lines == 1
                        else (var.size_1d == n_lines)
                    )
                    if not enable_flg:
                        return False
                else:
                    if var.size_1d != n_lines:
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
            size_set = set()
            for var in var_list:
                # スカラ変数は対象外
                if var.size_1d == 1:
                    continue
                size_set.add(var.size_1d)

            if len(size_set) > 1:
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
