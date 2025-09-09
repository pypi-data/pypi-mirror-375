from app_asset_translator import ConfigUtil
from app_asset_translator import Constants


def remove_none_values(value_list):
    return [i for i in value_list if i is not None]

# This function is used to filter out languages without a defined xml/string path
def get_language_details(language):
    # This part is required, as the language string, f.e 'Dutch-NL' is 1 layer higher than the required data
    current_language_key = list(language.keys())[0]
    language = language[current_language_key]

    string_path_defined = Constants.KEY_CONFIG_STRINGS_PATH in language
    xml_path_defined = Constants.KEY_CONFIG_XML_PATH in language
    json_path_defined = Constants.KEY_CONFIG_JSON_PATH in language

    # If the attribute does not exist, set the path to None
    if not string_path_defined:
        string_path = None
    else:
        string_path = language[Constants.KEY_CONFIG_STRINGS_PATH]

    # If the attribute does not exist, set the path to None
    if not xml_path_defined:
        xml_path = None
    else:
        xml_path = language[Constants.KEY_CONFIG_XML_PATH]

    # If the attribute does not exist, set the path to None
    if not json_path_defined:
        json_path = None
    else:
        json_path = language[Constants.KEY_CONFIG_JSON_PATH]

    if xml_path is None and string_path is None and json_path is None:
        pass
    else:
        return language


def get_languages():
    config = ConfigUtil.get_config()
    languages_section = config.get(Constants.KEY_CONFIG_SUPPORTED_LANGUAGES, [])
    language_list = [get_language_details(x) for x in languages_section]
    print(f"Language list: {language_list}")
    return remove_none_values(language_list)
