import os
import re
from collections.abc import Sequence
from pathlib import Path
from tempfile import mkstemp
from typing import Any, TypeAlias, TypeVar, overload

import fsspec
import fsspec.implementations
import pyarrow as pa
from pandas import DataFrame
from pyarrow import Table
from pyarrow import compute as pac


class StorageError(Exception): ...


GlobPath: TypeAlias = str


def create_dir_tree(fs: fsspec.AbstractFileSystem, path: str | list[str]):
    """Create a directory tree in the specified file system if it doesn't
    already exist.

    Parameters
    ----------
    path : str | list[str]
        Path that will be created. If it is a file (i.e. it ends with a
        trailing slash), the parent directories will be created, but not the
        file itself.
    """
    paths = ensure_in_list(path)

    for path in paths:
        path_ = Path(path)

        if not path.endswith(fs.sep):
            # If the path is a file, we want to create the parent directories
            path_ = path_.parent

        fs.makedirs(path_, exist_ok=True)


@overload
def joinpath(*path_pieces: str) -> str: ...  # type: ignore[overload-overlap]
@overload
def joinpath(*path_pieces: list[str] | str) -> list[str]: ...
@overload
def joinpath(*path_pieces: str | list[str]) -> str | list[str]: ...
def joinpath(*path_pieces, all_pieces_are_str: bool = False):
    """Join paths.

    If one of the path piece is a list, the function will join each element of
    the list with the other path pieces.

    os separator in the path pieces will be remove, except for the trailing
    separator of the last piece which is used to differenciate folders from
    files.

    Parameters
    ----------
    *path_pieces : str | list[str]
        Path pieces to join.

    Returns
    -------
    str | list[str]
        the joined path: str if all the components are strings, list of strings
        otherwise.

    Examples
    --------
    >>> joinpath("a", "b", "c")
    "a/b/c"
    >>> joinpath("a", "", "c")
    "a/c"
    >>> joinpath(["a", "b"], "c/")
    ["a/c/", "b/c/"]
    >>> joinpath(["a", "b"], ["c", "d"], "e")
    ["a/c/e", "a/d/e", "b/c/e", "b/d/e"]
    >>> joinpath(["a", "", "b"], ["c", "d"], "e")
    ["a/c/e", "a/d/e", "b/c/e", "b/d/e"]
    """
    if all(isinstance(piece, str) for piece in path_pieces):
        all_pieces_are_str = True

    if len(path_pieces) < 2:
        raise ValueError("At least two path pieces are required.")
    if len(path_pieces) > 2:
        # Recursive call to join the first two pieces and the rest of the pieces.
        # This will slowly reduce the number of pieces until there are only two.
        return joinpath(
            joinpath(path_pieces[0], path_pieces[1]),
            *path_pieces[2:],
            all_pieces_are_str=all_pieces_are_str,
        )

    first_paths = ensure_in_list(path_pieces[0])
    second_paths = ensure_in_list(path_pieces[1])

    joined_paths = _cartesian_product_join_paths(first_paths, second_paths)

    if all_pieces_are_str is True:
        return joined_paths[0]

    return joined_paths


def _cartesian_product_join_paths(
    first_path_piece: list[str], second_path_piece: list[str]
) -> list[str]:
    """Compute the cartesian product of two lists of paths.

    If one of the path piece is an empty string, it will be ignored.

    The output list will contain the concatenation of each element of the first
    list with each element of the second list.

    Returns
    -------
    list[str]
        List of length len(first_path_piece) * len(second_path_piece) that
        contains the concatenated path.
    """
    non_null_first_path_piece = [path for path in first_path_piece if path != ""]
    non_null_second_path_piece = [path for path in second_path_piece if path != ""]

    if len(non_null_first_path_piece) == 0:
        return non_null_second_path_piece
    elif len(non_null_second_path_piece) == 0:
        return non_null_first_path_piece

    results = [""] * len(non_null_first_path_piece) * len(non_null_second_path_piece)
    count = 0
    for first_path in non_null_first_path_piece:
        for second_path in non_null_second_path_piece:
            results[count] = first_path.rstrip("/") + os.sep + second_path.lstrip("/")
            count += 1

    return results[:count]


T = TypeVar("T")


def ensure_in_list(value: T | list[T]) -> list[T]:
    """Put in a list any scalar value that is not None.

    If it is already a list, do nothing.
    """
    if value is not None and not isinstance(value, list):
        value = [value]

    return value


def generate_temporary_filename(parent_directory: str | None = None) -> str:
    """Generate a file name in the OS temporary directory."""
    fd, file_path = mkstemp(dir=parent_directory)
    os.close(fd)
    os.unlink(file_path)
    return file_path


def get_one_of(data: dict[str, Any], possible_attributes: Sequence[str]) -> Any:
    """Get the first attribute that is not None in the data.

    Parameters
    ----------
    data : dict[str, Any]
        Data to get the attributes from.
    possible_attributes : Sequence[str]
        List of attributes to look for in the data.

    Returns
    -------
    Any
        The first attribute that is not None.

    Raises
    ------
    KeyError
        If none of the attributes are in the data.
    """
    for attribute in possible_attributes:
        if attribute in data:
            return data[attribute]

    raise KeyError(f"None of the attributes {possible_attributes} are in the data.")


def convert_decimal_columns_to_double_with_arrow_casting(table: Table) -> Table:
    """Convert every decimal columns to float64 (i.e. double)"""
    for i, (col_name, type_) in enumerate(zip(table.schema.names, table.schema.types)):
        if pa.types.is_decimal(type_):
            table = table.set_column(i, col_name, pac.cast(table.column(col_name), pa.float64()))
    return table


spark_forbidden_chars = [" ", ",", ";", "{", "}", "(", ")", "\n", "\t", "="]


def rename_parquet_col_names(data):
    """
    Renames the columns of a DataFrame to ensure they conform to valid naming conventions for Spark.
    Specifically, it replaces any forbidden characters with underscores and handles duplicate names
    by appending a suffix.

    Parameters
    ----------
    data : pandas.DataFrame
        The DataFrame whose column names need to be renamed. The function will modify the column names
        in place to ensure compatibility with Spark's naming conventions.

    Returns
    -------
    None
        The function modifies the DataFrame in place and does not return a new object.

    Notes
    -----
    - This function uses the `spark_forbidden_chars` list to identify characters that are not allowed
      in Spark column names and replaces them with underscores ('_').
    - If a column name duplicates a previously renamed column, a numeric suffix is appended to the name
      (e.g., `column_1`, `column_2`).
    - The function also ensures that all non-string column names are converted to strings.
    """
    first_mapping = {
        col: re.sub("[" + re.escape("".join(spark_forbidden_chars)) + "]", "_", col)
        for col in data.columns
        if any(char in str(col) for char in spark_forbidden_chars)
    }
    names_given = []
    for old_name, new_name in first_mapping.items():
        final_name = (
            new_name + "_" + str(names_given.count(new_name))
            if names_given.count(new_name) > 0
            else new_name
        )
        data.rename(columns={old_name: final_name}, inplace=True)
        names_given.append(new_name)
    data.rename(
        {col: str(col) for col in data.columns if not isinstance(col, str)}, axis=1, inplace=True
    )


def col_names_contain_forbidden_chars(df: DataFrame) -> bool:
    """check if a dataframe's columns contain spark forbidden characters."""
    for col in df.columns:
        if any(char in str(col) for char in spark_forbidden_chars):
            return True

    return False
