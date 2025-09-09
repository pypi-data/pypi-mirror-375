from app_asset_translator import ConfigUtil
from app_asset_translator import Constants
import json

def create_ios_resource_string(key, value):
    if str(value) == "nan":
        pass
    else:
        return f"\"{key}\" = \"{str(value).strip()}\";"


def write_resource_to_file(writer, value):
    if value is not None:
        writer.write(f"{value}\n")


def create_android_resource_string(key, value):
    if str(value) == "nan":
        pass
    else:
        return f"    <string name=\"{key}\">{str(value).strip()}</string>"

def generate_resource_file_for_language(language, given_df):
    locale = language[Constants.KEY_CONFIG_LOCALE]
    string_path = language.get(Constants.KEY_CONFIG_STRINGS_PATH)
    xml_path = language.get(Constants.KEY_CONFIG_XML_PATH)
    json_path = language.get(Constants.KEY_CONFIG_JSON_PATH)

    config = ConfigUtil.get_config()

    if string_path is not None:
        f = open(string_path, "w")

        results = [create_ios_resource_string(x, y) for x, y in
                   zip(given_df[config[Constants.KEY_CONFIG_VARIABLE_NAME]], given_df[locale])]

        [write_resource_to_file(f, x) for x in results]

        f.close()

    if xml_path is not None:
        f = open(xml_path, "w")
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write("<resources>\n")

        results = [create_android_resource_string(x, y) for x, y in
                   zip(given_df[config[Constants.KEY_CONFIG_VARIABLE_NAME]], given_df[locale])]
        [write_resource_to_file(f, x) for x in results]

        f.write("</resources>")

    if json_path is not None:
        result = {}
        for key, value in zip(given_df[config[Constants.KEY_CONFIG_VARIABLE_NAME]], given_df[locale]):
            if str(value) == "nan" or value is None:
                continue
            parts = key.split('_')
            current = result
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    current[part] = str(value).strip() if value is not None else ""
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
