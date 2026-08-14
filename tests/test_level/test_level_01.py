import io
import itertools as it
import functools as ft
import re

import textwrap
import hedy
import hedy.translation
from hedy import Command
from hedy.external import get_frontend_feature_flags_context, initialize_frontend_feature_flags_from_context
from hedy.sourcemap import SourceRange
from ..Tester import HedyTester, SkippedMapping

from hypothesis import given, settings
import hypothesis.strategies

import pytest


def closed_range(start, stop, step=1):
  inclusive = 1 if (step > 0) else -1
  return range(start, stop + inclusive, step)


def hedy_stdout(code: str, lvl=1, lang='en'):
    result = hedy.transpile(code, lvl, lang)
    assert result

    # TODO: replace these with transpilation flags
    rgx_subs = [ft.partial(re.compile(pat).sub, repl) for pat, repl in {
        r'time\.sleep\([^\n]*\)': 'pass',
        r'print\(([^\n]*)\)': r'print(\1, file=hedy_stdout)',
    }.items()]
    user_code = ft.reduce(lambda c, sub: sub(c), rgx_subs, result.code)
    run_code = hedy.lang_utils.NORMAL_PREFIX_CODE + user_code

    local_vars = {'hedy_stdout': io.StringIO()}
    exec(run_code, globals=None, locals=local_vars)
    return local_vars['hedy_stdout'].getvalue()


#
# print tests
#
@pytest.mark.parametrize('name, code, expected', [
    ('simple',           "print Hallo welkom bij Hedy!",     "Hallo welkom bij Hedy!"),
    ('number',           "print 10",                         "10"),
    ('Arabic',           "print ١١",                         "١١"),
    ('spaces',           "print        hallo!",              "hallo!"),
    ('no space',         "printHallo welkom bij Hedy!",      "Hallo welkom bij Hedy!"),
    ('comma',            "print one, two, three",            "one, two, three"),

    ('multiline',        "print Hallo welkom bij Hedy\nprint Mooi hoor", "Hallo welkom bij Hedy\nMooi hoor"),
    ('line /w spaces',   "print hallo\n      \nprint hallo",             "hallo\nhallo"),

    # escaping
    ('single quote',     "print 'Welcome to OceanView!'", "'Welcome to OceanView!'"),
    ('double quote',     'print "Welcome to OceanView!"', '"Welcome to OceanView!"'),
    ('inner single',     "print Welcome to Hedy's game!", "Welcome to Hedy's game!"),
    ('inner double',     'print It says "Hedy"',          'It says "Hedy"'),
    ('slash',            "print Yes/No",                  "Yes/No"),
    ('backslash',        "print Yes\\No",                 "Yes\\No"),
    ('ending backslash', "print Welcome to \\",           "Welcome to \\"),
])
def test_print_successfully(name, code, expected):
    output = hedy_stdout(code)
    assert output == expected + '\n', f"{name}: {repr(code)=}"


@pytest.mark.parametrize('name, code, expected, opts', [
    ('simple',   "print Hallo welkom bij Hedy!", "print(f'Hallo welkom bij Hedy!')", {}),
    ('no space', "printHallo welkom bij Hedy!",  "print(f'Hallo welkom bij Hedy!')", {}),
    *[
        (f"microbit lvl {lv}", "print a", "display.scroll('a')", {'microbit': True, 'skip_faulty': False, 'lvl': lv})
        for lv in closed_range(1, 3)
    ]
])
def test_print_transpile(name, code, expected, opts):
    result = hedy.transpile(code, opts.pop('lvl', 1), **opts)
    assert result and result.code == expected, f"{name}: {code=}"
    assert result.commands == [Command.print]


@pytest.mark.parametrize('lang', [
    # a nice mix of latin/non-latin and l2r and r2l!
    'ar', 'ca', 'sq', 'bg', 'es', 'fi', 'fr', 'he', 'nl', 'hi', 'ur', 'te', 'th', 'vi', 'uk', 'tr',
])
def test_print_translate(lang):
    en_print = 'print Hello World'
    xlated = hedy.translation.translate_keywords(en_print, 'en', lang, 1)
    actual = hedy.translation.translate_keywords(xlated, lang, 'en', 1)
    assert actual == en_print


