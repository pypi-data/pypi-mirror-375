"""
These tests, as beautiful as they might be, are not perfect. The biggest
limitation is that the file sotrage tested can only be the local one since
tempfile is used. It relies on OS specification to create and remove
temporary files / folders. Unfortunately, it cannot be extended to every
file system support in fsspec.

Tests of read/write methods are not isolated, and they rely on each other
to pass. If the tests fails, one of them (or both) is the culprit.
"""

import logging
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pandas as pd
import pytest

from papai_unified_storage.storage import Storage, filesystem, logger
from papai_unified_storage.utils import joinpath, rename_parquet_col_names
from tests.utils import create_files


@pytest.fixture()
def storage():
    return filesystem("file", auto_mkdir=False)


@pytest.fixture()
def test_dataframe():
    return pd.DataFrame(
        {"one": [-1, 1, 2.5], "two": ["foo", "bar", "baz"], "three": [True, False, True]},
        index=list("abc"),
    )


@pytest.fixture()
def test_dataframe_with_forbidden_chars():
    return pd.DataFrame(
        {"one(1)": [-1, 1, 2.5], "two{2}": ["foo", "bar", "baz"], "three;/": [True, False, True]},
        index=list("abc"),
    )


def test_dataframe_read_parquet(test_dataframe: pd.DataFrame, storage: Storage):
    with TemporaryDirectory() as d:
        test_dataframe.to_parquet(f"{d}/test.parquet")

        df_wrote_read = storage.read_dataset_from_parquet(f"{d}/test.parquet")

    assert test_dataframe.equals(df_wrote_read)


def test_read_dataset_from_parquet_decimal(storage: Storage):
    from decimal import Decimal
    from random import random

    import numpy as np
    from pyarrow import Table, parquet

    ar_deci_1 = [Decimal(random()) for _ in range(100)]
    ar_deci_2 = [Decimal(random() * 10) for _ in range(100)]
    ar_float = [random() * 100 for _ in range(100)]
    ar_string = ["moi" for _ in range(100)]

    table = Table.from_arrays(
        [ar_deci_1, ar_deci_2, ar_float, ar_string],
        names=["ar_deci_1", "ar_deci_2", "ar_float", "ar_string"],
    )
    with TemporaryDirectory() as d:
        parquet.write_table(table, f"{d}/test.parquet")

        df_read = storage.read_dataset_from_parquet(f"{d}/test.parquet")

    assert isinstance(df_read["ar_deci_1"].dtype, type(np.dtype("float64")))
    assert isinstance(df_read["ar_deci_2"].dtype, type(np.dtype("float64")))
    assert isinstance(df_read["ar_float"].dtype, type(np.dtype("float64")))
    assert isinstance(df_read["ar_string"].dtype, type(np.dtype("object")))


@pytest.mark.parametrize(
    ("dataframe_fixture, replace_spark_forbidden_characters"),
    (
        ("test_dataframe", True),
        ("test_dataframe", False),
        ("test_dataframe_with_forbidden_chars", True),
        ("test_dataframe_with_forbidden_chars", False),
    ),
)
def test_dataframe_write_parquet(
    request: pytest.FixtureRequest,
    dataframe_fixture: str,
    replace_spark_forbidden_characters: bool,
    storage: Storage,
):
    with TemporaryDirectory() as d:
        dataframe = request.getfixturevalue(dataframe_fixture)
        storage.write_dataframe_to_parquet(
            f"{d}/test.parquet", dataframe, replace_spark_forbidden_characters
        )

        df_wrote_read = pd.read_parquet(f"{d}/test.parquet")

        if replace_spark_forbidden_characters:
            rename_parquet_col_names(dataframe)
            assert df_wrote_read.equals(dataframe)
        else:
            assert df_wrote_read.equals(dataframe)


@pytest.fixture
def tmp_directories():
    with TemporaryDirectory() as remote:
        with TemporaryDirectory() as local:
            yield remote, local


@pytest.fixture(
    params=(
        (["f1", "d/f2", "d/f3", "d/d/g1"], ["f1", "d/f2"], "", ["f1", "f2"], {"recursive": False}),
        (
            ["f1", "d/f1", "d/f2", "d/f3", "d/d/g1"],
            ["d/f*"],
            "",
            ["f1", "f2", "f3"],
            {"recursive": False},
        ),
        (
            ["f1", "d/f1", "d/f2", "d/f3", "d/d/g1"],
            ["d/**"],
            "",
            ["f1", "f2", "f3"],
            {"recursive": False},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/dir2/file1"],
            ["download/file1", "download/file2"],
            ["download/file1", "download/file2"],
            {"recursive": False},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/"],
            "download",
            ["download/file1", "download/file2", "download/file3"],
            {"recursive": True},
        ),
        # You can't download a folders at a different locations than the rest
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/"],
            ["download1/file1", "download2/"],
            ["download1/file1", "download2/"],
            {"recursive": True},
        ),
    )
)
def data_test_get(request):
    return request.param


