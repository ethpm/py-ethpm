import contextlib
import os
import json
import pytest

from ethpm import Package

from ethpm.exceptions import ValidationError


@contextlib.contextmanager
def _generate_fixture_param(tmpdir, as_file_path, file_content):
    temp_manifest = tmpdir.mkdir('invalid').join('manifest.json')
    temp_manifest.write(file_content)

    if as_file_path:
        yield str(temp_manifest)
    else:
        with open(str(temp_manifest)) as file_obj:
            yield file_obj


@pytest.fixture(params=[True, False])
def valid_manifest_from_path(tmpdir, request):
    valid_manifest = json.dumps({
        "package_name": "foo",
        "manifest_version": "2",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, valid_manifest) as file_obj:
        yield file_obj


@pytest.fixture(params=[True, False])
def invalid_manifest_from_path(tmpdir, request):
    invalid_manifest = json.dumps({
        "package_name": "foo",
        "manifest_version": "not a valid version",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, invalid_manifest) as file_obj_or_path:
        yield file_obj_or_path


@pytest.fixture(params=[True, False])
def non_json_manifest(tmpdir, request):
    with _generate_fixture_param(tmpdir, request.param, 'This is invalid json') as file_obj_or_path:
        yield file_obj_or_path


def test_init_from_minimal_valid_manifest():
    minimal_manifest = {
        "package_name": "foo",
        "manifest_version": "2",
        "version": "1.0.0",
    }

    Package(minimal_manifest)


# only standalone packages are currently supported
# update test to all use cases when dependent packages are supported
def test_package_init_for_all_manifest_use_cases(all_standalone_manifests):
    for manifest in all_standalone_manifests:
        Package(manifest)


def test_init_from_invalid_manifest_data():
    with pytest.raises(ValidationError):
        Package({})


def test_init_from_invalid_argument_type():
    with pytest.raises(TypeError):
        Package("not a manifest")


def test_from_file_fails_with_missing_filepath(tmpdir, w3):
    path = os.path.join(
        str(tmpdir.mkdir('invalid')),
        'manifest.json',
    )

    assert not os.path.exists(path)
    with pytest.raises(FileNotFoundError):
        Package.from_file(path, w3)


def test_from_file_fails_with_non_json(non_json_manifest, w3):
    with pytest.raises(json.JSONDecodeError):
        Package.from_file(non_json_manifest, w3)


def test_from_file_fails_with_invalid_manifest(invalid_manifest_from_path, w3):
    with pytest.raises(ValidationError):
        Package.from_file(invalid_manifest_from_path, w3)


def test_from_file_succeeds_with_valid_manifest(valid_manifest_from_path, w3):
    assert Package.from_file(valid_manifest_from_path, w3)


def test_from_file_raises_type_error_with_invalid_param_type():
    with pytest.raises(TypeError):
        Package.from_file(1)