@pytest.mark.parametrize('name, code, expected', [
    ('ar',                      "قول أهلا ومرحبا بكم في هيدي!", "print(f'أهلا ومرحبا بكم في هيدي!')"),
    ('ar tatweel',              "قول لــــ",                   "print(f'لــــ')"),
    ('ar tatweel begin',        "ـــقول أ",                    "print(f'أ')"),
    ('ar tatweel multiple end', "ـــقــوـلــــ أ",             "print(f'أ')"),
    ('ar tatweel all places',   "ـــقــولـ أ",                 "print(f'أ')"),
    ('ar 2',                    "قول مرحبا أيها العالم!",      "print(f'مرحبا أيها العالم!')"),

    # FH, May 2022, sadly beginning a string with tatweel does not work
    # would need complex changes to the grammar (documented further in the grammar of level 1)
    # so I am leaving this as it is for now
    # ('ar tatweel itself',       "قول ـ",                       "ـ"),
])
def test_print_transpile_ar(name, code, expected):
    result = hedy.transpile(code, 1, lang='ar')
    assert result and result.code == expected, f"{name}: {code=}"


class TestsLevel1(HedyTester):
    level = 1
    '''
    Tests should be ordered as follows:
     * commands in the order of hedy.py e.g. for level 1: ['print', 'ask', 'echo', 'turn', 'forward']
     * combined tests
     * markup tests
     * negative tests
     * hypothesis tests

    Naming conventions are like this:
     * single keyword positive tests are just keyword or keyword_special_case
     * multi keyword positive tests are keyword1_keywords_2
     * negative tests should be situation_gives_exception
    '''

    #
    # ask tests
    #
    def test_ask(self):
        code = "ask wat is je lievelingskleur?"
        expected = "answer = input(f'wat is je lievelingskleur?')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_with_answer_keyword_uses_globals_lookup(self):
        code = "ask answer"
        expected = "answer = input(f'{globals().get(\"answer\", \"answer\")}')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_single_quoted_text(self):
        code = "ask 'Welcome to OceanView?'"
        expected = "answer = input(f'\\'Welcome to OceanView?\\'')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_double_quoted_text(self):
        code = 'ask "Welcome to OceanView?"'
        expected = "answer = input(f'\"Welcome to OceanView?\"')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_text_with_inner_single_quote(self):
        code = "ask Welcome to Hedy's game!"
        expected = """answer = input(f'Welcome to Hedy\\'s game!')"""

        self.single_level_tester(code=code, expected=expected)

    def test_ask_text_with_inner_double_quote(self):
        code = 'ask It says "Hedy"'
        expected = """answer = input(f'It says "Hedy"')"""

        self.single_level_tester(code=code, expected=expected)

    def test_ask_es(self):
        code = "ask ask Cuál es tu color favorito?"
        expected = "answer = input(f'ask Cuál es tu color favorito?')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_nl_code_transpiled_in_nl(self):
        code = "vraag Heb je er zin in?"
        expected = "answer = input(f'Heb je er zin in?')"

        self.single_level_tester(code=code, expected=expected, lang='nl')

    def test_ask_en_code_transpiled_in_nl(self):
        code = "ask Heb je er zin in?"
        expected = "answer = input(f'Heb je er zin in?')"

        self.single_level_tester(
            code=code,
            expected=expected,
            lang='nl',
            translate=False  # we are trying a Dutch keyword in en, can't be translated
        )

    def test_ask_number(self):
        code = "ask 42"
        expected = "answer = input(f'42')"

        self.single_level_tester(code=code, expected=expected)

    def test_ask_arabic_number(self):
        code = "ask ٢٣٤"
        expected = "answer = input(f'٢٣٤')"

        self.single_level_tester(code=code, expected=expected)

    #
    # play tests
    #
    def test_play_no_args(self):
        code = "play "
        expected = self.play_transpiled("'C4'")

        self.multi_level_tester(
            code=code,
            translate=False,
            expected=expected,
            max_level=2
        )

    def test_play(self):
        code = "play A"
        expected = self.play_transpiled("'A'")

        self.multi_level_tester(
            code=code,
            translate=False,
            expected=expected
        )

    def test_play_lowercase(self):
        code = "play a"
        expected = self.play_transpiled("'A'")

        self.multi_level_tester(
            code=code,
            translate=False,
            expected=expected
        )

    def test_play_int(self):
        code = "play 34"
        expected = self.play_transpiled("'34'")

        self.multi_level_tester(code=code, expected=expected)

    def test_play_int_arabic(self):
        code = "play ١١"
        expected = self.play_transpiled("'١١'")

        self.multi_level_tester(code=code, expected=expected, max_level=6)

    def test_print_answer_keyword_without_ask_prints_literal(self):
        code = "print answer"
        expected = "print(f'{globals().get(\"answer\", \"answer\")}')"

        self.single_level_tester(
            code=code,
            expected=expected,
            output='answer',
            expected_commands=[Command.print]
        )

    def test_print_localized_answer_keyword_without_ask_prints_literal(self):
        code = "print antwoord"
        expected = "print(f'{globals().get(\"answer\", \"antwoord\")}')"

        self.single_level_tester(
            code=code,
            expected=expected,
            output='antwoord',
            expected_commands=[Command.print],
            lang='nl'
        )

    def test_print_english_answer_keyword_in_nl_without_ask_prints_literal(self):
        code = "print answer"
        expected = "print(f'{globals().get(\"answer\", \"answer\")}')"

        self.single_level_tester(
            code=code,
            expected=expected,
            output='answer',
            expected_commands=[Command.print],
            lang='nl',
            translate=False
        )

    def test_print_mixed_english_and_localized_answer_keywords_in_nl(self):
        code = "print answer antwoord"
        expected = (
            "print(f'{globals().get(\"answer\", \"answer\")} "
            "{globals().get(\"answer\", \"antwoord\")}')"
        )

        self.single_level_tester(
            code=code,
            expected=expected,
            output='answer antwoord',
            expected_commands=[Command.print],
            lang='nl',
            translate=False
        )

    def test_ask_without_print_transpiles_to_single_ask_command(self):
        code = "ask What is your favorite color?"
        expected = "answer = input(f'What is your favorite color?')"

        self.single_level_tester(
            code=code,
            expected=expected,
            expected_commands=[Command.ask]
        )

    def test_ask_then_print_answer_keyword(self):
        code = textwrap.dedent("""\
        ask Name?
        print answer""")

        expected = textwrap.dedent("""\
        answer = input(f'Name?')
        print(f'{globals().get("answer", "answer")}')""")

        self.single_level_tester(
            code=code,
            expected=expected,
            expected_commands=[Command.ask, Command.print]
        )

    def test_print_answer_keyword_with_feature_flag_disabled(self):
        code = "print answer"
        expected = "print(f'answer')"

        previous_context = get_frontend_feature_flags_context()
        try:
            initialize_frontend_feature_flags_from_context({
                'frontend_environment': 'production',
                'feature_flags': {
                    'answer_interpolation': {
                        'production': False,
                        'local': True,
                        'alpha': True,
                    }
                },
            })

            self.single_level_tester(
                code=code,
                expected=expected,
                output='answer',
                expected_commands=[Command.print],
            )
        finally:
            initialize_frontend_feature_flags_from_context(previous_context)

    def test_print_answer_keyword_with_feature_flag_enabled(self):
        code = "print answer"
        expected = "print(f'{globals().get(\"answer\", \"answer\")}')"

        previous_context = get_frontend_feature_flags_context()
        try:
            initialize_frontend_feature_flags_from_context({
                'frontend_environment': 'local',
                'feature_flags': {
                    'answer_interpolation': {
                        'production': False,
                        'local': True,
                    }
                },
            })

            self.single_level_tester(
                code=code,
                expected=expected,
                output='answer',
                expected_commands=[Command.print],
            )
        finally:
            initialize_frontend_feature_flags_from_context(previous_context)

    def test_mixes_languages_nl_en(self):
        code = textwrap.dedent("""\
        vraag Heb je er zin in?
        echo
        ask are you sure?
        print mooizo!""")

        expected = textwrap.dedent("""\
        answer = input(f'Heb je er zin in?')
        print(answer)
        answer = input(f'are you sure?')
        print(f'mooizo!')""")

        self.single_level_tester(
            code=code,
            expected=expected,
            expected_commands=['ask', 'echo', 'ask', 'print'],
            lang='nl',
            translate=False  # mixed codes will not translate back to their original form, sadly
        )

    #
    # echo tests
    #
    def test_echo_without_argument(self):
        code = "ask wat?\necho"
        expected = "answer = input(f'wat?')\nprint(answer)"

        self.single_level_tester(code=code, expected=expected)

    def test_echo_with_quotes(self):
        code = textwrap.dedent("""\
        ask waar?
        echo oma's aan de""")

        expected = textwrap.dedent("""\
        answer = input(f'waar?')
        print('oma\\'s aan de '+answer)""")

        self.single_level_tester(code=code, expected=expected)

    #
    # forward tests
    #
    def test_forward(self):
        code = "forward 50"
        expected = self.forward_transpiled(50)

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=11
        )

    def test_forward_arabic_numeral(self):
        code = "forward ١١١١١١١"
        expected = self.forward_transpiled(1111111)

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=11
        )

    def test_forward_hindi_numeral(self):
        code = "forward ५५५"
        expected = self.forward_transpiled(555)

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=11
        )

    def test_forward_without_argument(self):
        code = 'forward'
        expected = textwrap.dedent("""\
        t.forward(0)
        time.sleep(0.1)""")

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=11
        )

    def test_forward_with_text_gives_type_error(self):
        code = "forward lalalala"

        self.multi_level_tester(
            code=code,
            max_level=12,
            exception=hedy.exceptions.InvalidArgumentTypeException,
            extra_check_function=lambda c: c.exception.arguments['line_number'] == 1
        )

    def test_multiple_forward_without_arguments(self):
        code = textwrap.dedent("""\
        forward
        forward""")
        expected = textwrap.dedent("""\
        t.forward(0)
        time.sleep(0.1)
        t.forward(0)
        time.sleep(0.1)""")

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    #
    # color tests
    #
    def test_color_no_args(self):
        code = "color"
        expected = "t.pencolor('black')"
        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=10)

    def test_one_color_red(self):
        code = "color red"
        expected = "t.pencolor('red')"

        self.single_level_tester(code=code, expected=expected,
                                 extra_check_function=self.is_turtle())

    def test_one_color_purple(self):
        code = "color purple"
        expected = "t.pencolor('purple')"

        self.single_level_tester(code=code, expected=expected,
                                 extra_check_function=self.is_turtle())

    def test_one_color_nl(self):
        code = "kleur paars"
        expected = "t.pencolor('purple')"

        self.single_level_tester(code=code, expected=expected,
                                 extra_check_function=self.is_turtle(), lang='nl')

    #
    # turn tests
    #
    def test_turn_no_args(self):
        code = "turn"
        expected = "t.right(0)"

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    def test_turn_right(self):
        code = "turn right"
        expected = "t.right(90)"

        self.single_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    def test_turn_left(self):
        code = "turn left"
        expected = "t.left(90)"

        self.single_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    def test_turn_left_nl(self):
        code = "draai links"
        expected = "t.left(90)"

        self.single_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            lang='nl'
        )

    def test_turn_ar(self):
        code = "استدر يسار"
        expected = "t.left(90)"

        self.single_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            lang='ar'
        )

    def test_turn_with_text_gives_error(self):
        code = textwrap.dedent("""\
        turn koekoek
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        # We test the skipping of faulty code by checking if a certain range contains an error after executing
        # The source range consists of from_line, from_column, to_line, to_column
        # we can add multiple tests to the skipped_mappings list to test multiple error mappings

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 13), hedy.exceptions.InvalidArgumentException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.single_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings
        )

    #
    # comment tests
    #
    def test_comment(self):
        code = "# geen commentaar, helemaal geen!"
        expected = ""

        self.multi_level_tester(code=code, expected=expected)

    def test_print_comment(self):
        code = "print Hallo welkom bij Hedy! # This is a print"
        expected = "print(f'Hallo welkom bij Hedy! ')"
        output = 'Hallo welkom bij Hedy!'

        self.single_level_tester(
            code=code,
            expected=expected,
            output=output,
            expected_commands=[Command.print]
        )

    #
    # combined commands tests
    #
    def test_print_ask_echo(self):
        code = textwrap.dedent("""\
        print Hallo
        ask Wat is je lievelingskleur
        echo je lievelingskleur is""")

        expected = textwrap.dedent("""\
        print(f'Hallo')
        answer = input(f'Wat is je lievelingskleur')
        print('je lievelingskleur is '+answer)""")

        self.single_level_tester(
            code=code,
            expected=expected,
            expected_commands=[Command.print, Command.ask, Command.echo])

    def test_forward_turn_combined(self):
        code = textwrap.dedent("""\
            forward 50
            turn
            forward 100""")

        expected = self.dedent(
            self.forward_transpiled(50),
            't.right(0)',
            self.forward_transpiled(100))

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            expected_commands=[Command.forward, Command.turn, Command.forward],
            max_level=11
        )

    #
    # markup tests
    #
    def test_lines_may_end_in_spaces(self):
        code = "print Hallo welkom bij Hedy! "
        expected = "print(f'Hallo welkom bij Hedy! ')"
        output = 'Hallo welkom bij Hedy!'

        self.single_level_tester(code=code, expected=expected, output=output, translate=False)

    def test_comments_may_be_empty(self):
        code = textwrap.dedent("""\
            #
            # This is a comment
            #
            print Привіт, Хейді!""")
        expected = "print(f'Привіт, Хейді!')"
        output = "Привіт, Хейді!"

        self.single_level_tester(code=code, expected=expected, output=output)

    #
    # negative tests
    #
    def test_print_with_space_gives_invalid(self):
        code = textwrap.dedent("""\
         print Hallo welkom bij Hedy!
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 30), hedy.exceptions.InvalidSpaceException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.multi_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings,
            max_level=1)

    def test_ask_with_space_gives_invalid(self):
        code = textwrap.dedent("""\
         ask Hallo welkom bij Hedy?
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 28), hedy.exceptions.InvalidSpaceException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.multi_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings,
            max_level=1)

    def test_lines_with_spaces_english_gives_invalid(self):
        code = textwrap.dedent("""\
         print Hallo welkom bij Hedy!
            print Hallo welkom bij Hedy!""")

        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.InvalidSpaceException,
            skip_faulty=False,
            max_level=3)

    def test_lines_with_spaces_french_gives_invalid(self):
        code = textwrap.dedent("""\
         affiche Bonjour Hedy!
            affiche Bonjour Hedy!""")

        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.InvalidSpaceException,
            skip_faulty=False,
            lang='fr',
            max_level=3)

    def test_lines_with_spaces_gives_invalid(self):
        code = " print Hallo welkom bij Hedy!\n print Hallo welkom bij Hedy!"
        expected = "pass\npass"

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 30), hedy.exceptions.InvalidSpaceException),
            SkippedMapping(SourceRange(1, 1, 1, 30), hedy.exceptions.InvalidSpaceException),
        ]

        self.multi_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings,
            max_level=3)

    def test_word_plus_period_gives_invalid(self):
        code = textwrap.dedent("""\
        word.
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 6), hedy.exceptions.MissingCommandException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.single_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings
        )

    def test_non_keyword_gives_invalid(self):
        code = textwrap.dedent("""\
        groen
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 6), hedy.exceptions.MissingCommandException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.single_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings
        )

    def test_one_mistake_not_skipped(self):
        code = "prind wrong"

        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.InvalidCommandException,
            max_level=3
        )

    def test_lonely_echo_gives_LonelyEcho(self):
        code = "echo wat dan?"
        self.single_level_tester(
            code,
            exception=hedy.exceptions.LonelyEchoException)

    def test_echo_before_ask_gives_lonely_echo(self):
        code = textwrap.dedent("""\
        echo what can't we do?
        ask time travel""")
        self.single_level_tester(code, exception=hedy.exceptions.LonelyEchoException)

    def test_pint_after_empty_line_gives_error_line_3(self):
        code = textwrap.dedent("""\
        print hallo

        prnt hallo
        prind skipping""")

        expected = textwrap.dedent("""\
        print(f'hallo')
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(3, 1, 3, 11), hedy.exceptions.InvalidCommandException),
            SkippedMapping(SourceRange(4, 1, 4, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.single_level_tester(
            code,
            expected=expected,
            skipped_mappings=skipped_mappings
        )

    def test_print_without_argument_gives_incomplete(self):
        self.multi_level_tester(
            code="print",
            exception=hedy.exceptions.IncompleteCommandException,
            extra_check_function=lambda c: c.exception.arguments['incomplete_command'] == 'print'
        )

    def test_print_without_argument_gives_incomplete_2(self):
        self.multi_level_tester(
            code="print lalalala\nprint",
            exception=hedy.exceptions.IncompleteCommandException,
            extra_check_function=lambda c: c.exception.arguments['incomplete_command'] == 'print',
            max_level=17,
        )

    def test_non_keyword_with_argument_gives_invalid(self):
        code = textwrap.dedent("""\
        aks felienne 123
        prind skipping""")

        expected = textwrap.dedent("""\
        pass
        pass""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 1, 17), hedy.exceptions.InvalidCommandException),
            SkippedMapping(SourceRange(2, 1, 2, 15), hedy.exceptions.InvalidCommandException),
        ]

        self.multi_level_tester(
            code=code,
            expected=expected,
            skipped_mappings=skipped_mappings,
            translate=False,
            extra_check_function=lambda c: c.arguments['invalid_command'] in ['aks', 'prind'],
            max_level=5,
        )

    def test_source_map(self):
        code = textwrap.dedent("""\
            print Hallo welkom bij Hedy!
            forward 50
            ask Wat is je lievelingskleur
            echo je lievelingskleur is""")

        expected_code = self.dedent(
            "print(f'Hallo welkom bij Hedy!')",
            self.forward_transpiled(50),
            "answer = input(f'Wat is je lievelingskleur')",
            "print('je lievelingskleur is '+answer)")

        expected_source_map = {
            '1/1-1/29': '1/1-1/33',
            '2/1-2/11': '2/1-4/16',
            '3/1-3/30': '5/1-5/45',
            '4/1-4/27': '6/1-6/39',
            '1/1-4/28': '1/1-6/39'
        }

        self.single_level_tester(code, expected=expected_code)
        self.source_map_tester(code=code, expected_source_map=expected_source_map)

# hypothesis initialization starts here


# numbers define an order since some commands must be in a certain place (f.e. here: ask must go before echo)
templates = [
    ("print <P>", -1),
    ("print <P>", -1),
    ("print <P>", -1),
    ("turn left", -1),  # arguments for turn and forward could also be randomly sampled
    ("turn right", -1),
    ("forward 200", -1),
    ("forward -200", -1),
    ("ask <P>", 1),
    ("echo <P>", 2),
    ("ask <P>", 3),
    ("echo <P>", 4)
]


def valid_permutation(lines):
    orders = [order for _, order in lines]
    significant_orders = [x for x in orders if x > 0]  # -1 may be placed everywhere
    list_ = [significant_orders[i] <= significant_orders[i+1] for i in range(len(significant_orders)-1)]
    return all(list_)


class TestsHypothesisLevel1(HedyTester):
    level = 1

    @given(code_tuples=hypothesis.strategies.permutations(templates), d=hypothesis.strategies.data())
    @settings(deadline=None, max_examples=100)
    # FH may 2023: we now always use a permutation, but a random sample which could potentially be smaller would be a nice addition!
    def test_template_combination(self, code_tuples, d):
        excluded_chars = ["_", "#", '\n', '\r', ' ']
        random_print_argument = hypothesis.strategies.text(
            alphabet=hypothesis.strategies.characters(blacklist_characters=excluded_chars),
            min_size=1,
            max_size=10)

        if valid_permutation(code_tuples):
            lines = [line.replace("<P>", d.draw(random_print_argument)) for line, _ in code_tuples]
            code = '\n'.join(lines)

            self.single_level_tester(
                code=code,
                translate=False
            )

            expected_commands = [Command.ask, Command.ask, Command.echo, Command.echo, Command.forward, Command.forward,
                                 Command.print, Command.print, Command.print, Command.turn, Command.turn]

            # TODO, FH sept 2023: all_commands parses and thus is expensive
            # we should get the commands list back from the parser instead (parseresult.commands)
            # since we don't use many single_level_tester features
            # we can transpile and check the python "manually"
            all_commands = sorted(hedy.all_commands(code, self.level, 'en'))
            self.assertEqual(expected_commands, all_commands)
