import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collections import OrderedDict

from tools.codegen.variable_checker import VariableChecker
from tools.codegen.variable_info import VariableInfo


def create_dummy_dict(input_data: str) -> dict:
    dummy_dict = OrderedDict()
    for item in input_data:
        key = (item[0], item[1], item[2])
        if key not in dummy_dict:
            dummy_dict[key] = []
        dummy_dict[key].append(VariableInfo(item[-1][0],
                                            item[-1][1],
                                            item[-1][2],
                                            item[-1][3]))
    return dummy_dict


class TestVariableChecker:

    def test_enable_datatype(self):
        dummy_dict = create_dummy_dict([[0, 1, 1, ('M', 'int', 1, 1)],
                                        [0, 1, 1, ('N', 'float', 1, 1)],
                                        [0, 1, 1, ('K', 'str', 1, 1)]])
        result = VariableChecker()._check_datatype_enable(dummy_dict)
        assert result == True


    def test_blank_datatype(self):
        dummy_dict = create_dummy_dict([[0, 1, 1, ('M', '', 1, 1)],
                                        [0, 1, 1, ('N', 'float', 1, 1)],
                                        [0, 1, 1, ('K', 'str', 1, 1)]])
        result = VariableChecker()._check_datatype_enable(dummy_dict)
        assert result == False


    def test_enable_list_element_vertical_1d(self):
        dummy_dict_1 = create_dummy_dict([[0, 1, 1, ('M', 'int', 3, 1)]])
        result_1 = VariableChecker()._check_element_size_enable(dummy_dict_1)
        assert result_1 == True

        dummy_dict_2 = create_dummy_dict([[0, 1, 1, ('M', 'int', 'A', 1)]])
        result_2 = VariableChecker()._check_element_size_enable(dummy_dict_2)
        assert result_2 == True

        dummy_dict_3 = create_dummy_dict([['A', 'A + 1', 1, ('M', 'int', 1, 1)]])
        result_3 = VariableChecker()._check_element_size_enable(dummy_dict_3)
        assert result_3 == True


    def test_disable_list_element_vertical_1d(self):
        dummy_dict_1 = create_dummy_dict([[0, 1, 1, ('M', 'int', 3, 2)]])
        result_1 = VariableChecker()._check_element_size_enable(dummy_dict_1)
        assert result_1 == False

        dummy_dict_2 = create_dummy_dict([[0, 1, 1, ('M', 'int', 'A', 'B')]])
        result_2 = VariableChecker()._check_element_size_enable(dummy_dict_2)
        assert result_2 == False


    def test_enable_list_element_horizon_1d(self):
        dummy_dict_1 = create_dummy_dict([[0, 3, 3, ('M', 'int', 3, 1)]])
        result_1 = VariableChecker()._check_element_size_enable(dummy_dict_1)
        assert result_1 == True

        dummy_dict_2 = create_dummy_dict([[0, 'A', 'A', ('M', 'int', 'A', 1)]])
        result_2 = VariableChecker()._check_element_size_enable(dummy_dict_2)
        assert result_2 == True

        dummy_dict_3 = create_dummy_dict([['A', 'A + B', 'B', ('M', 'int', 'B', 1)]])
        result_3 = VariableChecker()._check_element_size_enable(dummy_dict_3)
        assert result_3 == True


    def test_disable_list_element_horizon_1d(self):
        dummy_dict_1 = create_dummy_dict([[0, 3, 3, ('M', 'int', 4, 1)]])
        result_1 = VariableChecker()._check_element_size_enable(dummy_dict_1)
        assert result_1 == False

        dummy_dict_2 = create_dummy_dict([[0, 'A', 'A', ('M', 'int', 'B', 1)]])
        result_2 = VariableChecker()._check_element_size_enable(dummy_dict_2)
        assert result_2 == False


    def test_enable_list_element_2d(self):
        dummy_dict_1 = create_dummy_dict([[0, 3, 3, ('M', 'float', 3, 3)]])
        result_1 = VariableChecker()._check_element_size_enable(dummy_dict_1)
        assert result_1 == True

        dummy_dict_2 = create_dummy_dict([[0, 'A', 'A', ('M', 'float', 'A', 3)]])
        result_2 = VariableChecker()._check_element_size_enable(dummy_dict_2)
        assert result_2 == True

        dummy_dict_3 = create_dummy_dict([['A', 'A + B', 'B', ('M', 'float', 'B', 3)]])
        result_3 = VariableChecker()._check_element_size_enable(dummy_dict_3)
        assert result_3 == True


    def test_match_list_element(self):
        dummy_dict_1 = create_dummy_dict([[0, 3, 3, ('M', 'int', 3, 1)],
                                          [0, 3, 3, ('N', 'float', 3, 1)]])
        result_1 = VariableChecker()._check_element_size_match(dummy_dict_1)
        assert result_1 == True

        dummy_dict_2 = create_dummy_dict([['L + M', 'L + M + N', 'N', ('A', 'int',   'N', 1)],
                                          ['L + M', 'L + M + N', 'N', ('B', 'float', 'N', 1)]])
        result_2 = VariableChecker()._check_element_size_match(dummy_dict_2)
        assert result_2 == True


    def test_unmatch_list_element(self):
        dummy_dict_1 = create_dummy_dict([[0, 3, 3, ('M', 'int', 3, 1)],
                                          [0, 3, 3, ('N', 'float', 4, 1)]])
        result_1 = VariableChecker()._check_element_size_match(dummy_dict_1)
        assert result_1 == False

        dummy_dict_2 = create_dummy_dict([['L + M', 'L + M + N', 'N', ('A', 'int',   'N', 1)],
                                          ['L + M', 'L + M + N', 'N', ('B', 'float', 'M', 1)]])
        result_2 = VariableChecker()._check_element_size_match(dummy_dict_2)
        assert result_2 == False


    def test_consistent_variable(self):
        dummy_dict_1 = create_dummy_dict([[0, 3,         3, ('M', 'int', 3, 1)],
                                          ['M', 'M + 1', 1, ('N', 'float', 4, 1)]])
        result_1 = VariableChecker()._check_element_variable_match(dummy_dict_1)
        assert result_1 == True

        dummy_dict_2 = create_dummy_dict([[0, 3,         3, ('M', 'int', 3, 1)],
                                          ['M', 'M + 3', 3, ('N', 'float', 3, 1)]])
        result_2 = VariableChecker()._check_element_variable_match(dummy_dict_2)
        assert result_2 == True

        dummy_dict_3 = create_dummy_dict([[0, 3,         3, ('M', 'int', 3, 1)],
                                          [3, '3 + M', 'M', ('N', 'float', 'M', 1)]])
        result_3 = VariableChecker()._check_element_variable_match(dummy_dict_3)
        assert result_3 == True

        dummy_dict_4 = create_dummy_dict([[0, 1,                 1, ('M', 'int', 1, 1)],
                                          [0, 1,                 1, ('N', 'int', 1, 1)],
                                          [1, '1 + M + N', 'M + N', ('A', 'float', 'M + N', 'N')]])
        result_4 = VariableChecker()._check_element_variable_match(dummy_dict_4)
        assert result_4 == True


    def test_inconsistent_variable(self):
        dummy_dict_1 = create_dummy_dict([[0, 3,         3, ('M', 'int', 3, 1)],
                                          [3, '3 + M', 'M', ('A', 'float', 'N', 1)]])
        result_1 = VariableChecker()._check_element_variable_match(dummy_dict_1)
        assert result_1 == False

        dummy_dict_2 = create_dummy_dict([[0, 1,         1, ('M', 'int', 1, 1)],
                                          [0, 1,         1, ('N', 'int', 1, 1)],
                                          [1, '1 + M', 'M', ('A', 'float', 'M', 'O')]])
        result_2 = VariableChecker()._check_element_variable_match(dummy_dict_2)
        assert result_2 == False

        dummy_dict_3 = create_dummy_dict([[0, 1,                 1, ('M', 'int', 1, 1)],
                                          [0, 1,                 1, ('N', 'int', 1, 1)],
                                          [1, '1 + M + N', 'M + N', ('A', 'float', 'M + B', 'N')]])
        result_3 = VariableChecker()._check_element_variable_match(dummy_dict_3)
        assert result_3 == False
