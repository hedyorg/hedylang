from parameterized import parameterized

import hedy
import hedy.translation as hedy_translation
# from test_level_01 import HedyTester
from ..Tester import HedyTester

# tests should be ordered as follows:
# * Translation from English to Dutch
# * Translation from Dutch to English
# * Translation to several languages
# * Error handling


class TestsTranslationLevel1(HedyTester):
    level = 1
    keywords_from = hedy_translation.keywords_to_dict('en')
    keywords_to = hedy_translation.keywords_to_dict('nl')

    def test_print_english_dutch(self):
        code = 'print Hallo welkom bij Hedy!'

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = 'print Hallo welkom bij Hedy!'

        self.assertEqual(expected, result)

    def test_ask_english_dutch(self):
        code = "ask Hallo welkom bij Hedy!"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "vraag Hallo welkom bij Hedy!"

        self.assertEqual(expected, result)

    def test_echo_english_dutch(self):
        code = "ask Hallo welkom bij Hedy!\necho"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "vraag Hallo welkom bij Hedy!\necho"

        self.assertEqual(expected, result)

    def test_ask_echo_english_dutch(self):
        code = 'print Hallo welkom bij Hedy\'\'\nvraag hoe heet je\necho'

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = 'print Hallo welkom bij Hedy\'\'\nask hoe heet je\necho'

        self.assertEqual(expected, result)

    def test_print_kewords_english_dutch(self):
        code = "print print ask echo"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "print print ask echo"

        self.assertEqual(expected, result)

    def test_forward_english_dutch(self):
        code = "forward 50"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "vooruit 50"

        self.assertEqual(expected, result)

    def test_turn_english_dutch(self):
        code = "turn left"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "draai links"

        self.assertEqual(expected, result)

    def test_print_dutch_english(self):
        code = 'print Hallo welkom bij Hedy!'

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = 'print Hallo welkom bij Hedy!'

        self.assertEqual(expected, result)

    def test_ask_dutch_english(self):
        code = "vraag Hallo welkom bij Hedy!\nvraag veel plezier"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "ask Hallo welkom bij Hedy!\nask veel plezier"

        self.assertEqual(expected, result)

    def test_echo_french(self):
        code = "echo Hedy"

        result = hedy_translation.translate_keywords(
            code, "en", "fr", self.level)
        expected = "réponds Hedy"

        self.assertEqual(expected, result)

    def test_echo_dutch_english(self):
        code = "vraag stel je vraag\necho tekst"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "ask stel je vraag\necho tekst"

        self.assertEqual(expected, result)

    def test_ask_echo_dutch_english(self):
        code = 'vraag Hallo welkom bij Hedy!\necho hoi'

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = 'ask Hallo welkom bij Hedy!\necho hoi'

        self.assertEqual(expected, result)

    def test_ask_kewords_dutch_english(self):
        code = "vraag print ask echo"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "ask print ask echo"

        self.assertEqual(expected, result)

    def test_turn_dutch_english(self):
        code = "draai left"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "turn left"

        self.assertEqual(expected, result)

    def test_turn_dutch_english_no_argument(self):
        code = "draai"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "turn"

        self.assertEqual(expected, result)

    def test_translate_back(self):
        code = 'print Hallo welkom bij Hedy\nask hoe heet je\necho'

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        result = hedy_translation.translate_keywords(result, from_lang="nl", to_lang="en", level=self.level)

        self.assertEqual(code, result)

    def test_level1_answer_keyword_in_print_text_en_to_es(self):
        code = "print your name is answer"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="es", level=self.level)
        expected = "imprimir your name is respuesta"

        self.assertEqual(expected, result)

    def test_level1_answer_keyword_in_ask_and_print_text_en_to_es(self):
        code = "ask what is your name\nprint your name is answer"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="es", level=self.level)
        expected = "preguntar what is your name\nimprimir your name is respuesta"

        self.assertEqual(expected, result)

    def test_level1_answer_keyword_in_print_text_nl_to_en(self):
        code = "print jouw naam is antwoord"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="en", level=self.level)
        expected = "print jouw naam is answer"

        self.assertEqual(expected, result)

    def test_level1_answer_keyword_mixed_english_and_localized_nl_to_es(self):
        code = "print antwoord answer"

        result = hedy_translation.translate_keywords(code, from_lang="nl", to_lang="es", level=self.level)
        expected = "imprimir respuesta respuesta"

        self.assertEqual(expected, result)

    def test_level1_answer_keyword_respects_token_boundaries(self):
        code = "print myanswer answer_answer answer answer!"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="es", level=self.level)
        expected = "imprimir myanswer answer_answer respuesta respuesta!"

        self.assertEqual(expected, result)

    def test_level1_answer_keyword_only_in_ask_print_text(self):
        code = "forward answer\nprint answer"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "vooruit answer\nprint antwoord"

        self.assertEqual(expected, result)

    # No translation because of the invalid space error

    def test_invalid_space(self):
        # FH, dec 23: We remove leading spaces in the translation, since the editor
        # also does this. It means dropping a space from the program but that, I think, is better
        # than not translating a program that does run

        code = " ask Hedy"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "vraag Hedy"

        self.assertEqual(expected, result)

    def no_argument_ask(self):
        code = "ask"

        result = hedy_translation.translate_keywords(code, from_lang="en", to_lang="nl", level=self.level)
        expected = "ask"

        self.assertEqual(expected, result)

    @parameterized.expand([('en', 'forward'), ('es', 'adelante')])
    def test_forward_type_error_translates_command(self, lang, forward):
        code = f'{forward} text'

        self.multi_level_tester(
            lang=lang,
            code=code,
            max_level=12,
            exception=hedy.exceptions.InvalidArgumentTypeException,
            extra_check_function=self.exception_command(forward)
        )
