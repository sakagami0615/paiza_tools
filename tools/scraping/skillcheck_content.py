import os
from typing import List, Optional, Tuple

import pyperclip
from bs4 import BeautifulSoup

from tools.common.file_function import check_file_exist, read_json, read_text
from tools.config.file_config import FileConfig
from tools.scraping.question_content import QuestionContent


class PageNotFoundError(Exception):
    def __init__(self):
        message = "Input html text is not skillcheck page."
        super().__init__(message)


class QuestionNumberError(Exception):
    def __init__(self, title):
        message = f"Unable to extract number from this title('{title}')."
        super().__init__(message)


class SampleCaseSizeError(Exception):
    def __init__(self, n_inputs, n_outputs):
        message = (
            f"n_input_files({n_inputs}) and n_output_files({n_outputs}) do not match."
        )
        super().__init__(message)


class SkillcheckContent:

    VARIABLE_CLASS_TEXT = "入力される値"
    EXPECTED_OUTPUT_CLASS_TEXT = "期待する出力"
    CONDITION_CLASS_TEXT = "条件"
    BOX_CLASS_NAMES = ["box1", "box2", "box3"]

    def __init__(self, dir_path: str = ""):
        meta_file_path = os.path.join(dir_path, FileConfig.METADATA_FILE)
        try:
            check_file_exist(meta_file_path)
            metadata = read_json(meta_file_path)
            self.ques_html_path = os.path.join(dir_path, metadata["question_file"])
        except FileNotFoundError:
            self.ques_html_path = None

    def _strip_all_lines(self, text: str) -> str:
        return "\n".join([x.strip() for x in text.split("\n")]).strip()

    def _remove_head_line(self, text: str, is_strip: bool = True) -> str:
        remove_head_list = text.split("\n")[1:]
        if is_strip:
            remove_head_list = [x.strip() for x in remove_head_list]
        return "\n".join(remove_head_list)

    def _judge_html_format(self, html_text: str) -> bool:
        page_soup = BeautifulSoup(html_text, "html.parser")

        if page_soup.find("h1", class_="d-problem__page-title") is None:
            return False
        if page_soup.find("div", class_="inr1") is None:
            return False
        if page_soup.find("div", class_="inr2") is None:
            return False

        return True

    def _get_html_from_localfile(self) -> str:
        if self.ques_html_path is None:
            return ""
        return read_text(self.ques_html_path)

    def _get_html_from_clipboard(self) -> str:
        return pyperclip.paste()

    def _get_ques_html(self) -> str:
        local_html_text = self._get_html_from_localfile()
        clip_html_text = self._get_html_from_clipboard()

        local_html_result = self._judge_html_format(local_html_text)
        clip_html_result = self._judge_html_format(clip_html_text)

        if not local_html_result and not clip_html_result:
            raise PageNotFoundError

        if local_html_result:
            return local_html_text
        return clip_html_text

    def _find_text_in_box_class(
        self, src_soup: BeautifulSoup, class_text: str
    ) -> Optional[BeautifulSoup]:
        # box1からbox3までで探索し、class_textの文字がある場合は抽出
        for box_class in self.BOX_CLASS_NAMES:
            box_soups = src_soup.find_all("div", class_=box_class)
            for box_soup in box_soups:
                title = box_soup.find("dt")
                title = title if not title else title.text
                if title == class_text:
                    return box_soup
        return None

    def _extract_question_number(self, page_soup: BeautifulSoup) -> str:
        problem_soup = page_soup.find("h1", class_="d-problem__page-title")
        title = problem_soup.text
        title = title.replace("再チャレンジ", "").strip()
        ques_number = title.split(":")[0].strip()
        if not ques_number:
            raise QuestionNumberError(problem_soup.text)

        return ques_number

    def _extract_question_sentence(self, page_soup: BeautifulSoup) -> str:
        inr1_soup = page_soup.find("div", class_="inr1")
        sentence = inr1_soup.text.strip()
        return sentence

    def _extract_variable_format(self, page_soup: BeautifulSoup) -> Optional[str]:
        inr2_soup = page_soup.find("div", class_="inr2")
        format_soup = self._find_text_in_box_class(inr2_soup, self.VARIABLE_CLASS_TEXT)
        if format_soup is None:
            return None

        # 不要文字と行の削除
        target_text = format_soup.text.replace(self.VARIABLE_CLASS_TEXT, "").strip()
        target_text = self._remove_head_line(target_text).strip()

        # 先頭の説明文字の次に記載されている入力フォーマット内容を抽出
        target_list = target_text.split("\n\n")
        format_text = target_list[0]
        return format_text

    def _extract_excepted_output(self, page_soup: BeautifulSoup) -> Optional[str]:
        inr2_soup = page_soup.find("div", class_="inr2")
        excepted_soup = self._find_text_in_box_class(
            inr2_soup, self.EXPECTED_OUTPUT_CLASS_TEXT
        )
        if excepted_soup is None:
            return None

        # 不要文字の削除
        excepted_text = excepted_soup.text.replace(self.EXPECTED_OUTPUT_CLASS_TEXT, "")
        excepted_text = self._strip_all_lines(excepted_text)
        return excepted_text

    def _extract_condition(self, page_soup: BeautifulSoup) -> Optional[str]:
        inr2_soup = page_soup.find("div", class_="inr2")
        condition_soup = self._find_text_in_box_class(
            inr2_soup, self.CONDITION_CLASS_TEXT
        )
        if condition_soup is None:
            return None

        # 不要文字と行の削除
        target_text = condition_soup.text.replace(self.CONDITION_CLASS_TEXT, "").strip()
        target_text = self._remove_head_line(target_text)

        # 先頭の説明文字の次に記載されている入力フォーマット内容を抽出
        target_list = target_text.split("\n\n")
        format_text = target_list[0]
        return format_text

    def _extract_testcase_data(
        self, page_soup: BeautifulSoup
    ) -> Tuple[int, List[str], List[str]]:
        cate_soups = page_soup.find_all("div", class_="sample-content__title")
        data_soups = page_soup.find_all("pre", class_="sample-content__input")
        input_list = []
        output_list = []

        for cate_soup, data_soup in zip(cate_soups, data_soups):
            cate = cate_soup.text.strip()
            data = data_soup.text.strip()
            if cate.find("入力例") >= 0:
                input_list.append(data)
            elif cate.find("出力例") >= 0:
                output_list.append(data)

        # 入力と出力のサンプル数のサンプル数の非一致確認
        n_test_cases = len(input_list)
        if n_test_cases != len(output_list):
            raise SampleCaseSizeError(len(input_list), len(output_list))

        return (n_test_cases, input_list, output_list)

    def create_question_content(self) -> QuestionContent:
        page_html = self._get_ques_html()
        page_soup = BeautifulSoup(page_html, "html.parser")

        ques_number = self._extract_question_number(page_soup)
        ques_sentence = self._extract_question_sentence(page_soup)
        var_format = self._extract_variable_format(page_soup)
        excepted_output = self._extract_excepted_output(page_soup)
        condition = self._extract_condition(page_soup)
        n_test_cases, input_list, output_list = self._extract_testcase_data(page_soup)

        return QuestionContent(
            page_html,
            ques_number,
            ques_sentence,
            var_format,
            excepted_output,
            condition,
            n_test_cases,
            input_list,
            output_list,
        )
