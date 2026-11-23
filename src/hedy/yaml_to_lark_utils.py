import collections
import copy
import os
from ruamel import yaml


def extract_Lark_grammar_from_yaml():
    """Creates a lark file in ../grammars/ for  all yaml files located in ./data/keywords/.
    If a keyword is not yet translated, it will use the English translation of the keyword

    Args:
        only_new_lang (bool, optional): Specifies if only a lark file should be created for a new keyword language
        or for all languages. Defaults to True.
    """
    dirname = os.path.dirname(__file__)
    input_path = os.path.join(dirname, 'data', 'keywords')
    current_grammar_path = os.path.join(dirname, 'data', 'grammars')

    yaml_languages = [f.replace('.yaml', '') for f in os.listdir(input_path) if
                      os.path.isfile(os.path.join(input_path, f)) and f.endswith('.yaml')]

    template_lark = os.path.join(current_grammar_path, 'keywords-template.lark')
    with open(template_lark, 'r', encoding='utf-8') as f:
        template = f.read()

    for yaml_lang in yaml_languages:
        yaml_filesname_with_path = os.path.join(input_path, yaml_lang + '.yaml')
        default_yaml_with_path = os.path.join(input_path, 'en' + '.yaml')

        with open(default_yaml_with_path, 'r', encoding='utf-8') as stream:
            en_command_combinations = yaml.YAML(typ='safe', pure=True).load(stream)

        with open(yaml_filesname_with_path, 'r', encoding='utf-8') as stream:
            command_combinations = yaml.YAML(typ='safe', pure=True).load(stream)

        # Create an empty dictionary -> fill with english keywords and then overwrite all translated keywords
        translations = collections.defaultdict(lambda: 'Unknown Exception')
        translations.update(en_command_combinations)
        translations.update(command_combinations)

        translation_copy = copy.deepcopy(translations)
        for k, v in translation_copy.items():
            if yaml_lang == "ar":
                mixed_tatweel_in = ''.join([' "ـ"* ' + '"' + lang + '"' for lang in v]) + ' "ـ"* '
                translations[k] = mixed_tatweel_in
            else:
                # other languages need their translations surrounded by "'s
                translations[k] = '"' + v + '"'

            # we use | if we have multiple options, such as repete and repète
            if "|" in v:
                valid_translation = ""
                options = v.split("|")
                valid_translation = ' | '.join(['"' + option + '"' for option in options])
                translations[k] = valid_translation

        translated_template = template.format(**translations)

        lark_filesname_with_path = os.path.join(current_grammar_path, 'keywords-' + yaml_lang + '.lark')

        with open(lark_filesname_with_path, 'w', encoding='utf-8') as f:
            f.write(translated_template)



def _grammar_paths():
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, 'data', 'keywords'), os.path.join(dirname, 'data', 'grammars')


def _lark_file_for(grammar_path, yaml_file):
    return os.path.join(grammar_path, 'keywords-' + yaml_file[:-len('.yaml')] + '.lark')


def missing_grammars():
    """Return the languages that have a keyword YAML but no keywords-<lang>.lark file."""
    input_path, grammar_path = _grammar_paths()
    return sorted(
        f[:-len('.yaml')] for f in os.listdir(input_path)
        if f.endswith('.yaml') and not os.path.exists(_lark_file_for(grammar_path, f)))


def grammars_need_update():
    """Return True if a keywords-<lang>.lark file is missing, or older than the files it is generated from.

    The keyword grammars are generated from data/keywords/*.yaml and data/grammars/keywords-template.lark
    and are not checked in, so a fresh checkout (or a change in a keyword YAML) needs a regeneration.
    """
    if missing_grammars():
        return True

    input_path, grammar_path = _grammar_paths()
    template = os.path.join(grammar_path, 'keywords-template.lark')
    en_yaml = os.path.join(input_path, 'en.yaml')
    shared_sources_mtime = max(os.path.getmtime(template), os.path.getmtime(en_yaml))

    for f in os.listdir(input_path):
        if not f.endswith('.yaml'):
            continue
        source_mtime = max(shared_sources_mtime, os.path.getmtime(os.path.join(input_path, f)))
        if os.path.getmtime(_lark_file_for(grammar_path, f)) < source_mtime:
            return True
    return False


def is_source_checkout():
    """Return True if Hedy runs from a checkout of the repository (src/hedy next to dodo.py)."""
    return os.path.exists(os.path.join(os.path.dirname(__file__), '..', '..', 'dodo.py'))


def ensure_grammars_up_to_date():
    """Make sure the keyword grammars exist, and in a source checkout, that they are up to date.

    In a source checkout the grammars are not checked in, so they are generated when missing or older
    than their sources; any failure to do so is an error. An installed package ships the generated
    grammars and is never regenerated (its file timestamps say nothing about which file is newer),
    but a missing grammar is still an error: that language would otherwise silently fall back to English.
    """
    if is_source_checkout():
        if grammars_need_update():
            extract_Lark_grammar_from_yaml()
        return

    missing = missing_grammars()
    if missing:
        raise RuntimeError(f'The keyword grammars for {", ".join(missing)} are missing from the installed package.')


if __name__ == '__main__':
    # Used by `doit lark` (see dodo.py)
    extract_Lark_grammar_from_yaml()
