class CreateProcessCode:
    def __init__(self, config):
        self.config = config

    def create_solve_argument_code(self, var_dict: dict) -> str:
        def varname(v):
            return v.name if v.size_1d == 1 and v.size_2d == 1 else v.name + "_list"

        solve_arg_code = ", ".join(
            [varname(value) for values in var_dict.values() for value in values]
        )
        return solve_arg_code

    def create_input_process_code(self, var_dict: dict) -> str:
        stdin_proc_code = self.config["Template"]["StdinProcCode"]
        tab_str = self.config["TabString"]

        input_proc_str = ""
        curr_indent = 1

        for var_list in var_dict.values():
            # 配列初期化コード
            for var in var_list:
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
            for var in var_list:
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
