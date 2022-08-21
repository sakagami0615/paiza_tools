import os
import sys
from typing import List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from itertools import zip_longest

import pytest

from tools.scraping.question_content import QuestionContent
from tools.scraping.skillcheck_content import (
    PageNotFoundError,
    QuestionNumberError,
    SampleCaseSizeError,
    SkillcheckContent,
)


def create_test_html(title: Optional[str], ques_sentence: Optional[str], var_format: Optional[str],
                     excepted_output: Optional[str], condition: Optional[str],
                     input_list: List[str], answer_list: List[str],
                     title_class: str = 'd-problem__page-title',
                     inr1_class: str = 'inr1', inr2_class: str = 'inr2',
                     box1_class: str = 'box1', box2_class: str = 'box2', box3_class: str = 'box3'):

    def create_testcase_str(input_list: List[str], answer_list: List[str]):
        input_format = ('''<div class="sample-content"><div class="sample-content__title">{}</div><pre class="sample-content__input"><code>
                           {}
                           </code></pre></div>
                        ''')
        output_format = ('''</code></pre></div><div class="sample-content"><div class="sample-content__title">{}</div><pre class="sample-content__input"><code>
                           {}
                           </code></pre></div>
                        ''')
        testcase_str = '<div class="sample-container">'
        for idx, (input_text, output_text) in enumerate(zip_longest(input_list, answer_list)):
            if input_text:
                testcase_str += input_format.format(f"入力例{idx + 1}", input_text)
            if output_text:
                testcase_str += output_format.format(f"出力例{idx + 1}", output_text)
        return testcase_str

    testcase_str = create_testcase_str(input_list, answer_list)
    return f"""<h1 class="{title_class}">{title}</h1>
               <div class="{inr1_class}">
               <p class="mb15"><p>{ques_sentence}</p></p>
               </div>
               <div class="{inr2_class}">
               <div class="{box2_class}"><dl class="txt1"><dt class="icon1">評価ポイント</dt>
                 <dd>Point</dd>
               </dl></div>
               <div class="{box3_class}"><dl class="txt1"><dt class="icon2">入力される値</dt>
                 <dd>HEAD</dd>
                 <div class="{box1_class}"><dl class="txt2"><dd>{var_format}</dd></dl></div>
               </div>
               <div class="{box3_class}"><dl class="txt1"><dt class="icon3">期待する出力</dt>
                 <dd><p>{excepted_output}</p></dd></dl>
               </div>
               <div class="{box3_class}"><dl class="txt1"><dt class="icon4">条件</dt>
                 <dd>HEAD<br/></dd>
                 <dd>{condition}</dd>
               </dl></div>
               </div>
               {testcase_str}
               </div>"""



class TestScraping:

    def test_create_1st_challenge_content(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html('QuesNo:QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'])
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        result = SkillcheckContent().create_question_content()
        assert result == QuestionContent(test_html, 'QuesNo', 'QuesBody', 'Format','Output', 'Condition',
                                         2, ['1 2 3 4', '5 6 7 8'], ['10', '14'])


    def test_create_rechallenge_content(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html('再チャレンジ QuesNo:QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'])
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        result = SkillcheckContent().create_question_content()
        assert result == QuestionContent(test_html, 'QuesNo', 'QuesBody', 'Format','Output', 'Condition',
                                         2, ['1 2 3 4', '5 6 7 8'], ['10', '14'])


    def test_create_include_blank_content(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html(' QuesNo :QuesTitle',
                                     ' QuesBody ', ' Format ', ' Output ', ' Condition ',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'])
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        result = SkillcheckContent().create_question_content()
        assert result == QuestionContent(test_html, 'QuesNo', 'QuesBody', 'Format','Output', 'Condition',
                                         2, ['1 2 3 4', '5 6 7 8'], ['10', '14'])


    def test_not_find_page(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html('QuesNo:QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'],
                                     title_class='DUMMY_TITLE_CLASS')
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        is_page_not = True
        with pytest.raises(PageNotFoundError) as e:
            SkillcheckContent().create_question_content()
            is_page_not = False

        assert is_page_not == True
        assert str(e.value) == "Input html text is not skillcheck page."


    def test_extract_question_number_failure(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html(' :QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'])
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        is_page_not = True
        with pytest.raises(QuestionNumberError) as e:
            SkillcheckContent().create_question_content()
            is_page_not = False

        assert is_page_not == True
        assert str(e.value) == "Unable to extract number from this title(' :QuesTitle')."


    def test_extract_samplecase_failure(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html('QuesNo:QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10'],)
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        is_match_testcase = True
        with pytest.raises(SampleCaseSizeError) as e:
            SkillcheckContent().create_question_content()
            is_match_testcase = False

        assert is_match_testcase == True
        assert str(e.value) == f"n_input_files(2) and n_output_files(1) do not match."


    def test_extract_box_class_failure(self, monkeypatch: pytest.MonkeyPatch):
        test_html = create_test_html('QuesNo:QuesTitle',
                                     'QuesBody', 'Format', 'Output', 'Condition',
                                     ['1 2 3 4', '5 6 7 8'], ['10', '14'],
                                     box1_class='DUMMY_CLASS_1', box2_class='DUMMY_CLASS_3', box3_class='DUMMY_CLASS_3')
        monkeypatch.setattr(SkillcheckContent, "_get_html_from_clipboard", lambda arg: test_html)

        result = SkillcheckContent().create_question_content()
        assert result == QuestionContent(test_html, 'QuesNo', 'QuesBody', None, None, None,
                                         2, ['1 2 3 4', '5 6 7 8'], ['10', '14'])
