#
# Open Source Voting Translation Manager (OTM) - election translations
# Copyright (C) 2020  Chris Jerdonek
#
# This file is part of Open Source Voting Translation Manager (OTM).
#
# OTM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import functools
import json
from pathlib import Path
import sys

import yaml


LANG_CODE_EN = 'en'
LINES_CONTEXT = 6

TRANSLATIONS_PATH = Path('translations.json')


def _log(text):
    print(text, file=sys.stderr)


def read_yaml(path):
    with open(path) as f:
        data = yaml.safe_load(f)

    return data


def to_yaml(data):
    """
    Convert the data to a string of yaml.
    """
    # Pass allow_unicode=True so that string values will use Unicode
    # characters rather than being escaped for ascii.
    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


def check_or_update(target_path, new_text, check_mode=False):
    """
    Args:
      target_path: a Path object.
      check_mode: if True, only check that file contents match.  Don't
        actually write the new file contents.
    """
    if not check_mode:
        target_path.write_text(new_text)
        return

    current_text = target_path.read_text()
    if current_text == new_text:
        _log(f'file up-to-date: {target_path}')
        return

    current_lines, new_lines = (
        text.splitlines(keepends=True) for text in (current_text, new_text)
    )
    error_lines = [
        f'ERROR! file not up-to-date: {target_path}',
        'Line counts:',
        f'  current: {len(current_lines)}',
        f'      new: {len(new_lines)}',
    ]

    for line_index, (current_line, new_line) in enumerate(zip(current_lines, new_lines)):
        if current_line != new_line:
            line_no = line_index + 1
            # Show leading context in the error message.
            start_line_index = max(0, line_index - LINES_CONTEXT)
            start_line_no = start_line_index + 1

            error_lines.extend([
                '',
                f'First mismatch at: line {line_no} (1-based)',
                '',
                f'Showing current lines with leading context (lines {start_line_no} to {line_no}):',
                '',
                f'--- START CONTEXT ---',
            ])
            error_lines.extend(current_lines[start_line_no:line_index])
            error_lines.extend([
                current_line.rstrip(),
                f'*** MISMATCHED LINE {line_no} (above and below) ***',
                new_line.rstrip(),
                '',
                f'Showing mismatched line {line_no} (formatted):',
                f'  current: {current_line!r}',
                f'      new: {new_line!r}',
            ])
            break

    error_text = '\n'.join(error_lines)

    raise RuntimeError(error_text)


def read_index():
    data = read_yaml('index.yml')

    languages_data = data['languages']
    phrases_data = data['phrases']

    return (languages_data, phrases_data)


def get_lang_path(lang_code):
    return Path('languages') / f'{lang_code}.yml'


def read_lang_file(path):
    if not path.exists():
        return {}

    return read_yaml(path)


def iter_source_phrases(source_phrases):
    """
    Args:
      source_phrases: the value of the "phrases" key in the source
        `index.yml` file.
    """
    for phrase_id, phrase_data in source_phrases.items():
        new_phrase_data = {
            f'_{key}': value for key, value in phrase_data.items()
        }

        yield (phrase_id, new_phrase_data)


def update_lang_phrases(target_phrases, source_phrases, lang_code, lang_name):
    """
    Args:
      source_phrases: the value of the "phrases" key in the source
        `index.yml` file.
      lang_code: a 2-letter language code (other than English / "en").
      lang_name: the name of the language in English, e.g. "English" or
        "Spanish".
    """
    assert lang_code != LANG_CODE_EN

    translated_key = lang_name.lower()

    for phrase_id, phrase_data in iter_source_phrases(source_phrases):
        target_phrase = target_phrases.setdefault(phrase_id, {})
        target_phrase.update(phrase_data)

        # Add a placeholder key-value for the translation, if a value
        # isn't already present.
        target_phrase.setdefault(translated_key, '')


def update_language_file(source_phrases, languages_data, lang_code,
    check_mode=False):
    """
    Args:
      source_phrases: the value of the "phrases" key in the source
        `index.yml` file.
      check_mode: if True, only check that the file is updated.  Don't
        actually update it.
    """
    language_data = languages_data[lang_code]
    lang_name = language_data['name']

    lang_path = get_lang_path(lang_code)
    data = read_lang_file(lang_path)

    data['_meta'] = {
        'language': lang_name
    }
    target_phrases = data.setdefault('phrases', {})

    update_lang_phrases(target_phrases, source_phrases, lang_code=lang_code,
        lang_name=lang_name)

    updated_text = to_yaml(data)

    check_or_update(lang_path, new_text=updated_text, check_mode=check_mode)


def update_from_index(check_mode=False):
    """
    Args:
      check_mode: if True, only check that the files to update are updated.
        Don't actually update them.
    """
    languages_data, source_phrases = read_index()

    lang_codes = sorted(languages_data)
    lang_codes.remove(LANG_CODE_EN)

    for lang_code in lang_codes:
        update_language_file(source_phrases, languages_data, lang_code=lang_code,
            check_mode=check_mode)


def _build_lang(lang_code, lang_name, translations_data):
    lang_path = get_lang_path(lang_code)
    data = read_lang_file(lang_path)
    try:
        phrases_data = data['phrases']
    except KeyError:
        raise RuntimeError(lang_path, phrases_data)

    for phrase_id, phrase_data in phrases_data.items():
        translation_data = translations_data[phrase_id]

        phrase_key = lang_name.lower()
        try:
            text = phrase_data[phrase_key]
        except KeyError:
            msg = f'key {phrase_key!r} missing from phrase data: {phrase_data!r}'
            raise RuntimeError(msg) from None

        translation_data[lang_code] = text


def build_json(check_mode=False):
    """
    Args:
      check_mode: if True, only check that files are built.  Don't actually
        build them.
    """
    languages_data, phrases_data = read_index()

    translations_data = {}

    for phrase_id, phrase_data in iter_source_phrases(phrases_data):
        phrase_english = phrase_data.pop('_text')

        phrase_data[LANG_CODE_EN] = phrase_english

        translations_data[phrase_id] = phrase_data

    lang_codes = sorted(languages_data)
    # We are done processing English.
    lang_codes.remove(LANG_CODE_EN)

    for lang_code in lang_codes:
        lang_data = languages_data[lang_code]
        lang_name = lang_data['name']

        try:
            _build_lang(lang_code, lang_name=lang_name, translations_data=translations_data)
        except:
            msg = f'error while processing file for language: {lang_code!r}'
            raise RuntimeError(msg)

    data = {
        'languages': languages_data,
        'translations': translations_data,
    }

    # Pass ensure_ascii=False so that string values will use Unicode
    # characters rather than being escaped for ascii.
    new_built_text = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)

    check_or_update(TRANSLATIONS_PATH, new_text=new_built_text, check_mode=check_mode)


def check_updated():
    """
    Check that the repo is up-to-date.

    This check was added to run in CI.
    """
    update_from_index(check_mode=True)
    build_json(check_mode=True)


def main():
    args = sys.argv[1:]
    command_name = args[0]

    manage_funcs = {
        'build_json': build_json,
        'check_updated': check_updated,
        'update_from_index': update_from_index,
    }

    if command_name not in manage_funcs:
        targets = ', '.join(sorted(manage_funcs))
        msg = (
            f'invalid command name: {command_name!r} (must be one of: {targets})'
        )
        raise RuntimeError(msg)

    manage_func = manage_funcs[command_name]

    manage_func()


if __name__ == '__main__':
    main()
