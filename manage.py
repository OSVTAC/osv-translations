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

from pathlib import Path
import sys

import yaml


LANG_CODE_EN = 'en'


def read_yaml(path):
    with open(path) as f:
        data = yaml.safe_load(f)

    return data


def write_yaml(data, path):
    with open(path, mode='w') as f:
        yaml.dump(data, f, default_flow_style=False)


def get_lang_path(lang_code):
    return Path('languages') / f'{lang_code}.yml'


def read_lang_file(path):
    if not path.exists():
        return {}

    return read_yaml(path)


def update_lang_phrases(target_phrases, source_phrases, lang_code):
    is_english = lang_code == LANG_CODE_EN

    if is_english:
        text_key = 'text'
    else:
        text_key = '_en'

    for phrase_data in source_phrases:
        phrase_id = phrase_data['id']
        phrase_desc = phrase_data['desc']
        phrase_english = phrase_data['en']

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
    data = read_yaml('index.yml')

    languages_data = data['languages']
    source_phrases = data['phrases']

    for lang_code in sorted(languages_data):
        update_language_file(source_phrases, languages_data, lang_code=lang_code)


def main():
    args = sys.argv[1:]
    command_name = args[0]

    manage_funcs = {
        'update-from-index': update_from_index,
    }

    if command_name not in manage_funcs:
        targets = ', '.join(sorted(manage_funcs))
        msg = (
            f'invalid command name: {command_name!r} (not one of: {targets})'
        )
        raise RuntimeError(msg)

    manage_func = manage_funcs[command_name]

    manage_func()


if __name__ == '__main__':
    main()
