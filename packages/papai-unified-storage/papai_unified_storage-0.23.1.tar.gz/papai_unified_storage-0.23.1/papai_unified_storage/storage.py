import logging
from contextlib import contextmanager
from io import BytesIO, StringIO, TextIOWrapper
from typing import TYPE_CHECKING, Any, Callable, Literal, Union, overload

import fsspec
import pyarrow
import pyarrow.parquet

if TYPE_CHECKING:
    from fsspec import AbstractFileSystem
    from fsspec.spec import AbstractBufferedFile
    from pandas import DataFrame

from .utils import (
    GlobPath,
    StorageError,
    col_names_contain_forbidden_chars,
    convert_decimal_columns_to_double_with_arrow_casting,
    create_dir_tree,
    joinpath,
    rename_parquet_col_names,
)

logger = logging.getLogger(__name__)


def filesystem(protocol: str, **storage_options):
    """Generate a supercharged fsspec storage instance for a given protocol.

    Parameters
    ----------
    protocol : str
        name of the protocol to use. See options at
        https://filesystem-spec.readthedocs.io/en/latest/api.html#built-in-implementations

    Returns
    -------
    Storage(fsspec.AbstractFileSystem)
        Supercharged fsspec storage instance.
    """
    internal_fs_class = fsspec.get_filesystem_class(protocol)
    internal_fs = get_storage_wrapper(internal_fs_class, storage_options)
    fs = Storage(internal_fs)
    return fs


def get_storage_wrapper(storage_class: "AbstractFileSystem", storage_options):
    class FileSystemWrapper(storage_class):
        def get_file(self, rpath, lpath, **kwargs):
            create_dir_tree(fsspec.filesystem("file"), lpath)
            super().get_file(rpath, lpath, **kwargs)

        def put_file(self, lpath, rpath, **kwargs):
            create_dir_tree(self, rpath)
            super().put_file(lpath, rpath, **kwargs)

    return FileSystemWrapper(**storage_options)


