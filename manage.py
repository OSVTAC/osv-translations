#
# Open Source Voting Translation Manager (OTM) - election translations
# Copyright (C) 2020  Chris Jerdonek
#
# This file is part of Open Source Voting Translation Manager (OTM).
#
# OTR is free software: you can redistribute it and/or modify
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

import json
from pathlib import Path
import sys

import yaml


LANG_CODE_EN = 'en'

TRANSLATIONS_PATH = 'translations.json'


def read_yaml(path):
    with open(path) as f:
        data = yaml.safe_load(f)

    return data


def write_yaml(data, path):
    with open(path, mode='w') as f:
        yaml.dump(data, f, default_flow_style=False)


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
    for phrase_data in source_phrases:
        phrase_id = phrase_data['id']
        desc = phrase_data['desc']
        english = phrase_data['text']

        yield (phrase_id, desc, english)


def update_lang_phrases(target_phrases, source_phrases, lang_code):
    is_english = lang_code == LANG_CODE_EN

    if is_english:
        text_key = 'text'
    else:
        text_key = '_en'

    for phrase_info in iter_source_phrases(source_phrases):
        phrase_id, phrase_desc, phrase_english = phrase_info

        target_phrase = target_phrases.setdefault(phrase_id, {})
        target_phrase['_desc'] = phrase_desc
        target_phrase[text_key] = phrase_english

        if not is_english:
            target_phrase.setdefault('text', '')


def update_language_file(source_phrases, languages_data, lang_code):
    language_data = languages_data[lang_code]
    lang_name = language_data['name']

    lang_path = get_lang_path(lang_code)
    data = read_lang_file(lang_path)

    data['_meta'] = {
        'language': lang_name
    }
    target_phrases = data.setdefault('phrases', {})

    update_lang_phrases(target_phrases, source_phrases, lang_code=lang_code)

    write_yaml(data, path=lang_path)


def update_from_index():
    languages_data, phrases_data = read_index()

    lang_codes = sorted(languages_data)
    lang_codes.remove(LANG_CODE_EN)

    for lang_code in sorted(languages_data):
        update_language_file(source_phrases, languages_data, lang_code=lang_code)


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


def build_json():
    languages_data, phrases_data = read_index()

    translations_data = {}

    for phrase_info in iter_source_phrases(phrases_data):
        phrase_id, phrase_desc, phrase_english = phrase_info
        phrase_data  = {LANG_CODE_EN: phrase_english}
        translations_data[phrase_id] = phrase_data

    # We are done processing English.
    del languages_data[LANG_CODE_EN]

    for lang_code, lang_data in languages_data.items():
        lang_name = lang_data['name']

        try:
            _build_lang(lang_code, lang_name=lang_name, translations_data=translations_data)
        except:
            msg = f'error while processing file for language: {lang_code!r}'
            raise RuntimeError(msg)

    data = {'translations': translations_data}

    with open(TRANSLATIONS_PATH, mode='w') as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)


def main():
    args = sys.argv[1:]
    command_name = args[0]

    manage_funcs = {
        'build_json': build_json,
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
