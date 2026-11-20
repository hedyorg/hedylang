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

The keyword grammars (`src/hedy/data/grammars/keywords-<lang>.lark`) are generated from the keyword translations in `src/hedy/data/keywords/*.yaml` and are not checked in. They are generated automatically when `hedy` is imported and they are missing or older than the YAML files. You can also generate them explicitly with `uv run doit lark`.

## Releasing new versions

A GitHub Actions Workflow will be automatically release new versions to PyPI if the file named `VERSION` in the root of the repository is changed to a different version number.

To build the package locally, use `uv run doit build` rather than plain `uv build`. Plain `uv build` does not import `hedy`, so on a fresh clone the generated keyword grammars would be missing from the package.

After publishing it becomes available for use in https://github.com/hedyorg/hedy, by updating `requirements.txt` to reference the new version.

## Thanks to all Contributors

Thank you very much for taking your time to help Hedy.

[![Contributors](https://contrib.rocks/image?repo=hedyorg/hedy)]([https://github.com/codemaniac-sahil/news-webapp-api](https://github.com/hedyorg/hedy)https://github.com/hedyorg/hedy/graphs/contributors)
<p align="right">(<a href="#top">🔼 Back to top</a>)</p>
