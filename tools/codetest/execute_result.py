from enum import Enum
from typing import Tuple

from tools.common.color_code import ColorCode


class ResultType(Enum):
    AC = 1
    WA = 2
    RE = 3


class ExecuteResult:

    GREEN = "\033[093m{}\033[0m"
    YELLOW = "\033[092m{}\033[0m"
    RED = "\033[091m{}\033[0m"
    BLUE = "\033[094m{}\033[0m"

    def __init__(self):
        pass

    def _get_result_type(
        self, returncode: int, stdout: str, output_text: str
    ) -> ResultType:
        if returncode != 0:
            result = ResultType.RE
        elif stdout != output_text:
            result = ResultType.WA
        else:
            result = ResultType.AC
        return result

    def output_result(
        self,
        input_file_name: str,
        input_text: str,
        output_text: str,
        returncode: int,
        stdout: str,
    ) -> Tuple[bool, str]:
        result_state = self._get_result_type(returncode, stdout, output_text)

        if result_state == ResultType.AC:
            result_message = "#" + input_file_name + " ... "
            result_message += ColorCode.GREEN.format("AC")
            is_correct = True
        elif result_state == ResultType.WA:
            result_message = "#" + input_file_name + " ... "
            result_message += ColorCode.YELLOW.format("WA") + "\n"
            result_message += ColorCode.BLUE.format("[Input]\n")
            result_message += f"{input_text}\n"
            result_message += ColorCode.BLUE.format("[Expected]\n")
            result_message += f"{output_text}\n"
            result_message += ColorCode.BLUE.format("[YourResult]\n")
            result_message += f"{stdout}\n\n"
            is_correct = False
        else:
            result_message = "#" + input_file_name + " ... "
            result_message += ColorCode.RED.format("RE") + "\n"
            result_message += ColorCode.BLUE.format("[Input]\n")
            result_message += f"{input_text}\n"
            result_message += ColorCode.BLUE.format("[Expected]\n")
            result_message += f"{output_text}\n"
            result_message += ColorCode.BLUE.format("[YourResult(Traceback)]\n")
            result_message += f"{stdout}\n\n"
            is_correct = False

        return is_correct, result_message
