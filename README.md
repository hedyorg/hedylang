# Hedy

Hedy is a gradual programming language aimed at teaching programming and teaching Python. It teaches using different levels. The first level just offers printing text and asking for input. This level is meant to introduce learners to the idea of a programming language, and the environment. From there, Hedy builds up to include more complex syntax and additional concepts.

## Parts of Hedy

This repository contains the component that is the Hedy language, while <https://github.com/hedyorg/hedy> contains the website you see when you go to <https://hedy.org/>.

## Getting started

First, install [uv](https://docs.astral.sh/uv/getting-started/installation/), for example using Homebrew on macOS:

```
$ brew install uv
```

After cloning:

```
$ uv run doit test

# Or
$ uv run doit pretest
$ uv run pytest
```

## Running a Hedy program

You can transpile and run a Hedy program from the command line. Pass the level and a file (or `-` to read the program from stdin):

```
$ printf 'naam is Hedy\nprint hallo naam\n' > hello.hedy
$ uv run hedy 2 hello.hedy
hallo Hedy
```

Useful options:

- `--show-preprocessed`: also print the program as the parser sees it, after preprocessing. This is printed even when the program has errors, which helps when an error points to text you didn't write (for example the `else` Hedy adds to an `if` without one)
- `--show-ast`: also print the abstract syntax tree of the program
- `--show-python`: also print the generated Python code
- `--no-run`: only transpile, print the Python code and don't run it
- `--lang nl`: the program uses keywords in another language (default: `en`)
- `--fast`: skip the pauses Hedy adds between commands

Errors are reported with their error code and details, for example `line 1: Invalid error (invalid_command='prnt', level=1, guessed_command='print')`. The full, translated error messages are provided by the Hedy website.

Turtle programs open a window and need `tkinter` (for example `sudo apt install python3-tk`). Programs that use `play` (music) or `pressed` (keyboard input) depend on the website's browser runtime, so they can only be transpiled with `--no-run`.

`python -m hedy` works as well, and installing the package with pip provides the same `hedy` command.

## Releasing new versions

A GitHub Actions Workflow will be automatically release new versions to PyPI if the file named `VERSION` in the root of the repository is changed to a different version number.

After publishing it becomes available for use in https://github.com/hedyorg/hedy, by updating `requirements.txt` to reference the new version.

## Thanks to all Contributors

Thank you very much for taking your time to help Hedy.

[![Contributors](https://contrib.rocks/image?repo=hedyorg/hedy)]([https://github.com/codemaniac-sahil/news-webapp-api](https://github.com/hedyorg/hedy)https://github.com/hedyorg/hedy/graphs/contributors)
<p align="right">(<a href="#top">🔼 Back to top</a>)</p>
