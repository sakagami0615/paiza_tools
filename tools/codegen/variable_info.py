from typing import Union


class VariableInfo:
    def __init__(
        self,
        name: str,
        datatype: str = "",
        size_1d: Union[int, str] = 1,
        size_2d: Union[int, str] = 1,
    ):
        self.name = name
        self.datatype = datatype
        self.__size_1d = size_1d if isinstance(size_1d, str) else str(size_1d)
        self.__size_2d = size_2d if isinstance(size_2d, str) else str(size_2d)
        self.__size_1d, self.is_dynamic_size_1d = self._judge_var_dynamic(
            self.__size_1d
        )
        self.__size_2d, self.is_dynamic_size_2d = self._judge_var_dynamic(
            self.__size_2d
        )

    def _judge_var_dynamic(self, var: str):
        token = var.split("_")
        if len(token) < 2:
            return var, False
        return token[0], True

    @property
    def size_1d(self):
        return self.__size_1d if not self.__size_1d.isdigit() else int(self.__size_1d)

    @property
    def size_2d(self):
        return self.__size_2d if not self.__size_2d.isdigit() else int(self.__size_2d)

    @size_1d.setter
    def size_1d(self, size_1d):
        self.__size_1d = size_1d if isinstance(size_1d, str) else str(size_1d)
        self.__size_1d, self.is_dynamic_size_1d = self._judge_var_dynamic(
            self.__size_1d
        )

    @size_2d.setter
    def size_2d(self, size_2d):
        self.__size_2d = size_2d if isinstance(size_2d, str) else str(size_2d)
        self.__size_2d, self.is_dynamic_size_2d = self._judge_var_dynamic(
            self.__size_2d
        )

    def __str__(self):
        datatype = self.datatype if self.datatype != "" else "None"
        return (
            f"{self.name}<{datatype}>[{self.size_1d}({self.is_dynamic_size_1d})]"
            f"[{self.size_2d}({self.is_dynamic_size_2d})]"
        )
