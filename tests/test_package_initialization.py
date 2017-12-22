import contextlib
import os
import json
import pytest

from ethpm import Package

from ethpm.exceptions import ValidationError


@contextlib.contextmanager
def _generate_fixture_param(tmpdir, as_file_path, file_content):
    temp_lockfile = tmpdir.mkdir('invalid').join('lockfile.json')
    temp_lockfile.write(file_content)

    if as_file_path:
        yield str(temp_lockfile)
    else:
        with open(str(temp_lockfile)) as file_obj:
            yield file_obj


@pytest.fixture(params=[True, False])
def valid_lockfile_from_path(tmpdir, request):
    valid_lockfile = json.dumps({
        "package_name": "foo",
        "lockfile_version": "1",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, valid_lockfile) as file_obj:
        yield file_obj


@pytest.fixture(params=[True, False])
def invalid_lockfile_from_path(tmpdir, request):
    invalid_lockfile = json.dumps({
        "package_name": "foo",
        "lockfile_version": "not a valid version",
        "version": "1.0.0",
    })
    with _generate_fixture_param(tmpdir, request.param, invalid_lockfile) as file_obj_or_path:
        yield file_obj_or_path


@pytest.fixture(params=[True, False])
def non_json_lockfile(tmpdir, request):
    with _generate_fixture_param(tmpdir, request.param, 'This is invalid json') as file_obj_or_path:
        yield file_obj_or_path


def test_init_from_valid_lockfile_data():
    minimal_lockfile = {
        "package_name": "foo",
        "lockfile_version": "1",
        "version": "1.0.0",
    }

    Package(minimal_lockfile)


def test_init_from_invalid_lockfile_data():
    with pytest.raises(ValidationError):
        Package({})


def test_init_from_invalid_argument_type():
    with pytest.raises(TypeError):
        Package("not a lockfile")


def test_from_file_fails_with_missing_filepath(tmpdir):
    path = os.path.join(
        str(tmpdir.mkdir('invalid')),
        'lockfile.json',
    )

    assert not os.path.exists(path)
    with pytest.raises(FileNotFoundError):
        Package.from_file(path)


def test_from_file_fails_with_non_json(non_json_lockfile):
    with pytest.raises(json.JSONDecodeError):
        Package.from_file(non_json_lockfile)


def test_from_file_fails_with_invalid_lockfile(invalid_lockfile_from_path):
    with pytest.raises(ValidationError):
        Package.from_file(invalid_lockfile_from_path)


def test_from_file_succeeds_with_valid_lockfile(valid_lockfile_from_path):
    assert Package.from_file(valid_lockfile_from_path)


def test_from_file_raises_type_error_with_invalid_param_type():
    with pytest.raises(TypeError):
        Package.from_file(1)