def test_get(storage: Storage, tmp_directories, data_test_get):
    remote_dir, local_dir = tmp_directories
    (remote_paths_to_create, get_rpaths, get_lpath, expected_existing_files, get_kwargs) = (
        data_test_get
    )

    create_files(joinpath(remote_dir, remote_paths_to_create))

    storage.get(joinpath(remote_dir, get_rpaths), joinpath(local_dir, get_lpath), **get_kwargs)

    for file in expected_existing_files:
        assert os.path.exists(joinpath(local_dir, file))


@pytest.fixture(
    params=(
        (["f1", "d1/f2", "d2/f3", "d2/d/g1"], "d2", "", ["f3"], {"recursive": False}),
        (["f1", "d1/f2", "d2/f3", "d2/d/g1"], "d2", "", ["f3", "d/g1"], {"recursive": True}),
        (["f1", "d1/f2", "d2/f3", "d2/d/g1"], "d2", "local_d", ["f3", "d/g1"], {"recursive": True}),
    )
)
def data_test_get_files(request):
    return request.param


def test_get_files(storage: Storage, tmp_directories, data_test_get_files):
    remote_dir, local_dir = tmp_directories
    (remote_paths_to_create, get_rpath, get_lpath, expected_existing_files, get_kwargs) = (
        data_test_get_files
    )

    create_files(joinpath(remote_dir, remote_paths_to_create))

    local_files = storage.get_files(
        joinpath(remote_dir, get_rpath), joinpath(local_dir, get_lpath), **get_kwargs
    )

    remote_dir_without_root = remote_dir.strip("/").split("/", 1)[1]
    expected_results = joinpath(
        local_dir, get_lpath, remote_dir_without_root, get_rpath, expected_existing_files
    )
    assert set(local_files) == set(expected_results)


@pytest.fixture(
    params=(
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            "file1",
            "upload/file1",
            ["upload/file1"],
            {"recursive": False},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            "dir1/**",
            "upload/",
            ["upload/file1", "upload/file2", "upload/file3", "upload/dir2/file1"],
            {"recursive": False},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            "dir1",
            "upload/",
            [
                "upload/dir1/file1",
                "upload/dir1/file2",
                "upload/dir1/file3",
                "upload/dir1/dir2/file1",
            ],
            {"recursive": True},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/dir2/file1"],
            ["upload/file1", "upload/file2"],
            ["upload/file1", "upload/file2"],
            {"recursive": False},
        ),
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/"],
            "upload",
            ["upload/file1", "upload/file2", "upload/file3"],
            {"recursive": True},
        ),
        # You can't upload a folders at a different locations than the rest
        (
            ["file1", "dir1/file1", "dir1/file2", "dir1/file3", "dir1/dir2/file1"],
            ["file1", "dir1/"],
            ["upload1/file1", "upload2/"],
            ["upload1/file1", "upload2/"],
            {"recursive": True},
        ),
    )
)
def data_test_put(request):
    return request.param


def test_put(storage: Storage, tmp_directories, data_test_put):
    remote_dir, local_dir = tmp_directories
    (local_paths_to_create, put_lpath, put_rpaths, expected_existing_files, put_kwargs) = (
        data_test_put
    )

    create_files(joinpath(local_dir, local_paths_to_create))

    storage.put(joinpath(local_dir, put_lpath), joinpath(remote_dir, put_rpaths), **put_kwargs)

    for file in expected_existing_files:
        assert os.path.exists(joinpath(remote_dir, file))


def test_list_files(storage: Storage):
    with TemporaryDirectory() as d:
        create_files([f"{d}/f1", f"{d}/d/f2"])

        assert set(storage.list_files(d, recursive=True)) == {f"{d}/f1", f"{d}/d/f2"}
        assert set(storage.list_files(d)) == {f"{d}/f1"}


def test_list_files_with_details(storage: Storage):
    with TemporaryDirectory() as d:
        create_files([f"{d}/f1", f"{d}/d/f2"])

        list_files = storage.list_files(d, recursive=True, detail=True)
        assert len(list_files) == 2
        for file_detail, file_name in zip(list_files.values(), [f"{d}/d/f2", f"{d}/f1"]):
            assert file_detail["name"] == file_name
            assert file_detail["size"] == len(file_name)


