import os
from tempfile import TemporaryDirectory

import fsspec
import pandas as pd
import pytest


@pytest.mark.parametrize(
    "paths_pieces, expected_result",
    (
        (["a", ["b"], "c"], ["a/b/c"]),
        (["a", "b", "c"], "a/b/c"),
        (["a", "", "c"], "a/c"),
        (["a/", "/b/", "//c"], "a/b/c"),
        (["a/", "/b/", "//c/"], "a/b/c/"),
        (["a", ["b", "c"]], ["a/b", "a/c"]),
        ([["a", "b"], ["c", "d"]], ["a/c", "a/d", "b/c", "b/d"]),
        (["a", ["b", "c"], "d"], ["a/b/d", "a/c/d"]),
        ([["a", "", "b"], ["c", "d"], "e"], ["a/c/e", "a/d/e", "b/c/e", "b/d/e"]),
        ([["a", "b", "c"], ["", ""], "e"], ["a/e", "b/e", "c/e"]),
        ([["", ""], ["a", "b", "c"], "e"], ["a/e", "b/e", "c/e"]),
    ),
)
def test_joinpath(paths_pieces, expected_result):
    from papai_unified_storage import joinpath

    assert joinpath(*paths_pieces) == expected_result


def test_create_local_dir_tree_folder():
    from papai_unified_storage.utils import create_dir_tree

    with TemporaryDirectory() as d:
        create_dir_tree(fsspec.filesystem("file"), f"{d}/a/b/c/")

        assert os.path.exists(f"{d}/a/b/c/")


test_examples = [
    (pd.DataFrame({"A": [], "B": [], "C": []}), False, pd.DataFrame({"A": [], "B": [], "C": []})),
    (
        pd.DataFrame({"A(1)": [], "B": [], "C": []}),
        True,
        pd.DataFrame({"A_1_": [], "B": [], "C": []}),
    ),
    (
        pd.DataFrame({"A ": [], "A;": [], "C": []}),
        True,
        pd.DataFrame({"A_": [], "A__1": [], "C": []}),
    ),
    (pd.DataFrame({"A,": [], "B": [], "C": []}), True, pd.DataFrame({"A_": [], "B": [], "C": []})),
    (
        pd.DataFrame({"A;": [], "B;": [], "C": []}),
        True,
        pd.DataFrame({"A_": [], "B_": [], "C": []}),
    ),
    (
        pd.DataFrame({"A{1}": [], "A(1)": [], "A,1,": []}),
        True,
        pd.DataFrame({"A_1_": [], "A_1__1": [], "A_1__2": []}),
    ),
    (pd.DataFrame({"A\n": [], "B": [], "C": []}), True, pd.DataFrame({"A_": [], "B": [], "C": []})),
    (pd.DataFrame({"A\t": [], "B": [], "C": []}), True, pd.DataFrame({"A_": [], "B": [], "C": []})),
    (pd.DataFrame({"A=B": [], "B": [], 1: []}), True, pd.DataFrame({"A_B": [], "B": [], "1": []})),
]


@pytest.mark.parametrize("sample_dataframe, expected_check, _", test_examples)
def test_col_names_contain_forbidden_chars(sample_dataframe: pd.DataFrame, expected_check: bool, _):
    from papai_unified_storage.utils import col_names_contain_forbidden_chars

    assert col_names_contain_forbidden_chars(sample_dataframe) == expected_check


@pytest.mark.parametrize("sample_dataframe, _, expected_dataframe", test_examples)
def test_rename_parquet_col_names(
    sample_dataframe: pd.DataFrame, expected_dataframe: pd.DataFrame, _
):
    from papai_unified_storage.utils import rename_parquet_col_names

    rename_parquet_col_names(sample_dataframe)
    assert sample_dataframe.columns.tolist() == expected_dataframe.columns.tolist()
