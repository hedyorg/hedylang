import textwrap

from parameterized import parameterized

from hedy import exceptions
import hedy
from hedy import Command
from hedy.sourcemap import SourceRange
from ..Tester import HedyTester, SkippedMapping


class TestsLevel12(HedyTester):
    level = 12
    '''
    Tests should be ordered as follows:
     * commands in the order of hedy.py e.g. for level 1: ['print', 'ask', 'echo', 'turn', 'forward']
     * combined tests
     * markup tests
     * negative tests

    Naming conventions are like this:
     * single keyword positive tests are just keyword or keyword_special_case
     * multi keyword positive tests are keyword1_keywords_2
     * negative tests should be situation_gives_exception
    '''

    # TODO: if pressed not working for now, disable tests
    # def test_if_pressed_with_list_access_func_arg(self):
    #     code = textwrap.dedent("""\
    #         define test with k
    #             print 'Press ' k
    #             if k is pressed
    #                 print 'correct'
    #             else
    #                 print 'incorrect'

    #         animals = 'a', 'b', 'c'
    #         call test with animals at random""")

    #     expected = textwrap.dedent("""\
    #     global_scope_ = dict()
    #     def test(k):
    #       local_scope_test_ = {"k": k}
    #       print(f'''Press {local_scope_test_.get("k") or global_scope_.get("k") or k}''')
    #       if_pressed_mapping = {"else": "if_pressed_default_else"}
    #       if_pressed_mapping[(local_scope_test_.get("k") or global_scope_.get("k") or k).data] = 'if_pressed_test_k_'
    #       global if_pressed_test_k_
    #       def if_pressed_test_k_():
    #         print(f'''correct''')
    #       if_pressed_mapping['else'] = 'if_pressed_test_else_'
    #       global if_pressed_test_else_
    #       def if_pressed_test_else_():
    #         print(f'''incorrect''')
    #       extensions.if_pressed(if_pressed_mapping)
    #     global_scope_["animals"] = Value([Value('a'), Value('b'), Value('c')])
    #     test(random.choice((global_scope_.get("animals") or animals).data))""")

    #     self.multi_level_tester(code=code, expected=expected, max_level=15)

    # #
    # function tests
    #
    # Gives a type error, ignoring for now (FH, June 2025)
    # def test_simple_function(self):
    #     code = textwrap.dedent("""\
    #     define simple_function_1 with parameter
    #         print "simple_function_1 - 1"
    #         m = "simple_function_1 - 2"
    #         print m
    #     define simple_function_2 with param
    #         print "simple_function_2 - 1"
    #         print param
    #     define simple_function_3 with param_a, param_b, param_c
    #         if param_a = "A"
    #             print "simple_function_3 - 1"
    #             print param_b
    #         else
    #             print "simple_function_3 - 2"
    #             if param_a = "B"
    #                 print "simple_function_3 - 2A"
    #                 print param_b
    #             else
    #                 print "simple_function_3 - 2B"
    #                 print param_c
    #     a = "test1"
    #     call simple_function_3 with "A", a, 1
    #     call simple_function_3 with "B", a, 1
    #     call simple_function_3 with "C", a, 1""")
    #
    #     expected = textwrap.dedent("""\
    #     def simple_function_1(parameter):
    #       print(f'''simple_function_1 - 1''')
    #       m = Value('simple_function_1 - 2')
    #       print(f'''{m}''')
    #     def simple_function_2(param):
    #       print(f'''simple_function_2 - 1''')
    #       print(f'''{param}''')
    #     def simple_function_3(param_a, param_b, param_c):
    #       if param_a.data == 'A':
    #         print(f'''simple_function_3 - 1''')
    #         print(f'''{param_b}''')
    #       else:
    #         print(f'''simple_function_3 - 2''')
    #         if param_a.data == 'B':
    #           print(f'''simple_function_3 - 2A''')
    #           print(f'''{param_b}''')
    #         else:
    #           print(f'''simple_function_3 - 2B''')
    #           print(f'''{param_c}''')
    #     a = Value('test1')
    #     simple_function_3(Value('A'), a, Value(1, num_sys='Latin'))
    #     simple_function_3(Value('B'), a, Value(1, num_sys='Latin'))
    #     simple_function_3(Value('C'), a, Value(1, num_sys='Latin'))""")
    #
    #     output = textwrap.dedent("""\
    #     simple_function_3 - 1
    #     test1
    #     simple_function_3 - 2
    #     simple_function_3 - 2A
    #     test1
    #     simple_function_3 - 2
    #     simple_function_3 - 2B
    #     1""")
    #
    #     self.multi_level_tester(
    #         code=code,
    #         expected=expected,
    #         output=output,
    #         unused_allowed=True,
    #         max_level=16
    #     )

    def test_function_use(self):
        code = textwrap.dedent("""\
        define func with n1, n2
            return n1 + n2

        print call func with 1, 2""")

        expected = self.dedent(
            "def func(n1, n2):",
            (self.return_transpiled(
                f"{{localize({self.sum_transpiled('n1', 'n2')}, num_sys=get_num_sys(n1))}}"), '  '),
            "print(f'''{func(Value(1, num_sys='Latin'), Value(2, num_sys='Latin'))}''')")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            expected=expected
        )

    def test_function_with_arabic_var(self):
        code = textwrap.dedent(f"""\
             define test_function_1
                 i = ١
                 return "Test function " i
             print call test_function_1""")

        expected = self.dedent(
            "def test_function_1():",
            ("i = Value(1, num_sys='Arabic')", "  "),
            (self.return_transpiled('Test function {i}'), "  "),
            "print(f'''{test_function_1()}''')")

        self.multi_level_tester(
            code=code,
            expected=expected,
            output="Test function ١",
            max_level=12
        )

    def test_undefined_function_without_params(self):
        code = textwrap.dedent("""\
        call func""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UndefinedFunctionException
        )

    def test_undefined_function_with_params(self):
        code = textwrap.dedent("""\
        print call func with 1, 2""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UndefinedFunctionException
        )

    def test_function_use_builtin_name(self):
        code = textwrap.dedent("""\
            define sum with n1, n2
                return n1 + n2

            print call sum with 1, 2""")

        return_arg = f"{{localize({self.sum_transpiled('n1', 'n2')}, num_sys=get_num_sys(n1))}}"
        expected = self.dedent(
            "def sum(n1, n2):",
            (self.return_transpiled(return_arg), '  '),
            "print(f'''{sum(Value(1, num_sys='Latin'), Value(2, num_sys='Latin'))}''')")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            expected=expected
        )

    def test_function_returns_number(self):
        code = textwrap.dedent("""\
        define func with n1, n2
            return n1 + n2

        a = call func with 1, 2
        print a + 3""")

        return_arg = f"{{localize({self.sum_transpiled('n1', 'n2')}, num_sys=get_num_sys(n1))}}"
        expected = self.dedent(
            "def func(n1, n2):",
            (self.return_transpiled(return_arg), '  '),
            "a = func(Value(1, num_sys='Latin'), Value(2, num_sys='Latin'))",
            f"print(f'''{{localize({self.sum_transpiled('a', '3')}, num_sys=get_num_sys(a))}}''')")

        self.multi_level_tester(
            code=code,
            expected=expected,
            output='6',
            max_level=12,
        )

    def test_function_returns_arabic_number(self):
        code = textwrap.dedent("""\
        define func with n1, n2
            return n1 + n2

        a = call func with ٣, ١
        print a + 3""")

        return_arg = f"{{localize({self.sum_transpiled('n1', 'n2')}, num_sys=get_num_sys(n1))}}"
        expected = self.dedent(
            "def func(n1, n2):",
            (self.return_transpiled(return_arg), '  '),
            "a = func(Value(3, num_sys='Arabic'), Value(1, num_sys='Arabic'))",
            f"print(f'''{{localize({self.sum_transpiled('a', '3')}, num_sys=get_num_sys(a))}}''')")

        self.multi_level_tester(
            code=code,
            max_level=12,
            output='٧',
            expected=expected,
        )

    def test_too_many_parameters(self):
        code = textwrap.dedent("""\
        define func with n1, n2
            return n1 + n2

        print call func with 1, 2, 3""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.WrongNumberofArguments
        )

    def test_too_few_parameters(self):
        code = textwrap.dedent("""\
        define func with n1, n2
            return n1 + n2

        print call func with 1""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.WrongNumberofArguments
        )

    def test_unused_function_use_builtin_name(self):
        code = textwrap.dedent("""\
        define sum with n1, n2
            return n1 + n2

        print 'hola!'""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UnusedVariableException
        )

    def test_function_calls_another_function(self):
        code = textwrap.dedent("""\
        a = 1

        define add_one with n1
            print n1 + 1

        define add_another with n1
            call add_one with n1

        call add_another with a""")

        expected = self.dedent("""\
            a = Value(1, num_sys='Latin')
            def add_one(n1):
              print(f'''{localize(sum_with_error(n1, 1, \"""Runtime Values Error\"""), num_sys=get_num_sys(n1))}''')
            def add_another(n1):
              add_one(n1)
            add_another(a)""")

        self.multi_level_tester(
            code=code,
            expected=expected,
            output='2',
            max_level=12,
            unused_allowed=True
        )

    def test_unused_global_var_named_as_function_arg(self):
        code = textwrap.dedent("""\
        define add with n
            return n + 1
        n is 10
        print call add with 2""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UnusedVariableException
        )

    def test_unused_function_arg_named_as_global_var(self):
        code = textwrap.dedent("""\
        define add with n
            x is 1
            return x + 1

        x is 10
        print x
        print call add with 2""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UnusedVariableException
        )

    def test_unused_global_var_named_as_function_local_var(self):
        code = textwrap.dedent("""\
            define add
                x is 1
                print x + 1
            x is 10
            call add""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UnusedVariableException
        )

    def test_unused_function_local_var_named_as_global_var(self):
        code = textwrap.dedent("""\
        define add
            x is 1
            print 'one'
        x is 10
        print x
        call add""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UnusedVariableException
        )

    def test_local_var_cannot_be_used_in_global_scope(self):
        code = textwrap.dedent("""\
        define add
            x is 5
            print x
        print call add
        print x + 1""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=hedy.exceptions.UndefinedVarException
        )

    def test_global_var_can_be_used_in_local_scope_if_defined_before(self):
        code = textwrap.dedent("""\
        x is 5
        define add
            print x
        call add""")

        expected = textwrap.dedent("""\
        x = Value(5, num_sys='Latin')
        def add():
          print(f'''{x}''')
        add()""")

        self.multi_level_tester(
            code=code,
            expected=expected,
            max_level=12,
        )

    def test_global_var_used_in_local_scope_if_defined_after_gives_error(self):
        code = textwrap.dedent("""\
        define add
            print x
        x is 5
        call add""")

        self.multi_level_tester(
            code=code,
            max_level=12,
            skip_faulty=False,
            exception=exceptions.UnquotedTextException,
        )

    # TODO: if pressed not working for now, disable tests

    # def test_global_var_should_not_shadow_local_var_in_func(self):
    #     code = textwrap.dedent("""\
    #     define turn
    #         if x is pressed
    #             print 'good'
    #         else
    #             print 'bad'
    #     call turn
    #     x is 1 + 1
    #     print x""")

    #     expected = textwrap.dedent("""\
    #     global_scope_ = dict()
    #     def turn():
    #       local_scope_turn_ = dict()
    #       if_pressed_mapping = {"else": "if_pressed_default_else"}
    #       if_pressed_mapping['x'] = 'if_pressed_turn_x_'
    #       global if_pressed_turn_x_
    #       def if_pressed_turn_x_():
    #         print(f'''good''')
    #       if_pressed_mapping['else'] = 'if_pressed_turn_else_'
    #       global if_pressed_turn_else_
    #       def if_pressed_turn_else_():
    #         print(f'''bad''')
    #       extensions.if_pressed(if_pressed_mapping)
    #     turn()
    #     global_scope_["x"] = Value(1 + 1, num_sys='Latin')
    #     print(f'''{global_scope_.get("x") or x}''')""")

    #     self.multi_level_tester(
    #         code=code,
    #         expected=expected,
    #         max_level=12,
    #     )

    # def test_if_pressed_in_func(self):
    #     code = textwrap.dedent("""\
    #     define turnz
    #         x is 'a'
    #         if x is pressed
    #             x is 'great'
    #         else
    #             x is 'not great'
    #         print x

    #     call turnz""")

    #     expected = textwrap.dedent("""\
    #         global_scope_ = dict()
    #         def turnz():
    #           local_scope_turnz_ = dict()
    #           local_scope_turnz_["x"] = Value('a')
    #           if_pressed_mapping = {"else": "if_pressed_default_else"}
    #           if_pressed_mapping[(local_scope_turnz_.get("x") or global_scope_.get("x") or x).data] = 'if_pressed_turnz_x_'
    #           global if_pressed_turnz_x_
    #           def if_pressed_turnz_x_():
    #             local_scope_turnz_["x"] = Value('great')
    #           if_pressed_mapping['else'] = 'if_pressed_turnz_else_'
    #           global if_pressed_turnz_else_
    #           def if_pressed_turnz_else_():
    #             local_scope_turnz_["x"] = Value('not great')
    #           extensions.if_pressed(if_pressed_mapping)
    #           print(f'''{local_scope_turnz_.get("x") or global_scope_.get("x") or x}''')
    #         turnz()""")

    #     self.multi_level_tester(
    #         code=code,
    #         expected=expected,
    #         max_level=12,
    #     )

    # def test_if_pressed_in_func_with_arg(self):
    #     code = textwrap.dedent("""\
    #     define make_turn with direction
    #         if direction = 'left'
    #             turn -90
    #         else
    #             turn 90
    #     if l is pressed
    #         call make_turn with 'left'
    #     else
    #         call make_turn with 'right'""")

    #     expected = textwrap.dedent('''\
    #     global_scope_ = dict()
    #     def make_turn(direction):
    #       local_scope_make_turn_ = {"direction": direction}
    #       if (local_scope_make_turn_.get("direction") or global_scope_.get("direction") or direction).data == 'left':
    #         __trtl = number_with_error(-90, """Runtime Value Error""")
    #         t.right(min(600, __trtl) if __trtl > 0 else max(-600, __trtl))
    #       else:
    #         __trtl = number_with_error(90, """Runtime Value Error""")
    #         t.right(min(600, __trtl) if __trtl > 0 else max(-600, __trtl))
    #     if_pressed_mapping = {"else": "if_pressed_default_else"}
    #     if_pressed_mapping['l'] = 'if_pressed_l_'
    #     global if_pressed_l_
    #     def if_pressed_l_():
    #       make_turn(Value('left'))
    #     if_pressed_mapping['else'] = 'if_pressed_else_'
    #     global if_pressed_else_
    #     def if_pressed_else_():
    #       make_turn(Value('right'))
    #     extensions.if_pressed(if_pressed_mapping)''')

    #     self.multi_level_tester(
    #         code=code,
    #         expected=expected,
    #         max_level=12,
    #     )

    # def test_if_pressed_in_two_funcs(self):
    #     code = textwrap.dedent("""\
    #     x is 'a'
    #     define turnz
    #         if x is pressed
    #             x is 'turn'
    #         else
    #             x is 'do not turn'
    #         print x

    #     define forwardz
    #         if x is pressed
    #             x is 'go forward'
    #         else
    #             x is 'do not go forward'
    #         print x

    #     call turnz
    #     call forwardz
    #     print x""")

    #     expected = textwrap.dedent("""\
    #     global_scope_ = dict()
    #     global_scope_["x"] = Value('a')
    #     def turnz():
    #       local_scope_turnz_ = dict()
    #       if_pressed_mapping = {"else": "if_pressed_default_else"}
    #       if_pressed_mapping[(local_scope_turnz_.get("x") or global_scope_.get("x") or x).data] = 'if_pressed_turnz_x_'
    #       global if_pressed_turnz_x_
    #       def if_pressed_turnz_x_():
    #         local_scope_turnz_["x"] = Value('turn')
    #       if_pressed_mapping['else'] = 'if_pressed_turnz_else_'
    #       global if_pressed_turnz_else_
    #       def if_pressed_turnz_else_():
    #         local_scope_turnz_["x"] = Value('do not turn')
    #       extensions.if_pressed(if_pressed_mapping)
    #       print(f'''{local_scope_turnz_.get("x") or global_scope_.get("x") or x}''')
    #     def forwardz():
    #       local_scope_forwardz_ = dict()
    #       if_pressed_mapping = {"else": "if_pressed_default_else"}
    #       if_pressed_mapping[(local_scope_forwardz_.get("x") or global_scope_.get("x") or x).data] = 'if_pressed_forwardz_x_'
    #       global if_pressed_forwardz_x_
    #       def if_pressed_forwardz_x_():
    #         local_scope_forwardz_["x"] = Value('go forward')
    #       if_pressed_mapping['else'] = 'if_pressed_forwardz_else_'
    #       global if_pressed_forwardz_else_
    #       def if_pressed_forwardz_else_():
    #         local_scope_forwardz_["x"] = Value('do not go forward')
    #       extensions.if_pressed(if_pressed_mapping)
    #       print(f'''{local_scope_forwardz_.get("x") or global_scope_.get("x") or x}''')
    #     turnz()
    #     forwardz()
    #     print(f'''{global_scope_.get("x") or x}''')""")

    #     self.multi_level_tester(
    #         code=code,
    #         expected=expected,
    #         max_level=12,
    #     )

    # def test_source_map(self):
    # Gives a type error, ignoring for now (FH, June 2025)
    #     self.maxDiff = None
    #     code = textwrap.dedent("""\
    #         price = 0.0
    #         food = ask 'What would you like to order?'
    #         drink = ask 'What would you like to drink?'
    #         if food is 'hamburger'
    #             price = price + 6
    #         if food is 'pizza'
    #             price = price + 5
    #         if drink is 'water'
    #             price = price + 1
    #         if drink is 'soda'
    #             price = price + 2
    #         print 'That will be ' price ' dollar, please'""")
    #
    #     expected_code = self.dedent(
    #         "price = Value(0, num_sys='Latin')",
    #         self.input_transpiled('food', 'What would you like to order?'),
    #         self.input_transpiled('drink', 'What would you like to drink?'),
    #         '''\
    #         if food.data == 'hamburger':
    #           price = Value(sum_with_error(price, 6, """Runtime Values Error"""), num_sys=get_num_sys(price))
    #         if food.data == 'pizza':
    #           price = Value(sum_with_error(price, 5, """Runtime Values Error"""), num_sys=get_num_sys(price))
    #         if drink.data == 'water':
    #           price = Value(sum_with_error(price, 1, """Runtime Values Error"""), num_sys=get_num_sys(price))
    #         if drink.data == 'soda':
    #           price = Value(sum_with_error(price, 2, """Runtime Values Error"""), num_sys=get_num_sys(price))
    #         print(f\'\'\'That will be {price} dollar, please\'\'\')''')
    #
    #     expected_source_map = {
    #         '1/1-1/6': '1/1-1/6',
    #         '1/1-1/12': '1/1-1/36',
    #         '2/1-2/5': '2/1-2/5',
    #         '2/1-2/43': '2/1-11/33',
    #         '3/1-3/6': '12/1-12/6',
    #         '3/1-3/44': '12/1-21/35',
    #         '4/4-4/8': '3/20-3/24',
    #         '4/4-4/23': '22/4-22/28',
    #         '5/5-5/10': '25/1-25/6',
    #         '5/13-5/18': '27/1-27/6',
    #         '5/5-5/25': '23/1-23/98',
    #         '4/1-5/34': '22/1-23/100',
    #         '6/4-6/8': '5/3-5/7',
    #         '6/4-6/19': '24/4-24/24',
    #         '7/5-7/10': '29/1-29/6',
    #         '7/13-7/18': '1/1-1/6',
    #         '7/5-7/25': '25/1-25/99',
    #         '6/1-7/34': '24/1-25/101',
    #         '8/4-8/9': '12/42-12/47',
    #         '8/4-8/20': '26/4-26/25',
    #         '9/5-9/10': '23/1-23/6',
    #         '9/13-9/18': '25/1-25/6',
    #         '9/5-9/25': '27/1-27/98',
    #         '8/1-9/34': '26/1-27/100',
    #         '10/4-10/9': '13/20-13/25',
    #         '10/4-10/19': '28/4-28/24',
    #         '11/5-11/10': '27/1-27/6',
    #         '11/13-11/18': '29/1-29/6',
    #         '11/5-11/25': '29/1-29/99',
    #         '10/1-11/34': '28/1-29/101',
    #         '12/23-12/28': '27/93-27/98',
    #         '12/1-12/46': '30/1-30/50',
    #         '1/1-12/47': '1/1-30/50'
    #     }
    #
    #     self.single_level_tester(code, expected=expected_code)
    #     self.source_map_tester(code=code, expected_source_map=expected_source_map)

    def test_nested_functions(self):
        code = textwrap.dedent("""\
        define simple_function
            define nested_function
                print 1
        call simple_function""")

        expected = textwrap.dedent("""\
        pass
        simple_function()""")

        skipped_mappings = [
            SkippedMapping(SourceRange(1, 1, 3, 34), hedy.exceptions.NestedFunctionException),
        ]

        self.multi_level_tester(
            code=code,
            expected=expected,
            unused_allowed=True,
            skipped_mappings=skipped_mappings,
            max_level=12
        )

    #
    # play tests / music tests
    #
    def test_play_var(self):
        code = textwrap.dedent("""\
            n = 'C4' #
            play n""")

        expected = self.dedent(
            "n = Value('C4')",
            self.play_transpiled('n.data'))

        self.multi_level_tester(
            code=code,
            expected=expected,
            max_level=17)

    def test_play_arabic_number_var(self):
        code = textwrap.dedent("""\
            n is ١١
            play n""")

        expected = self.dedent(
            "n = Value(11, num_sys='Arabic')",
            self.play_transpiled('n.data'))

        self.multi_level_tester(code=code, expected=expected)

    def test_play_keyword_var(self):
        code = textwrap.dedent("""\
            sum is 'C4'
            play sum""")

        expected = self.dedent(
            "_sum = Value('C4')",
            self.play_transpiled('_sum.data'))

        self.multi_level_tester(code=code, expected=expected)

    def test_play_list_access_random(self):
        code = textwrap.dedent("""\
        notes = 'C4', 'E4', 'D4', 'F4', 'G4'
        play notes at random""")

        expected = self.dedent(
            f"notes = Value([Value('C4'), Value('E4'), Value('D4'), Value('F4'), Value('G4')])",
            self.play_transpiled("random.choice(notes.data).data"))

        self.multi_level_tester(
            code=code,
            translate=[],
            skip_faulty=False,
            unused_allowed=True,
            expected=expected,
            max_level=12
        )

    def test_play_list_access_random_repeat(self):
        code = textwrap.dedent("""\
        notes = 1, 2, 3

        repeat 10 times
            play notes at random""")

        expected = self.dedent(
            f"""\
            notes = Value([Value(1, num_sys='Latin'), Value(2, num_sys='Latin'), Value(3, num_sys='Latin')])
            for __i in range({self.int_transpiled(10)}):""",
            (self.play_transpiled('random.choice(notes.data).data'), '  '),
            ("time.sleep(0.1)", '  '))

        self.multi_level_tester(code=code, expected=expected, max_level=12)

    @parameterized.expand(['-', '*', '/'])
    def test_play_calculation(self, op):
        code = textwrap.dedent(f"""\
            note is 34
            play note {op} 1""")
        expected = self.dedent(
            "note = Value(34, num_sys='Latin')",
            self.play_transpiled(f"{self.number_transpiled('note')} {op} {self.number_transpiled(1)}"))

        self.multi_level_tester(code=code, expected=expected)

    @parameterized.expand(['-', '*', '/', '+'])
    def test_play_arabic_calc(self, op):
        code = f"play ٣١ {op} ١"
        expected = self.play_transpiled(f'31 {op} 1')

        self.multi_level_tester(code=code, expected=expected)

    def test_play_calc_with_var(self):
        code = textwrap.dedent(f"""\
            note is 34
            play note + 1""")
        expected = self.dedent(
            "note = Value(34, num_sys='Latin')",
            self.play_transpiled(self.sum_transpiled('note', 1)))

        self.multi_level_tester(code=code, expected=expected)

    def test_play_input(self):
        code = textwrap.dedent("""\
            note = ask 'Give me a note'
            play note""")

        expected = self.dedent(
            self.input_transpiled('note', 'Give me a note'),
            self.play_transpiled('note.data'))

        self.multi_level_tester(code=code, expected=expected, max_level=12)

    def test_play_unquoted_text_gives_error(self):
        code = "play undef"
        self.multi_level_tester(code=code, exception=exceptions.UnquotedAssignTextException)

    #
    # color tests
    #
    @parameterized.expand(hedy.english_colors)
    def test_all_colors(self, color):
        code = f'color "{color}"'
        expected = self.color_transpiled(f'{color}')

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    @parameterized.expand(['zwart', 'blauw', 'bruin', 'grijs', 'groen', 'oranje', 'roze', 'rood', 'wit', 'geel'])
    def test_all_colors_nl(self, color):
        code = f'kleur "{color}"'
        expected = self.color_transpiled(f'{color}', lang='nl')

        self.multi_level_tester(
            code=code,
            expected=expected,
            lang='nl',
            extra_check_function=self.is_turtle()
        )

    def test_color_with_var(self):
        code = textwrap.dedent("""\
            foo is 'white'
            color foo""")
        expected = self.dedent(
            "foo = Value('white')",
            self.color_transpiled('{foo}')
        )

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
        )

    def test_color_with_keyword_var(self):
        code = textwrap.dedent("""\
            sum is 'white'
            color sum""")
        expected = self.dedent(
            "_sum = Value('white')",
            self.color_transpiled('{_sum}')
        )

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=18
        )

    @parameterized.expand(['red', "'red'"])
    def test_color_with_or_without_quotes(self, color):
        code = f"color {color}"

        self.multi_level_tester(
            code=code,
            expected=self.color_transpiled('red'),
            extra_check_function=self.is_turtle(),
            max_level=12,
        )

    def test_color_without_quotes_nl(self):
        code = "kleur blauw"

        self.multi_level_tester(
            code=code,
            expected=self.color_transpiled('blue', lang='nl'),
            extra_check_function=self.is_turtle(),
            lang='nl',
            max_level=12,
        )

    #
    # unquoted text tests
    # Level 12 accepts unquoted text like level 11: an unquoted word is a variable if one is defined,
    # otherwise it is a string. Quoted text has its quotes stripped. Quotes are mandatory from level 13.
    #
    def test_unquoted_text_program_from_issue_6575(self):
        code = textwrap.dedent("""\
            # print, ask, variables
            print 'some text' "or numbers 123"
            answer = ask 'a question?'
            variable = text
            variable_number = 123
            print 'use' variable 'or' variable_number 'in a line'

            # list, for
            list = text, or, a, number, 123
            print 'item from' list at random
            add something to list
            remove something from list
            for element in list
                print element 'is in the list'

            # if, else, elif, repeat
            if variable is text
                if variable_number is 123
                    print 'this'
                elif text in list
                    print 'that'
                else
                    print 'something else'
                    print 'or more'
            repeat 3 times
                print 'repeat this line'

            # and, or
            if variable is text and variable_number is 123
                print 'both are true'
            elif variable is text or variable_number is 123
                print 'only one is true'
            else
                print 'nothing is true'

            #functions
            define a_function
                print 'the function prints this line'

            call a_function

            # music, turtle, sleep, clear
            play C4
            play 28
            turn 360
            forward 100
            color green
            sleep 1
            clear

            # maths
            answer = 5.4+5.4
            answer = 5.4-5.4
            answer = 5.4*5.4
            answer = 5.4/5.4""")

        # `answer` is assigned but never read, which is not what this test is about
        self.multi_level_tester(code=code, unused_allowed=True, max_level=12)

        python = hedy.transpile(code, self.level, unused_allowed=True).code
        for line in [
            "variable = Value('text')",
            "_list.data.append(Value('something'))",
            "_list.data.remove(Value('something'))",
            "if variable.data == 'text':",
            "elif Value('text') in _list.data:",
            "if variable.data == 'text' and variable_number.data == 123:",
            "elif variable.data == 'text' or variable_number.data == 123:",
            "__trtl = f'green'",
        ]:
            self.assertIn(line, python)

    @parameterized.expand([('is', 'hoi'), ('=', 'hoi'), ('is', "'hoi'"), ('=', "'hoi'")])
    def test_assign_text_with_or_without_quotes(self, assign, value):
        code = textwrap.dedent(f"""\
            name {assign} {value}
            print name""")

        expected = textwrap.dedent("""\
            name = Value('hoi')
            print(f'''{name}''')""")

        self.multi_level_tester(code=code, expected=expected, output='hoi', max_level=12)

    def test_assign_unquoted_text_with_spaces_and_quote(self):
        code = textwrap.dedent("""\
            name = it's me
            print name""")

        expected = textwrap.dedent("""\
            name = Value('it\\'s me')
            print(f'''{name}''')""")

        self.multi_level_tester(code=code, expected=expected, output="it's me", max_level=12)

    @parameterized.expand(['hoi', "'hoi'"])
    def test_if_equality_with_or_without_quotes(self, value):
        code = textwrap.dedent(f"""\
            name = hoi
            if name is {value}
                print 'yes'
            else
                print 'no'""")

        expected = textwrap.dedent("""\
            name = Value('hoi')
            if name.data == 'hoi':
              print(f'''yes''')
            else:
              print(f'''no''')""")

        self.multi_level_tester(code=code, expected=expected, output='yes', max_level=12)

    @parameterized.expand(['hoi', "'hoi'"])
    def test_if_and_or_with_or_without_quotes(self, value):
        code = textwrap.dedent(f"""\
            name = hoi
            age = 12
            if name is {value} and age is 12
                print 'both'
            elif name is {value} or age is 12
                print 'one'""")

        expected = textwrap.dedent("""\
            name = Value('hoi')
            age = Value(12, num_sys='Latin')
            if name.data == 'hoi' and age.data == 12:
              print(f'''both''')
            elif name.data == 'hoi' or age.data == 12:
              print(f'''one''')""")

        self.multi_level_tester(code=code, expected=expected, output='both', max_level=12)

    def test_if_not_equal_unquoted_text(self):
        code = textwrap.dedent("""\
            name = hoi
            if name != hallo
                print 'different'""")

        expected = textwrap.dedent("""\
            name = Value('hoi')
            if name.data!='hallo':
              print(f'''different''')""")

        self.multi_level_tester(code=code, expected=expected, output='different', max_level=12)

    @parameterized.expand([('dog', 'fish'), ("'dog'", "'fish'")])
    def test_if_in_not_in_list_with_or_without_quotes(self, in_value, not_in_value):
        code = textwrap.dedent(f"""\
            animals = dog, cat
            if {in_value} in animals
                print 'in'
            if {not_in_value} not in animals
                print 'not in'""")

        expected = textwrap.dedent("""\
            animals = Value([Value('dog'), Value('cat')])
            if Value('dog') in animals.data:
              print(f'''in''')
            if Value('fish') not in animals.data:
              print(f'''not in''')""")

        self.multi_level_tester(code=code, expected=expected, output='in\nnot in', max_level=12)

    @parameterized.expand([('fish', 'dog'), ("'fish'", "'dog'")])
    def test_add_remove_with_or_without_quotes(self, add_value, remove_value):
        code = textwrap.dedent(f"""\
            animals = dog, cat
            add {add_value} to animals
            remove {remove_value} from animals
            for animal in animals
                print animal""")

        expected = self.dedent(
            "animals = Value([Value('dog'), Value('cat')])",
            "animals.data.append(Value('fish'))",
            self.remove_transpiled('animals', "Value('dog')"),
            """\
            for animal in animals.data:
              print(f'''{animal}''')
              time.sleep(0.1)""")

        self.multi_level_tester(code=code, expected=expected, output='cat\nfish', max_level=12)

    # hedyorg/hedy#6741
    @parameterized.expand([("'grey fish'", "Value('grey fish')"), ('"grey fish"', 'Value("grey fish")')])
    def test_add_remove_quoted_text_with_spaces(self, add_value, transpiled_value):
        code = textwrap.dedent(f"""\
            animals = 'big dog', 'cat'
            add {add_value} to animals
            remove 'big dog' from animals
            for animal in animals
                print animal""")

        expected = self.dedent(
            "animals = Value([Value('big dog'), Value('cat')])",
            f"animals.data.append({transpiled_value})",
            self.remove_transpiled('animals', "Value('big dog')"),
            """\
            for animal in animals.data:
              print(f'''{animal}''')
              time.sleep(0.1)""")

        self.multi_level_tester(code=code, expected=expected, output='cat\ngrey fish', max_level=12)

    def test_unquoted_defined_variable_is_used_as_variable(self):
        code = textwrap.dedent("""\
            animal = dog
            other = animal
            animals = cat, fish
            add animal to animals
            if animal in animals
                print 'added'
            remove animal from animals
            if other is animal
                print other""")

        expected = self.dedent(
            "animal = Value('dog')",
            "other = animal",
            "animals = Value([Value('cat'), Value('fish')])",
            "animals.data.append(animal)",
            """\
            if animal in animals.data:
              print(f'''added''')""",
            self.remove_transpiled('animals', 'animal'),
            """\
            if other.data == animal.data:
              print(f'''{other}''')""")

        self.multi_level_tester(code=code, expected=expected, output='added\ndog', max_level=12)

    def test_color_with_unquoted_variable(self):
        code = textwrap.dedent("""\
            foo = white
            color foo""")

        expected = self.dedent(
            "foo = Value('white')",
            self.color_transpiled('{foo}'))

        self.multi_level_tester(
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle(),
            max_level=12,
        )