def test_glob_files_with_details(storage: Storage):
    with TemporaryDirectory() as d:
        create_files([f"{d}/f1", f"{d}/d/f1", f"{d}/d/f2", f"{d}/d/f3"])

        list_files = storage.glob_files(f"{d}/d/f*", detail=True)
        assert len(list_files) == 3
        for file_detail, file_name in zip(
            list_files.values(), [f"{d}/d/f1", f"{d}/d/f2", f"{d}/d/f3"]
        ):
            assert file_detail["name"] == file_name
            assert file_detail["size"] == len(file_name)


def test_list_files_without_root_folder_name(storage: Storage):
    with TemporaryDirectory() as d:
        create_files([f"{d}/f1", f"{d}/d/f2"])

        d_without_root = d.strip("/").split("/", 1)[1]

        assert set(storage.list_files(d, recursive=True, remove_root_folder=True)) == {
            f"{d_without_root}/f1",
            f"{d_without_root}/d/f2",
        }

        root_folder = d.strip("/").split("/", 1)[0]
        root_folder_with_sep = storage.filesystem.sep + root_folder + storage.filesystem.sep
        assert set(storage.list_files(d, recursive=True, remove_prefix=root_folder_with_sep)) == {
            f"{d_without_root}/f1",
            f"{d_without_root}/d/f2",
        }


def test_list_files_without_root_folder_name_and_remove_prefix(storage: Storage):
    with TemporaryDirectory() as d:
        first_folder_name = d.split("/", 2)[1] + storage.filesystem.sep
        d_without_root_nor_first_folder = d.split("/", 2)[2]

        create_files([f"{d}/f1", f"{d}/d/f2"])

        assert set(
            storage.list_files(
                d, recursive=True, remove_root_folder=True, remove_prefix=first_folder_name
            )
        ) == {f"{d_without_root_nor_first_folder}/f1", f"{d_without_root_nor_first_folder}/d/f2"}


def test_remove_files(storage: Storage):
    with TemporaryDirectory() as d:
        create_files([f"{d}/f1", f"{d}/d/f2"])

        storage.remove_files([f"{d}/f1", f"{d}/d/f2"])

        assert not os.path.exists(f"{d}/f1")
        assert not os.path.exists(f"{d}/d/f2")


def test_open_read_write(storage: Storage):
    with NamedTemporaryFile(mode="wb+") as file:
        with storage.open_for_writing(file.name) as f:
            f.write(b"content")

        with storage.open_for_reading(file.name) as f:
            assert f.read() == b"content"


def test_move(storage: Storage):
    with TemporaryDirectory() as d:
        # create a file
        with open(f"{d}/f1", "w") as f:
            f.write("content")

        storage.move(f"{d}/f1", f"{d}/f2")

        assert not os.path.exists(f"{d}/f1")
        assert os.path.exists(f"{d}/f2")


def test_bytes_to_file(storage: Storage):
    with TemporaryDirectory() as d:
        file_path = f"{d}/file"
        storage.write_to_file(file_path, b"content")

        with open(file_path, "rb") as f:
            assert f.read() == b"content"


def test_str_to_file(storage: Storage):
    with TemporaryDirectory() as d:
        file_path = f"{d}/file"
        storage.write_to_file(file_path, "content")

        with open(file_path) as f:
            assert f.read() == "content"


@pytest.fixture
def json_data():
    return {"a": 1, "b": 2, "c": 3}


def test_loader(storage: Storage, json_data: dict):
    import json

    with TemporaryDirectory() as d:
        with open(f"{d}/json", "w") as file:
            json.dump(json_data, file)

        out_model: dict = storage.loader(file.name, json.load, text=True)

        for key_item_1, key_item_2 in zip(json_data.items(), out_model.items()):
            if key_item_1[1] != key_item_2[1]:
                assert False


def test_disable_debug_logging(caplog, storage: Storage):
    logger.setLevel(logging.DEBUG)

    with caplog.at_level("INFO"):
        logger.info("This should be logged")
    assert "This should be logged" in caplog.text

    with storage.disable_debug_logging():
        with caplog.at_level("INFO"):
            logger.info("This should be not logged")
    assert "This should be logged" in caplog.text

    # check that it reverts back to the original function after exiting the context manager
    with caplog.at_level("INFO"):
        logger.info("This should be logged")
    assert "This should be logged" in caplog.text


def test_enable_debug_logging(storage: Storage):
    called = [False]

    def assert_called(msg: str):
        called[0] = True

    storage.log_debug_fn = assert_called
    storage.log_debug_fn("This should be called")
    assert called[0] is True
