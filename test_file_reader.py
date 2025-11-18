"""
Unit tests for multi-format file reader
"""

import os
import sqlite3
import tempfile
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
import pytest

from backend.file_reader import FileFormatError, MultiFormatReader


# Sample test data
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "age": [25, 30, 35, 28, 32],
            "score": [85.5, 92.0, 78.5, 88.0, 95.5],
            "active": [True, True, False, True, False],
        }
    )


class TestMultiFormatReader:
    """Test suite for MultiFormatReader"""

    def test_get_supported_formats(self):
        """Test that supported formats list is returned"""
        formats = MultiFormatReader.get_supported_formats()
        assert isinstance(formats, list)
        assert ".csv" in formats
        assert ".xlsx" in formats
        assert ".json" in formats
        assert len(formats) >= 10

    def test_is_supported(self):
        """Test format support detection"""
        assert MultiFormatReader.is_supported("data.csv") is True
        assert MultiFormatReader.is_supported("data.xlsx") is True
        assert MultiFormatReader.is_supported("data.json") is True
        assert MultiFormatReader.is_supported("data.unsupported") is False

    def test_detect_format(self):
        """Test format detection from filename"""
        assert MultiFormatReader.detect_format("data.csv") == ".csv"
        assert MultiFormatReader.detect_format("data.CSV") == ".csv"
        assert MultiFormatReader.detect_format("data.xlsx") == ".xlsx"

        with pytest.raises(FileFormatError):
            MultiFormatReader.detect_format("data.unsupported")

    def test_read_csv(self, sample_dataframe):
        """Test CSV reading"""
        # Create CSV bytes
        csv_buffer = StringIO()
        sample_dataframe.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # Read CSV
        df = MultiFormatReader.read_csv(csv_bytes)

        assert len(df) == 5
        assert list(df.columns) == list(sample_dataframe.columns)
        assert df["name"].tolist() == sample_dataframe["name"].tolist()

    def test_read_csv_via_read_file(self, sample_dataframe):
        """Test CSV reading via read_file method"""
        csv_buffer = StringIO()
        sample_dataframe.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        df = MultiFormatReader.read_file(csv_bytes, "test.csv")

        assert len(df) == 5
        assert "name" in df.columns

    def test_read_tsv(self, sample_dataframe):
        """Test TSV reading"""
        # Create TSV bytes
        tsv_buffer = StringIO()
        sample_dataframe.to_csv(tsv_buffer, sep="\t", index=False)
        tsv_bytes = tsv_buffer.getvalue().encode("utf-8")

        # Read TSV
        df = MultiFormatReader.read_tsv(tsv_bytes)

        assert len(df) == 5
        assert list(df.columns) == list(sample_dataframe.columns)

    def test_read_excel(self, sample_dataframe):
        """Test Excel reading"""
        # Create Excel bytes
        excel_buffer = BytesIO()
        sample_dataframe.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_bytes = excel_buffer.getvalue()

        # Read Excel
        df = MultiFormatReader.read_excel(excel_bytes)

        assert len(df) == 5
        assert list(df.columns) == list(sample_dataframe.columns)
        assert df["name"].tolist() == sample_dataframe["name"].tolist()

    def test_read_excel_via_read_file(self, sample_dataframe):
        """Test Excel reading via read_file with .xlsx extension"""
        excel_buffer = BytesIO()
        sample_dataframe.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_bytes = excel_buffer.getvalue()

        df = MultiFormatReader.read_file(excel_bytes, "test.xlsx")

        assert len(df) == 5
        assert "name" in df.columns

    def test_read_json_records(self, sample_dataframe):
        """Test JSON reading with records orientation"""
        # Create JSON bytes (records format)
        json_str = sample_dataframe.to_json(orient="records")
        json_bytes = json_str.encode("utf-8")

        # Read JSON
        df = MultiFormatReader.read_json(json_bytes)

        assert len(df) == 5
        assert set(df.columns) == set(sample_dataframe.columns)

    def test_read_json_split(self, sample_dataframe):
        """Test JSON reading with split orientation"""
        json_str = sample_dataframe.to_json(orient="split")
        json_bytes = json_str.encode("utf-8")

        df = MultiFormatReader.read_json(json_bytes, orient="split")

        assert len(df) == 5

    def test_read_parquet(self, sample_dataframe):
        """Test Parquet reading"""
        # Create Parquet bytes
        parquet_buffer = BytesIO()
        sample_dataframe.to_parquet(parquet_buffer, index=False)
        parquet_bytes = parquet_buffer.getvalue()

        # Read Parquet
        df = MultiFormatReader.read_parquet(parquet_bytes)

        assert len(df) == 5
        assert list(df.columns) == list(sample_dataframe.columns)

    def test_read_feather(self, sample_dataframe):
        """Test Feather reading"""
        # Create Feather bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".feather") as tmp:
            sample_dataframe.to_feather(tmp.name)
            tmp.seek(0)

        try:
            with open(tmp.name, "rb") as f:
                feather_bytes = f.read()

            # Read Feather
            df = MultiFormatReader.read_feather(feather_bytes)

            assert len(df) == 5
            assert list(df.columns) == list(sample_dataframe.columns)
        finally:
            os.unlink(tmp.name)

    def test_read_pickle(self, sample_dataframe):
        """Test Pickle reading"""
        # Create Pickle bytes
        pickle_buffer = BytesIO()
        sample_dataframe.to_pickle(pickle_buffer)
        pickle_bytes = pickle_buffer.getvalue()

        # Read Pickle
        df = MultiFormatReader.read_pickle(pickle_bytes)

        assert len(df) == 5
        assert list(df.columns) == list(sample_dataframe.columns)

    def test_read_sqlite(self, sample_dataframe):
        """Test SQLite reading"""
        # Create SQLite database
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            conn = sqlite3.connect(tmp.name)
            sample_dataframe.to_sql("test_table", conn, index=False)
            conn.close()

            with open(tmp.name, "rb") as f:
                sqlite_bytes = f.read()

        try:
            # Read SQLite (auto-detect table)
            df = MultiFormatReader.read_sqlite(sqlite_bytes)

            assert len(df) == 5
            assert set(df.columns) == set(sample_dataframe.columns)

            # Read SQLite with specific table
            df2 = MultiFormatReader.read_sqlite(sqlite_bytes, table_name="test_table")
            assert len(df2) == 5
        finally:
            os.unlink(tmp.name)

    def test_read_hdf5(self, sample_dataframe):
        """Test HDF5 reading"""
        # Create HDF5 file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as tmp:
            sample_dataframe.to_hdf(tmp.name, key="data", mode="w")

            with open(tmp.name, "rb") as f:
                hdf5_bytes = f.read()

        try:
            # Read HDF5 (auto-detect key)
            df = MultiFormatReader.read_hdf5(hdf5_bytes)

            assert len(df) == 5
            assert list(df.columns) == list(sample_dataframe.columns)

            # Read HDF5 with specific key
            df2 = MultiFormatReader.read_hdf5(hdf5_bytes, key="data")
            assert len(df2) == 5
        finally:
            os.unlink(tmp.name)

    def test_read_orc(self, sample_dataframe):
        """Test ORC reading"""
        try:
            # Create ORC bytes
            orc_buffer = BytesIO()
            sample_dataframe.to_orc(orc_buffer, index=False)
            orc_bytes = orc_buffer.getvalue()

            # Read ORC
            df = MultiFormatReader.read_orc(orc_bytes)

            assert len(df) == 5
            assert set(df.columns) == set(sample_dataframe.columns)
        except ImportError:
            pytest.skip("pyarrow not installed for ORC support")

    def test_empty_csv(self):
        """Test handling of empty CSV"""
        csv_bytes = b"col1,col2\n"

        df = MultiFormatReader.read_csv(csv_bytes)

        assert len(df) == 0
        assert list(df.columns) == ["col1", "col2"]

    def test_malformed_csv(self):
        """Test handling of malformed CSV"""
        csv_bytes = b"not,a,valid\ncsv,file"

        # Should not raise error, pandas is lenient
        df = MultiFormatReader.read_csv(csv_bytes)
        assert len(df) >= 0

    def test_unsupported_format_error(self):
        """Test error handling for unsupported formats"""
        with pytest.raises(FileFormatError) as exc_info:
            MultiFormatReader.read_file(b"data", "file.unsupported")

        assert "Unsupported file format" in str(exc_info.value)

    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        invalid_json = b"{invalid json content"

        with pytest.raises(FileFormatError):
            MultiFormatReader.read_json(invalid_json)

    def test_case_insensitive_extensions(self, sample_dataframe):
        """Test that file extensions are case-insensitive"""
        csv_buffer = StringIO()
        sample_dataframe.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # Should work with uppercase extension
        df = MultiFormatReader.read_file(csv_bytes, "TEST.CSV")
        assert len(df) == 5

        df2 = MultiFormatReader.read_file(csv_bytes, "test.CsV")
        assert len(df2) == 5

    def test_txt_file_auto_delimiter(self):
        """Test TXT file reading with auto-delimiter detection"""
        # Tab-delimited
        txt_bytes = b"col1\tcol2\tcol3\n1\t2\t3\n4\t5\t6\n"
        df = MultiFormatReader.read_txt(txt_bytes)

        assert len(df) == 2
        assert len(df.columns) == 3

    def test_excel_multiple_sheets(self, sample_dataframe):
        """Test reading specific sheet from Excel"""
        # Create Excel with multiple sheets
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            sample_dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
            sample_dataframe.to_excel(writer, sheet_name="Sheet2", index=False)
        excel_bytes = excel_buffer.getvalue()

        # Read default sheet
        df1 = MultiFormatReader.read_excel(excel_bytes)
        assert len(df1) == 5

        # Read specific sheet
        df2 = MultiFormatReader.read_excel(excel_bytes, sheet_name="Sheet2")
        assert len(df2) == 5


