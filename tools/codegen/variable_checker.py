class VariableChecker:
    def __init__(self):
        pass

    def __check_datatype_enable(self, var_dict: dict):
        for vars in var_dict.values():
            for var in vars:
                if var.datatype in ["int", "float", "str"]:
                    return False
        return True

    def __check_element_size_match(self, var_dict: dict):
        # 同じ列の入力データの変数の要素数が会っているかを確認
        # ex) x[0], y[0]
        #     ...   ...
        #     x[N], y[N] みたいに揃っているかを確認する
        for vars in var_dict.values():
            if len(vars) < 2:
                continue
            base_size_1d = vars[0].size_1d
            for var in vars:
                if var.size_id != base_size_1d:
                    return False
        return True

    def __check_element_variable_match(self, var_dict: dict):
        # 要素指定に使われている変数が定義されているかを確認
        var_set = set()
        for vars in var_dict.values():
            for var in vars:
                var_set.add(var.name)
                if type(var.size_1d) == str and var.size_1d in var_set:
                    return False
                if type(var.size_2d) == str and var.size_2d in var_set:
                    return False
        return True

    def check_variable_dict(self, var_dict: dict) -> bool:
        results = [
            self.__check_datatype_enable(var_dict),
            self.__check_element_size_match(var_dict),
            self.__check_element_variable_match(var_dict),
        ]
        result = False if False in results else True
        return result
