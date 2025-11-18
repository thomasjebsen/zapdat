"""
Multi-format file reader for data analysis
Supports CSV, Excel, JSON, TSV, Parquet, Feather, Pickle, SQLite, HDF5, and ORC
"""

import os
import sqlite3
import tempfile
from io import BytesIO, StringIO

import pandas as pd


class FileFormatError(Exception):
    """Raised when file format is not supported or cannot be read"""

    pass


class MultiFormatReader:
    """Reads various data file formats and returns pandas DataFrames"""

    # Supported file extensions mapped to their readers
    SUPPORTED_FORMATS = {
        ".csv": "read_csv",
        ".tsv": "read_tsv",
        ".txt": "read_txt",
        ".xlsx": "read_excel",
        ".xls": "read_excel",
        ".json": "read_json",
        ".parquet": "read_parquet",
        ".feather": "read_feather",
        ".pkl": "read_pickle",
        ".pickle": "read_pickle",
        ".db": "read_sqlite",
        ".sqlite": "read_sqlite",
        ".sqlite3": "read_sqlite",
        ".h5": "read_hdf5",
        ".hdf5": "read_hdf5",
        ".orc": "read_orc",
    }

    @classmethod
    def get_supported_formats(cls) -> list:
        """Returns list of supported file extensions"""
        return list(cls.SUPPORTED_FORMATS.keys())

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if file format is supported"""
        ext = cls._get_extension(filename)
        return ext in cls.SUPPORTED_FORMATS

    @staticmethod
    def _get_extension(filename: str) -> str:
        """Extract lowercase file extension from filename"""
        return os.path.splitext(filename.lower())[1]

    @classmethod
    def detect_format(cls, filename: str) -> str:
        """Detect file format from filename extension"""
        ext = cls._get_extension(filename)
        if ext not in cls.SUPPORTED_FORMATS:
            raise FileFormatError(
                f"Unsupported file format: {ext}. "
                f"Supported formats: {', '.join(cls.SUPPORTED_FORMATS.keys())}"
            )
        return ext

    @classmethod
    def read_file(cls, file_content: bytes, filename: str, **kwargs) -> pd.DataFrame:
        """
        Read file content and return a pandas DataFrame

        Args:
            file_content: Raw bytes from uploaded file
            filename: Original filename with extension
            **kwargs: Additional arguments to pass to the reader

        Returns:
            pd.DataFrame: Parsed data

        Raises:
            FileFormatError: If format is unsupported or reading fails
        """
        ext = cls.detect_format(filename)
        reader_method = cls.SUPPORTED_FORMATS[ext]

        try:
            reader = getattr(cls, reader_method)
            return reader(file_content, **kwargs)
        except Exception as e:
            raise FileFormatError(f"Error reading {ext} file: {str(e)}") from e

    @staticmethod
    def read_csv(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read CSV file"""
        text_content = file_content.decode("utf-8")
        return pd.read_csv(StringIO(text_content), **kwargs)

    @staticmethod
    def read_tsv(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read TSV (Tab-Separated Values) file"""
        text_content = file_content.decode("utf-8")
        return pd.read_csv(StringIO(text_content), sep="\t", **kwargs)

    @staticmethod
    def read_txt(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read TXT file (assumes tab-delimited by default)"""
        text_content = file_content.decode("utf-8")
        # Try to auto-detect delimiter
        return pd.read_csv(StringIO(text_content), sep=None, engine="python", **kwargs)

    @staticmethod
    def read_excel(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read Excel file (.xlsx or .xls)"""
        return pd.read_excel(BytesIO(file_content), **kwargs)

    @staticmethod
    def read_json(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read JSON file"""
        text_content = file_content.decode("utf-8")
        # Try different JSON orientations
        try:
            return pd.read_json(StringIO(text_content), **kwargs)
        except ValueError as e:
            # Try with orient='records' for array of objects
            try:
                return pd.read_json(StringIO(text_content), orient="records", **kwargs)
            except ValueError:
                raise FileFormatError(f"Invalid JSON format: {str(e)}") from e

    @staticmethod
    def read_parquet(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read Parquet file"""
        return pd.read_parquet(BytesIO(file_content), **kwargs)

    @staticmethod
    def read_feather(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read Feather file"""
        # Feather requires a file path, so we write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".feather") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            df = pd.read_feather(tmp_path, **kwargs)
            return df
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def read_pickle(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read Pickle file"""
        return pd.read_pickle(BytesIO(file_content), **kwargs)

    @staticmethod
    def read_sqlite(file_content: bytes, table_name: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Read SQLite database file

        Args:
            file_content: SQLite database file bytes
            table_name: Name of table to read (if None, reads first table)
            **kwargs: Additional arguments for read_sql
        """
        # SQLite requires a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            conn = sqlite3.connect(tmp_path)

            # If no table specified, get the first table
            if table_name is None:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                if not tables:
                    raise FileFormatError("No tables found in SQLite database")
                table_name = tables[0][0]

            df = pd.read_sql(f"SELECT * FROM {table_name}", conn, **kwargs)
            conn.close()
            return df
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def read_hdf5(file_content: bytes, key: str | None = None, **kwargs) -> pd.DataFrame:
        """
        Read HDF5 file

        Args:
            file_content: HDF5 file bytes
            key: Key/path to read from HDF5 (if None, reads first key)
            **kwargs: Additional arguments for read_hdf
        """
        # HDF5 requires a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        try:
            # If no key specified, try to get the first one
            if key is None:
                with pd.HDFStore(tmp_path, "r") as store:
                    keys = store.keys()
                    if not keys:
                        raise FileFormatError("No datasets found in HDF5 file")
                    key = keys[0]

            df = pd.read_hdf(tmp_path, key=key, **kwargs)
            return df
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def read_orc(file_content: bytes, **kwargs) -> pd.DataFrame:
        """Read ORC file"""
        return pd.read_orc(BytesIO(file_content), **kwargs)