class TestFileReaderIntegration:
    """Integration tests for file reader"""

    def test_read_file_workflow(self, sample_dataframe):
        """Test complete workflow: detect -> read -> analyze"""
        formats_to_test = [
            ("test.csv", lambda df: df.to_csv(index=False).encode("utf-8")),
            ("test.json", lambda df: df.to_json(orient="records").encode("utf-8")),
        ]

        for filename, create_bytes in formats_to_test:
            file_bytes = create_bytes(sample_dataframe)

            # Detect format
            assert MultiFormatReader.is_supported(filename)

            # Read file
            df = MultiFormatReader.read_file(file_bytes, filename)

            # Verify
            assert len(df) == 5
            assert "name" in df.columns
            assert "age" in df.columns

    def test_real_world_csv_edge_cases(self):
        """Test real-world CSV edge cases"""
        # CSV with quotes and commas in values
        csv_with_quotes = b'"name","description"\n"John Doe","Hello, World"\n"Jane","Test, 123"'
        df = MultiFormatReader.read_csv(csv_with_quotes)
        assert len(df) == 2
        assert df["description"].iloc[0] == "Hello, World"

        # CSV with missing values
        csv_with_missing = b"a,b,c\n1,2,3\n4,,6\n,,9"
        df = MultiFormatReader.read_csv(csv_with_missing)
        assert len(df) == 3
        assert pd.isna(df["b"].iloc[1])

    def test_large_file_handling(self):
        """Test handling of larger files"""
        # Create a larger DataFrame
        large_df = pd.DataFrame(
            {"col1": range(10000), "col2": np.random.rand(10000), "col3": ["text"] * 10000}
        )

        # Test CSV
        csv_bytes = large_df.to_csv(index=False).encode("utf-8")
        df = MultiFormatReader.read_csv(csv_bytes)
        assert len(df) == 10000

        # Test Parquet (more efficient for large data)
        parquet_buffer = BytesIO()
        large_df.to_parquet(parquet_buffer, index=False)
        parquet_bytes = parquet_buffer.getvalue()
        df = MultiFormatReader.read_parquet(parquet_bytes)
        assert len(df) == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
