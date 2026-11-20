"""Run a Hedy program from the command line.

Usage:
    hedy LEVEL FILE            (installed script, e.g. `uv run hedy ...`)
    python -m hedy LEVEL FILE [--lang LANG] [--show-python] [--no-run] [--fast]

FILE may be '-' to read the program from stdin.

Turtle programs need tkinter and open a window. Music (`play`) and keyboard
(`pressed`) programs rely on the browser runtime of the Hedy website and
cannot be run here; they can still be transpiled with --no-run.
"""

import argparse
import re
import sys
import warnings

# The grammar merger warns about duplicated rules at higher levels; that is noise for users.
warnings.filterwarnings('ignore', category=UserWarning, module=r'hedy\.grammar')

import hedy  # noqa: E402
from hedy import exceptions, lang_utils  # noqa: E402

# Arguments that are either shown separately or are too noisy to print.
_HIDDEN_ARGUMENTS = {'line_number', 'location', 'fixed_code', 'fixed_result'}


def format_hedy_error(ex: exceptions.HedyException) -> str:
    """Describe a HedyException without needing the website's translations."""
    args = ex.arguments
    line = args.get('line_number')
    if line is None and isinstance(args.get('location'), (tuple, list)) and args['location']:
        line = args['location'][0]

    prefix = f'line {line}: ' if line is not None else ''
    details = ', '.join(f'{k}={v!r}' for k, v in args.items() if k not in _HIDDEN_ARGUMENTS)
    message = f'{prefix}{ex.error_code} error'
    if details:
        message += f' ({details})'

    fixed_code = args.get('fixed_code')
    if fixed_code:
        message += '\n\nSuggested fix:\n' + fixed_code
    return message


def build_program(result: hedy.ParseResult, fast: bool) -> str:
    code = lang_utils.NORMAL_PREFIX_CODE
    if result.has_turtle:
        code += lang_utils.TURTLE_PREFIX_CODE
    code += result.code
    if result.has_turtle:
        code += '\nturtle.done()\n'
    if fast:
        # This is the same approach as HedyTester.run_code in tests/Tester.py, which uses this regex
        # to keep the tests fast.
        # Note: this regex works on the transpiled Python, so it is fragile. It also removes the
        # pauses from the programmer's own `sleep` commands (not just the ones Hedy adds itself),
        # and it can match `time.sleep(` inside strings in the program.
        # TODO: refactor to a `fast` option in the transpiler that leaves out only the automatic
        # pauses (see add_sleep_to_command and the pause after `play` in hedy/__init__.py).
        code = re.sub(r'time\.sleep\([^\n]*\)', 'pass', code)
    return code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='hedy', description='Transpile and run a Hedy program.')
    parser.add_argument('level', type=int, help='Hedy level of the program (e.g. 1-18)')
    parser.add_argument('file', help="Hedy source file, or '-' for stdin")
    parser.add_argument('--lang', default='en', help="language of the keywords (default: 'en')")
    parser.add_argument('--show-python', action='store_true', help='print the generated Python code')
    parser.add_argument('--no-run', action='store_true', help='only transpile, do not run')
    parser.add_argument('--fast', action='store_true', help='skip the pauses Hedy adds between commands')
    args = parser.parse_args(argv)

    try:
        source = sys.stdin.read() if args.file == '-' else open(args.file, encoding='utf-8').read()
    except OSError as e:
        print(f'Cannot read {args.file}: {e.strerror}', file=sys.stderr)
        return 2

    try:
        result = hedy.transpile(source, args.level, lang=args.lang)
    except exceptions.HedyException as ex:
        print(format_hedy_error(ex), file=sys.stderr)
        return 1

    if args.show_python or args.no_run:
        print(result.code)
        if args.no_run:
            return 0
        print('-' * 40)

    unsupported = [name for name, used in (('music (play)', result.has_music),
                                           ('keyboard input (pressed)', result.has_pressed)) if used]
    if unsupported:
        print(f"This program uses {' and '.join(unsupported)}, which only works on the Hedy website. "
              'Use --no-run to see the generated Python.', file=sys.stderr)
        return 1

    if result.has_turtle:
        try:
            import tkinter  # noqa: F401
        except ImportError:
            print('This is a turtle program, which needs tkinter '
                  '(e.g. `sudo apt install python3-tk`).', file=sys.stderr)
            return 1

    try:
        exec(build_program(result, args.fast), {'__name__': '__hedy__'})
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        # Runtime errors from the generated code (e.g. a wrong value type, or an index out of range).
        print(f'Runtime error: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
