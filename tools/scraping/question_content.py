from typing import List, Optional

from itertools import zip_longest


class QuestionContent:
    def __init__(
        self,
        html: str,
        ques_number: str,
        ques_sentence: str,
        var_format: Optional[str],
        excepted_output: Optional[str],
        condition: Optional[str],
        n_test_cases: int,
        input_list: List[str],
        answer_list: List[str],
    ):

        self.html = html
        self.ques_number = ques_number
        self.ques_sentence = ques_sentence
        self.var_format = var_format
        self.excepted_output = excepted_output
        self.condition = condition
        self.n_test_cases = n_test_cases
        self.input_list = input_list
        self.answer_list = answer_list

    def __eq__(self, other):
        if not isinstance(other, QuestionContent):
            return NotImplemented
        return (
            self.html == other.html
            and self.ques_number == other.ques_number
            and self.ques_sentence == other.ques_sentence
            and self.var_format == other.var_format
            and self.excepted_output == other.excepted_output
            and self.condition == other.condition
            and self.n_test_cases == other.n_test_cases
            and self.input_list == other.input_list
            and self.answer_list == other.answer_list
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        HEADER_INPUT = "- input -"
        HEADER_OUTPUT = "- output -"

        def create_testcase_str(no: int, input_str: str, answer_str: str) -> str:
            input_list = input_str.split("\n")
            answer_list = answer_str.split("\n")
            input_max_width = max(max([len(x) for x in input_list]), len(HEADER_INPUT))

            padding = lambda x: x + " " * (input_max_width - len(x))
            result_line = f"/// SampleCase_{no} ///\n"
            result_line += f"{padding(HEADER_INPUT)} | {HEADER_OUTPUT}\n"
            for input_line, output_line in zip_longest(input_list, answer_list):
                if input_line is None:
                    input_line = ""
                if output_line is None:
                    output_line = ""
                result_line += f"{padding(input_line)} | {output_line} \n"
            return result_line

        result_str = (
            "================================================================\n"
        )
        result_str += "[number]\n"
        result_str += f"| {self.ques_number}\n\n"
        result_str += "[sentence]\n"
        result_str += (
            "\n".join([f"| {x}" for x in self.ques_sentence.split("\n")]) + "\n\n"
        )
        result_str += "[var_format]\n"
        result_str += (
            "\n".join([f"| {x}" for x in self.var_format.split("\n")]) + "\n\n"
        )
        result_str += "[excepted_output]\n"
        result_str += (
            "\n".join([f"| {x}" for x in self.excepted_output.split("\n")]) + "\n\n"
        )
        result_str += "[condition]\n"
        result_str += "\n".join([f"| {x}" for x in self.condition.split("\n")]) + "\n\n"
        result_str += "[n_test_cases]\n"
        result_str += f"| {self.n_test_cases}\n\n"
        result_str += "[input/answer_list]\n"
        for i, (input_item, answer_item) in enumerate(
            zip(self.input_list, self.answer_list)
        ):
            result_str += create_testcase_str(i + 1, input_item, answer_item)
        result_str += "================================================================"
        return result_str
