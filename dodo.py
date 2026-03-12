import os
from os import path
from glob import glob
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
        task_dep=['lark', 'test'],
        actions=[
            ['uv', 'build'],
        ],
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


def task_publish():
    """Publish the project.

    We *must* run the tests before publishing, because running the tests will
    generate the *-Total grammar files.
    """
    return dict(
        title=lambda _: 'Publish the project',
        task_dep=['build', 'test'],
        actions=[
            ['uv', 'publish'],
        ],
    )


class Verbosity:
    LIVE = 2

# The current Python interpreter, use to run other Python scripts as well
python3 = sys.executable

def replace_ext(filename, ext):
    """Replace the extension of a filename."""
    return path.splitext(filename)[0] + ext
