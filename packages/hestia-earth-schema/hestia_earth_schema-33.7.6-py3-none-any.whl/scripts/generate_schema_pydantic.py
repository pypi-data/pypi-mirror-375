import os
import json
import shutil
from pathlib import Path
from datamodel_code_generator import generate, PythonVersion

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.join(_CURRENT_DIR, '..')
_SRC_DIR = os.path.join(_ROOT_DIR, 'src', '@hestia-earth', 'json-schema', 'json-schema')

_TMP_DIR = os.path.join(_CURRENT_DIR, 'pydantic')
_DEST_DIR = os.path.join(_ROOT_DIR, 'hestia_earth', 'schema', 'pydantic')


def _clean_dir(folder: str):
    os.makedirs(folder, exist_ok=True)
    shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)


def _remove_deep_ref(value: dict):
    if 'items' in value and '$ref' in value['items']:
        value['items']['$ref'] = value['items']['$ref'].replace('-deep', '')
    if '$ref' in value:
        value['$ref'] = value['$ref'].replace('-deep', '')

    return value


def _copy_schema(file: str):
    with open(os.path.join(_SRC_DIR, file), 'r') as f:
        data = json.load(f)

    data['$id'] = f"{data['title']}.json"

    # replace all -deep references
    data['properties'] = {
        k: _remove_deep_ref(v)
        for k, v in data['properties'].items()
    }

    if 'allOf' in data:
        del data['allOf']

    if 'oneOf' in data:
        del data['oneOf']

    with open(os.path.join(_TMP_DIR, file), 'w') as f:
        f.write(json.dumps(data, indent=2))


def _update_term(code: str, *args):
    return code.replace(
        "name: str",
        "name: Optional[str]"
    )


def _update_actor(code: str, *args):
    return code.replace("lastName: str", "lastName: Optional[str]")


def _update_method_classification(code: str, schema_type: str):
    return code.replace(
        'MethodClassification',
        schema_type + 'MethodClassification'
    )


_UPDATE_GENERATED_FILE = {
    'Term': _update_term,
    'Actor': _update_actor,
    'Management': _update_method_classification,
    'Measurement': _update_method_classification
}


def _update_generated_file(schema_type: str):
    if schema_type in _UPDATE_GENERATED_FILE:
        filepath = os.path.join(_DEST_DIR, f"{schema_type}.py")

        with open(filepath, 'r') as f:
            code = f.read()

        code = _UPDATE_GENERATED_FILE[schema_type](code, schema_type)

        with open(filepath, 'w') as f:
            f.write(code)


def main():
    _clean_dir(_TMP_DIR)
    _clean_dir(_DEST_DIR)

    files = [f for f in os.listdir(_SRC_DIR) if not 'deep' in f]

    # copy files for pydantic
    list(map(_copy_schema, files))

    generate(
        input_=Path(_TMP_DIR),
        input_file_type="json_schema",
        output=Path(_DEST_DIR),
        custom_formatters=['formatters.float', 'formatters.dates'],
        custom_template_dir=Path(os.path.join(_CURRENT_DIR, 'templates')),
        target_python_version=PythonVersion.PY_39,
        use_standard_collections=True,
        use_one_literal_as_default=True,
    )

    return [
        _update_generated_file(f.split('.')[0]) for f in files
    ]


if __name__ == '__main__':
    main()