class Storage:
    def __init__(self, filesystem: "AbstractFileSystem"):
        """Create storage proxy to a remote file system.

        Parameters
        ----------
        filesystem : fsspec.AbstractFileSystem
            The file system to use.
        """
        self.filesystem = filesystem

    @contextmanager
    def disable_debug_logging(self):
        old_level = logger.level
        logger.setLevel(logging.CRITICAL)
        yield
        logger.setLevel(old_level)

    @contextmanager
    def error_logging(self, error_msg: str):
        try:
            yield
        except Exception as exc:
            logger.exception(error_msg)
            raise StorageError(error_msg) from exc

    @overload
    def get(
        self,
        remote_path: str | list[str] | GlobPath | list[GlobPath],
        local_path: str,
        recursive: bool = False,
    ): ...
    @overload
    def get(self, remote_path: list[str], local_path: list[str], recursive: bool = False): ...
    def get(self, remote_path, local_path, recursive=False):
        """Copy remote file(s) to local.

        Copies a specific file or tree of files (if recursive=True). If
        rpath ends with a "/", it will be assumed to be a directory, and
        target files will go within. Can submit a list of paths, which may
        be glob-patterns and will be expanded.

        If both remote_path and local_path are lists, they must be the same
        length and paths will not be expanded. That means that you can't
        download a folder recursively to different location than the rest.

        If you set recursive=True, then remote_paths that are folders
        will be downloaded recursively. If you use a glob pattern in a
        remote_path (e.g. `folder/*`), it will download the folder `folder`
        recursively, but not the other non-glob pattern path of `remote_path`.

        Calls get_file for each source.

        Examples
        --------
        >>> fs.get(["file1", "folder"], "download", recursive=True)
        >>> pathlib.Path("download").rglob('*')
        [download/file1, download/folder/file2]
        >>> fs.get(["file1", "folder/**"], "download", recursive=False)
        >>> pathlib.Path("download").rglob('*')
        [download/file1, download/folder/file2]
        >>> # You can't download a folder at a different location than the rest
        >>> fs.get(["file1", "folder/*"], ["download/1/file1", "download/2/"])
        >>> pathlib.Path("download").rglob('*')
        [download/1/file1, download/2/]
        >>> fs.get("file1", "download/path/to/file")
        >>> pathlib.Path("download").rglob('*')
        [download/path/to/file]

        Notes
        -----
        See `Storage.get_files` for another way of downloading multiple files to local.
        """
        base_log_msg = f"remote file(s) at {remote_path} to local at {local_path}"
        with self.error_logging(f"Failed to copy {base_log_msg}"):
            result = self.filesystem.get(remote_path, local_path, recursive)
        logger.info(f"Copied {base_log_msg}")
        return result

    def get_files(self, remote_path: str, local_path: str, recursive=False) -> list[str]:
        """Copy a specific tree of remote files to local and retuen the local paths.

        If you set recursive=True, then remote_paths that are folders
        will be downloaded recursively.

        Calls get_file for each source.

        Returns
        -------
        list[str]
            List of local paths where the files were downloaded.

        Examples
        --------
        >>> # given the structure:
        >>> # dir1/
        >>> # ├── file1
        >>> # └── folder/
        >>> #     └── file2
        >>> fs.get_files("dir1", "download/path/")
        ["download/path/file1", "download/path/folder/file2"]
        """
        remote_files = self.filesystem.find(remote_path, maxdepth=None if recursive else 1)
        names_without_bucket_name = self._remove_prefix(remote_files, remove_root_folder=True)
        local_paths = joinpath(local_path, names_without_bucket_name)

        for remote_file, local_file in zip(remote_files, local_paths):
            self.get_file(remote_file, local_file)
        logger.info(f"Copied remote file(s) at {remote_path} to local at {local_path}")
        return local_paths

    def get_file(self, rpath, lpath, **kwargs):
        base_log_msg = f"remote file at {rpath} to local at {lpath}"
        with self.error_logging(f"Failed to copy {base_log_msg}"):
            result = self.filesystem.get_file(rpath, lpath, **kwargs)
        logger.info(f"Copied {base_log_msg}")
        return result

    def put(self, local_path: str | list[str], remote_path: str | list[str], recursive=False):
        """Copy file(s) from local to remote.

        Copies a specific file or tree of files (if recursive=True). If
        rpath ends with a "/", it will be assumed to be a directory, and
        target files will go within. Can submit a list of paths, which may
        be glob-patterns and will be expanded.

        If both remote_path and local_path are lists, they must be the same
        length and paths will not be expanded. That means that you can't
        upload a folder recursively to different location than the rest.

        If you set recursive=True, then local_paths that are folders
        will be uploaded recursively. If you use a glob pattern in a
        local_path (e.g. `folder/*`), it will upload the folder `folder`
        recursively, but not the other non-glob pattern path of `local_path`.

        Calls put_file for each source.

        Examples
        --------
        >>> fs.put(["file1", "folder"], "upload", recursive=True)
        >>> fs.glob('upload/**')
        [upload/file1, upload/folder/file2]
        >>> fs.put(["file1", "folder/**"], "upload", recursive=False)
        >>> fs.glob('upload/**')
        [upload/file1, upload/folder/file2]
        >>> # You can't upload a folder at a different location than the rest
        >>> fs.put(["file1", "folder/"], ["upload/1/file1", "upload/2/"], recursively=True)
        >>> fs.glob('upload/**')
        []
        >>> fs.put("file1", "upload/path/to/file")
        >>> fs.glob('upload/**')
        [upload/path/to/file]
        """
        base_log_msg = f"local file(s) at {local_path} to remote at {remote_path}"
        with self.error_logging(f"Failed to copy {base_log_msg}"):
            result = self.filesystem.put(local_path, remote_path, recursive)
        logger.info(f"Copied {base_log_msg}")
        return result

    def put_file(self, lpath, rpath, **kwargs):
        base_log_msg = f"local file at {lpath} to remote at {rpath}"
        with self.error_logging(f"Failed to copy {base_log_msg}"):
            result = self.filesystem.put_file(lpath, rpath, **kwargs)
        logger.info(f"Copied {base_log_msg}")
        return result

    def open(self, path: str, mode: str, **kwargs):
        base_log_msg = f"remote file at {path} with {mode=}"
        with self.error_logging(f"Failed to open {base_log_msg}"):
            fd = self.filesystem.open(path, mode, **kwargs)
        logger.info(f"Opened {base_log_msg}")
        return fd

    def open_for_writing(
        self, path: str, text: bool = False
    ) -> Union[TextIOWrapper, "AbstractBufferedFile"]:
        """Open a remote file for writing.

        Parameters
        ----------
        path : str
            Path to the file to open.
        text : bool, optional
            Whether to open it in text mode (when `text = True`) or binary mode
            (when `text = False`), by default False

        Examples
        --------
        >>> with fs.open_for_writing("file.txt") as f:
        ...     f.write("Hello, world!")
        >>> with fs.open_for_writing("model.joblib") as f:
        ...     joblib.dump(model, f)
        """
        mode = "wb" if text is False else "w"
        return self.open(path, mode)

    def open_for_reading(
        self, path: str, text: bool = False
    ) -> Union[TextIOWrapper, "AbstractBufferedFile"]:
        mode = "rb" if text is False else "r"
        return self.open(path, mode)

    def move(self, source_path: str, destination_path: str):
        """Move file(s) from one location to another.

        This fails if the target file system is not capable of creating the
        directory, for example if it is write-only or if auto_mkdir=False. There is
        no command line equivalent of this scenario without an explicit mkdir to
        create the new directory.
        See https://filesystem-spec.readthedocs.io/en/latest/copying.html for more
        information.
        """
        base_log_msg = f"remote file(s) from {source_path} to {destination_path}"
        with self.error_logging(f"Failed to move {base_log_msg}"):
            result = self.filesystem.mv(source_path, destination_path)
        logger.info(f"Moved {base_log_msg}")
        return result

    def _remove_prefix(
        self, files: list[str], remove_root_folder: bool = True, remove_prefix: str | None = None
    ):
        if remove_root_folder is True:
            files = [file.lstrip("/").partition("/")[2] for file in files]

        if remove_prefix is not None:
            files = [
                (file.replace(remove_prefix, "", 1) if file.startswith(remove_prefix) else file)
                for file in files
            ]

        return files

    @overload
    def list_files(
        self,
        path: str,
        recursive: bool = False,
        remove_root_folder: bool = False,
        remove_prefix: str | None = None,
        detail: Literal[False] = False,
    ) -> list[str]: ...
    @overload
    def list_files(
        self,
        path: str,
        recursive: bool = False,
        remove_root_folder: bool = False,
        remove_prefix: str | None = None,
        detail: Literal[True] = True,
    ) -> dict[str, dict[str, Any]]: ...
    def list_files(
        self, path, recursive=False, remove_root_folder=False, remove_prefix=None, detail=False
    ):
        """List files in a remote directory.

        Parameters
        ----------
        path : str
            Path at which to list objects.
        recursive : bool, optional
            Whether to list objects that are deeper than `path`,
            by default False.
        remove_root_folder : bool, optional
            Whether to remove the root folder of `path` in the results,
            by default False.
        remove_prefix : str, optional
            If not None, will remove prefix `remove_prefix` from the results,
            by default None.
        detail : bool, optional
            If True, return a list of dictionaries with details about the
            files. It also disables the `remove_root_folder` and
            `remove_prefix` options. By default False.

        Returns
        -------
        list[str]
            List of objects that exist under `path`.
        """
        if recursive is True:
            maxdepth = None
        else:
            maxdepth = 1

        base_log_msg = f"remote files at {path}"
        with self.error_logging(f"Failed to list {base_log_msg}"):
            files = self.filesystem.find(path, maxdepth, detail=detail)
        logger.info(f"Listed {base_log_msg}")

        if detail is False:
            files = self._remove_prefix(files, remove_root_folder, remove_prefix)
        return files

    @overload
    def glob_files(
        self,
        pattern: str,
        remove_root_folder: bool = False,
        remove_prefix: str | None = None,
        detail: Literal[False] = False,
    ) -> list[str]: ...
    @overload
    def glob_files(
        self,
        pattern: str,
        remove_root_folder: bool = False,
        remove_prefix: str | None = None,
        detail: Literal[True] = True,
    ) -> dict[str, dict[str, Any]]: ...
    def glob_files(self, pattern, remove_root_folder=False, remove_prefix=None, detail=False):
        """List files in a remote directory that match a pattern.

        Parameters
        ----------
        pattern : str
            pattern to list objects with.
        remove_root_folder : bool, optional
            Whether to remove the root folder of `path` in the results,
            by default False.
        remove_prefix : str, optional
            If not None, will remove prefix `remove_prefix` from the results,
            by default None.
        detail : bool, optional
            If True, return a list of dictionaries with details about the
            files. It also disables the `remove_root_folder` and
            `remove_prefix` options. By default False.

        Returns
        -------
        list[str]
            List of objects that matches `pattern`.
        """
        base_log_msg = f"remote files matching {pattern}"
        with self.error_logging(f"Failed to list {base_log_msg}"):
            files = self.filesystem.glob(pattern, detail=detail)
        logger.info(f"Listed {base_log_msg}")

        if detail is False:
            files = self._remove_prefix(files, remove_root_folder, remove_prefix)
        return files

    def remove_files(self, paths: str | list[str], recursive: bool = False):
        base_log_msg = f"remote file(s) at {paths}"
        with self.error_logging(f"Failed to remove {base_log_msg}"):
            result = self.filesystem.rm(paths, recursive)
        logger.info(f"Removed {base_log_msg}")
        return result

    def read_dataset_from_parquet(self, path: str) -> "DataFrame":
        base_log_msg = f"remote dataset from {path}"
        with self.error_logging(f"Failed to read {base_log_msg}"):
            parquet = pyarrow.parquet.ParquetDataset(path, filesystem=self.filesystem)
        logger.info(f"Read {base_log_msg}")

        table = parquet.read_pandas()
        table = convert_decimal_columns_to_double_with_arrow_casting(table)
        return table.to_pandas()

    def write_dataframe_to_parquet(
        self, path: str, df: "DataFrame", replace_spark_forbidden_characters: bool = False
    ):
        base_log_msg = f"remote dataset to {path}"

        if replace_spark_forbidden_characters and col_names_contain_forbidden_chars(df):
            rename_parquet_col_names(df)

        table = pyarrow.Table.from_pandas(df)
        with self.error_logging(f"Failed to write {base_log_msg}"):
            # By default timestamps are in ns resolution, causing a problem of casting to Long type by spark reader,
            # setting coerce_timestamps to us fixes the issue
            result = pyarrow.parquet.write_table(
                table, path, coerce_timestamps="us", filesystem=self.filesystem
            )
        logger.info(f"Wrote {base_log_msg}")
        return result

    def loader(self, path: str, load_method: Callable, text: bool = False) -> object:
        """Loads an object from a remote file using the provided loading function.

        Parameters
        ----------
        path : str
            Path to the object to load.
        load_method : Callable
            Method to use to load the object.
        text : bool, optional
            Whether to open it in text mode (when `text = True`) or binary mode
            (when `text = False`), by default False

        Returns
        -------
        object
            object loaded by the `load_method`.

        Examples
        --------
        >>> data = fs.loader("file.json", json.load)
        >>> data
        {'key': 'value'}
        >>> dataset = fs.loader("file.parquet", pd.read_parquet)
        >>> type(dataset)
        <class 'pandas.core.frame.DataFrame'>
        """
        base_log_msg = f"object with {load_method.__name__} from remote file at {path}"

        mode = "rb" if text is False else "r"

        with self.disable_debug_logging():
            with self.error_logging(f"Failed to load {base_log_msg}"):
                with self.filesystem.open(path, mode) as f:
                    result = load_method(f)
        logger.info(f"Loaded {base_log_msg}")
        return result

    def write_to_file(self, path: str, content: str | bytes | BytesIO | StringIO):
        """Write content to a remote file.

        Parameters
        ----------
        path : str
            Path to the file to write.
        content : str | bytes | BytesIO | StringIO
            Content to write to the file.
        """
        base_log_msg = f"content to remote file at {path}"

        if isinstance(content, (str, StringIO)):
            mode = "w"
        else:
            mode = "wb"

        if isinstance(content, (BytesIO, StringIO)):
            content.seek(0)
            content = content.read()

        create_dir_tree(self.filesystem, path)

        with self.disable_debug_logging():
            with self.error_logging(f"Failed to write {base_log_msg}"):
                with self.filesystem.open(path, mode) as f:
                    # f.write actually supports both str and bytes
                    f.write(content)  # type: ignore[arg-type]
        logger.info(f"Wrote {base_log_msg}")

    def exists(self, path: str) -> bool:
        """Check if a file exists in the remote file system."""
        return self.filesystem.exists(path)
