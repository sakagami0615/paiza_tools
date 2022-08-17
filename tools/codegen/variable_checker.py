class VariableChecker:
    def __init__(self):
        pass

    def _check_datatype_enable(self, var_dict: dict):
        for var_list in var_dict.values():
            for var in var_list:
                if var.datatype not in ["int", "float", "str"]:
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
        for var_list in var_dict.values():
            for var in var_list:
                var_set.add(var.name)
                if isinstance(var.size_1d, str) and var.size_1d not in var_set:
                    return False
                if isinstance(var.size_2d, str) and var.size_2d not in var_set:
                    return False
        return True

    def check_variable_dict(self, var_dict: dict) -> bool:
        results = [
            self._check_datatype_enable(var_dict),
            self._check_element_size_match(var_dict),
            self._check_element_variable_match(var_dict),
        ]
        return all(results)
