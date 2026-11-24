import os
from os import path
from glob import glob
import subprocess
import sys
import platform

def task_lark():
    """Generate Lark grammar files based on keyword information in keyword YAMLs."""
    script = 'src/hedy/yaml_to_lark_utils.py'
    keyword_yamls = glob('src/hedy/data/keywords/*.yaml')
    grammars = ['src/hedy/data/grammars/keywords-' + replace_ext(path.basename(y), '.lark') for y in keyword_yamls]

    return dict(
        title=lambda _: 'Create Lark grammar files',
        file_dep=[
            script,
            'src/hedy/data/grammars/keywords-template.lark',
            *keyword_yamls,
        ],
        actions=[
            [python3, script],
        ],
        targets=grammars,
    )


def task_pretest():
    """Collect all tasks that need to happen before testing can work."""
    return dict(
        title=lambda _: 'Prepare the project for testing',
        task_dep=['lark'],
        actions=[
        ],
    )


def task_build():
    """Build the project."""
    return dict(
        title=lambda _: 'Build the project',
        task_dep=['lark'],
        actions=[
            # Clear dist/, so it only contains the files that are going to be tested and published
            ['uv', 'build', '--clear'],
        ],
        verbosity=Verbosity.LIVE,
    )


def task_test():
    """Run the tests."""
    return dict(
        title=lambda _: 'Run the tests',
        task_dep=['pretest'],
        actions=[
            ['uv', 'run', 'pytest'],
        ],
        verbosity=Verbosity.LIVE,
    )


def task_test_wheel():
    """Build the wheel, install it in a clean environment and run the tests against it."""
    return dict(
        title=lambda _: 'Run the tests against the built wheel',
        task_dep=['build'],
        actions=[test_wheel],
        verbosity=Verbosity.LIVE,
    )


def task_publish():
    """Publish the wheel that was built and tested by test_wheel."""
    return dict(
        title=lambda _: 'Publish the project',
        task_dep=['test_wheel'],
        actions=[
            ['uv', 'publish'],
        ],
    )


class Verbosity:
    LIVE = 2


WHEEL_VENV = '.venv-wheel'

# What a consumer of the package does. The Dutch keyword fails if the keyword grammars are not in the wheel.
SMOKE_TEST = '''
import sys
import hedy

assert hedy.__file__.startswith(sys.prefix), f'Not testing the installed wheel but {hedy.__file__}'
assert hedy.transpile('print hello', 1).code == "print(f'hello')"
assert 'input(' in hedy.transpile('vraag hoe heet je', 1, lang='nl').code
print(f'Smoke test passed, using {hedy.__file__}')
'''


def test_wheel():
    """Install the wheel in dist/ like a consumer would, and run the tests against it.

    The tests run from the root of the repository. They import the installed package and not src/hedy,
    because the project itself is not installed in this environment (the smoke test checks this).
    """
    def run(*args, **kwargs):
        return subprocess.run(args, check=True, **kwargs)

    [wheel] = glob('dist/*.whl')
    python = path.join(WHEEL_VENV, *(['Scripts', 'python.exe'] if sys.platform == 'win32' else ['bin', 'python']))

    run('uv', 'venv', '--clear', '--python', python3, WHEEL_VENV)

    # First only the wheel and its own dependencies: this must be enough for a consumer
    run('uv', 'pip', 'install', '--python', python, wheel)
    run(python, '-c', SMOKE_TEST)

    # Then add the (locked) development dependencies to be able to run the tests
    requirements = run('uv', 'export', '--locked', '--quiet', '--all-extras', '--no-emit-project', stdout=subprocess.PIPE)
    run('uv', 'pip', 'install', '--python', python, '--requirements', '-', input=requirements.stdout)
    run(python, '-c', SMOKE_TEST)
    run(python, '-m', 'pytest')


# The current Python interpreter, use to run other Python scripts as well
python3 = sys.executable

def replace_ext(filename, ext):
    """Replace the extension of a filename."""
    return path.splitext(filename)[0] + ext
