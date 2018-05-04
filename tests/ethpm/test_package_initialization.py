import contextlib
import os
import json
import pytest

from ethpm import Package

from ethpm.exceptions import ValidationError


@contextlib.contextmanager
def _generate_fixture_param(tmpdir, as_file_path, file_content):
    temp_package = tmpdir.mkdir('invalid').join('package.json')
    temp_package.write(file_content)

    if as_file_path:
        yield str(temp_package)
    else:
        with open(str(temp_package)) as file_obj:
            yield file_obj


@pytest.fixture(params=[True, False])
def valid_package_from_path(tmpdir, request):
    valid_package = json.dumps({
        "package_name": "foo",
        "manifest_version": "2",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, valid_package) as file_obj:
        yield file_obj


@pytest.fixture(params=[True, False])
def invalid_package_from_path(tmpdir, request):
    invalid_package = json.dumps({
        "package_name": "foo",
        "manifest_version": "not a valid version",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, invalid_package) as file_obj_or_path:
        yield file_obj_or_path


@pytest.fixture(params=[True, False])
def non_json_package(tmpdir, request):
    with _generate_fixture_param(tmpdir, request.param, 'This is invalid json') as file_obj_or_path:
        yield file_obj_or_path


def test_init_from_valid_package_data():
    minimal_package = {
        "package_name": "foo",
        "manifest_version": "2",
        "version": "1.0.0",
    }

    Package(minimal_package)


def test_init_from_invalid_package_data():
    with pytest.raises(ValidationError):
        Package({})


def test_init_from_invalid_argument_type():
    with pytest.raises(TypeError):
        Package("not a package")


def test_from_file_fails_with_missing_filepath(tmpdir):
    path = os.path.join(
        str(tmpdir.mkdir('invalid')),
        'package.json',
    )

    assert not os.path.exists(path)
    with pytest.raises(FileNotFoundError):
        Package.from_file(path)


def test_from_file_fails_with_non_json(non_json_package):
    with pytest.raises(json.JSONDecodeError):
        Package.from_file(non_json_package)


def test_from_file_fails_with_invalid_package(invalid_package_from_path):
    with pytest.raises(ValidationError):
        Package.from_file(invalid_package_from_path)


def test_from_file_succeeds_with_valid_package(valid_package_from_path):
    assert Package.from_file(valid_package_from_path)


def test_from_file_raises_type_error_with_invalid_param_type():
    with pytest.raises(TypeError):
        Package.from_file(1)
