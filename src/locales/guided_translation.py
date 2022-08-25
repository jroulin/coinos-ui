#!/usr/bin/python

import argparse, json, logging, sys
from pathlib import Path

DEFAULT_FROM_LOCALE = 'en'
LOCALE_DATA_FILEPATH = '../lib/translations/lang.json'

def nested_dict_keys(d, _keyname_prefix=''):
    entry_list = []
    for key in d:
        value = d[key]
        if isinstance(value, dict):
            entry_list += nested_dict_keys(value, _keyname_prefix + key + '.')
        else:
            entry_list += [_keyname_prefix + key]
    return entry_list

def create_locale(locale_code):
    logging.debug("Creating locale %s...", locale_code)
    with open(LOCALE_DATA_FILEPATH, 'r', encoding='utf-8') as lang_file:
        lang_data = json.load(lang_file)

    lang_data[locale_code] = input("What is the name of the language " + locale_code + "? ")

    with open(LOCALE_DATA_FILEPATH, 'w') as lang_file:
        json.dump(lang_data, lang_file, ensure_ascii=False, indent='\t')
        lang_file.write('\n')
    logging.debug("Created locale %s.", locale_code)

def localize_string(string_id, from_data, to_data):
    logging.debug("Translating string with id %s", string_id)
    id_parts = string_id.split('.')

    # get original string
    to_translate = from_data
    for id_part in id_parts:
        to_translate = to_translate[id_part]

    # get translated string
    print("Please translate the following text (id " + string_id + "):")
    print(to_translate)

    translated = input("Type the translated text then press ENTER: ")
    print(translated)

    # find/create place to put translated string
    translation_location = to_data  # the dictionary or list that should contain the translated string
    for id_part in id_parts[:-1]:
        if id_part not in translation_location:
            translation_location[id_part] = {}
        translation_location = translation_location[id_part]

    translation_location[id_parts[-1]] = translated

if __name__ == "__main__":
    # setup and parse commandline arguments
    args_parser = argparse.ArgumentParser(description="guided translation of CoinOS")
    args_parser.add_argument('from_locale', nargs='?', type=str,
                             help="which locale to translate from")
    args_parser.add_argument('to_locale', nargs='?', type=str,
                             help="which locale to translate to")
    args_parser.add_argument('-v', '--verbose', action='count', default=0,
                             help="show more information (use twice for even more)")
    args_parser.add_argument('-V', '--version', action='store_true',
                             help="show version info and exit")
    args = args_parser.parse_args()

    if args.version:
        print("Guided Translation Script version 0.3.0")
        sys.exit(0)

    from_locale = args.from_locale or input("Which locale do you want to translate from (default: %s)? "
                                            % DEFAULT_FROM_LOCALE) or DEFAULT_FROM_LOCALE
    to_locale = args.to_locale or input("Which locale do you want to translate to? ")
    if not to_locale:
        raise ValueError("You need to specify a language to translate to.")

    if args.verbose >= 2:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    elif args.verbose >= 1:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s')

    # load locale files
    logging.debug("Reading file to convert from (%s.json)", from_locale)
    with open(from_locale + ".json", 'r', encoding='utf-8') as from_file:
        from_json_text = from_file.read()
    logging.debug("Converting from data from JSON to object")
    from_data = json.loads(from_json_text)
    from_id_list = nested_dict_keys(from_data)
    logging.info("Successfully obtained %d strings from locale %s",
                 len(from_id_list), from_locale)
    logging.debug("List of strings: %s", from_id_list)

    logging.debug("Reading file to convert to (%s.json)", to_locale)
    to_filepath = "./" + to_locale + ".json"
    if Path(to_filepath).exists():
        with open(to_locale + ".json", 'r', encoding='utf-8') as to_file:
            to_json_text = to_file.read()
        logging.debug("Converting to data from JSON to object")
        to_data = json.loads(to_json_text)
    else:
        logging.info("No file found.  Creating new locale.")
        create_locale(to_locale)
        to_data = {}
    to_id_list = nested_dict_keys(to_data)
    logging.info("Successfully obtained %d strings from locale %s",
                 len(to_id_list), to_locale)
    logging.debug("List of strings: %s", to_id_list)

    if set(from_id_list) == set(to_id_list):
        print("Translations are already complete.")
    else:
        # localize strings!
        try:
            for string_id in from_id_list:
                if string_id not in to_id_list:
                    localize_string(string_id, from_data, to_data)
                    to_id_list.append(string_id)
        except KeyboardInterrupt:
            print("\nProgram interrupted.  Saving strings...")

        # save localized data
        with open(to_locale + ".json", 'w', encoding='utf-8') as to_file:
            json.dump(to_data, to_file, ensure_ascii=False, indent='\t')
            to_file.write('\n')
        logging.info("Saved %d localized strings to %s.json", len(to_id_list), to_locale)