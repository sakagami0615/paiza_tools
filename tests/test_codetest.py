import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.codetest.execute_code import ExecuteCode
from tools.codetest.execute_result import ResultType
from tools.common.file_function import write_json, write_text

TAB = "    "


def create_dummy_script_code(args: str, in_process: str) -> str:

    code = """
import sys


def solve({}):
    pass


def main():
    def stdin_iter():
        for stdin in sys.stdin:
            for item_str in stdin.split():
                print(item_str)
                yield item_str
    iter_var = stdin_iter()
    {}
    solve({})


if __name__ == '__main__':
    main()
""".format(args, in_process, args)
    return code


def create_dummy_metadata() -> dict:
    return {
        "script_file": "main.py",
        "n_test_cases": 1,
        "input_file_format": "_in_{}.txt",
        "output_file_format": "_out_{}.txt"
    }

def create_codetest_env(tmpdir: str, solve_args: str, input_process: str, input_text: str, output_text: str) -> None:
    metadata = create_dummy_metadata()
    write_json(os.path.join(tmpdir, "_metadata.json"), metadata)
    write_text(os.path.join(tmpdir, metadata["script_file"]), create_dummy_script_code(solve_args, input_process))
    write_text(os.path.join(tmpdir, metadata["input_file_format"].format(1)), input_text)
    write_text(os.path.join(tmpdir, metadata["output_file_format"].format(1)), output_text)


class TestCodeTest:

    def test_correct_result_success(self, tmpdir):
        solve_args = "a_list"
        input_process  = f"a_list = [None] * 3\n{TAB}"
        input_process += f"for i in range(3):\n{TAB * 2}"
        input_process += f"a = int(next(iter_var))\n{TAB * 2}"
        input_process +=  "a_list[i] = a"

        input_text = "1 2 3"
        output_text = "\n".join(input_text.split())

        create_codetest_env(tmpdir, solve_args, input_process, input_text, output_text)

        is_correct, result_state, _ = ExecuteCode(tmpdir)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == True


    def test_correct_result_failure(self, tmpdir):
        solve_args = "a_list"
        input_process  = f"a_list = [None] * 3\n{TAB}"
        input_process += f"for i in range(3):\n{TAB * 2}"
        input_process += f"a = int(next(iter_var))\n{TAB * 2}"
        input_process +=  "a_list[i] = a"

        input_text = "1 2 3"
        output_text = "dummy_output"

        create_codetest_env(tmpdir, solve_args, input_process, input_text, output_text)

        is_correct, result_state, _ = ExecuteCode(tmpdir)._run_one_case(0)
        assert result_state != ResultType.RE
        assert is_correct == False


    def test_rte_list_size_not_match(self, tmpdir):
        solve_args = "a_list"
        input_process  = f"a = [None] * 4\n{TAB}"
        input_process += f"for i in range(4)\n{TAB * 2}"
        input_process += f"a = int(input())\n{TAB * 2}"
        input_process +=  "a_list[i] = a"

        input_text = "1 2 3"
        output_text = "\n".join(input_text.split())

        create_codetest_env(tmpdir, solve_args, input_process, input_text, output_text)

        _, result_state, _ = ExecuteCode(tmpdir)._run_one_case(0)
        assert result_state == ResultType.RE
