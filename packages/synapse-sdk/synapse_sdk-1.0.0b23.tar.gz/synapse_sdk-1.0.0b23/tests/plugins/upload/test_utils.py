import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from synapse_sdk.plugins.categories.upload.actions.upload import (
    ExcelMetadataUtils,
    ExcelSecurityConfig,
    PathAwareJSONEncoder,
)


class TestPathAwareJSONEncoder:
    """Test PathAwareJSONEncoder class."""

    def test_path_object_encoding(self):
        """Test encoding Path objects."""
        encoder = PathAwareJSONEncoder()
        path = Path('/test/path')
        result = encoder.default(path)
        assert result == '/test/path'

    def test_datetime_encoding(self):
        """Test encoding datetime objects."""
        encoder = PathAwareJSONEncoder()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = encoder.default(dt)
        assert result == '2023-01-01T12:00:00'

    def test_string_with_fspath(self):
        """Test encoding objects with __fspath__ method."""
        encoder = PathAwareJSONEncoder()

        class MockPathLike:
            def __fspath__(self):
                return '/mock/path'

        obj = MockPathLike()
        result = encoder.default(obj)
        assert result == '/mock/path'

    def test_fallback_to_parent(self):
        """Test fallback to parent encoder for unknown objects."""
        encoder = PathAwareJSONEncoder()

        class UnknownObject:
            pass

        obj = UnknownObject()
        try:
            encoder.default(obj)
            assert False, 'Should have raised TypeError'
        except TypeError:
            pass

    def test_full_json_encoding(self):
        """Test full JSON encoding with mixed types."""
        data = {'path': Path('/test/path'), 'timestamp': datetime(2023, 1, 1), 'name': 'test'}
        result = json.dumps(data, cls=PathAwareJSONEncoder)
        expected = '{"path": "/test/path", "timestamp": "2023-01-01T00:00:00", "name": "test"}'
        assert result == expected


class TestExcelSecurityConfig:
    """Test ExcelSecurityConfig class."""

    def test_default_config_values(self):
        """Test default configuration values."""
        config = ExcelSecurityConfig()
        assert config.MAX_FILE_SIZE_MB == 10
        assert config.MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024
        assert config.MAX_MEMORY_USAGE_MB == 30
        assert config.MAX_MEMORY_USAGE_BYTES == 30 * 1024 * 1024
        assert config.MAX_ROWS == 10000
        assert config.MAX_COLUMNS == 50
        assert config.MAX_FILENAME_LENGTH == 255
        assert config.MAX_COLUMN_NAME_LENGTH == 100
        assert config.MAX_METADATA_VALUE_LENGTH == 1000

    @patch.dict(
        os.environ,
        {
            'EXCEL_MAX_FILE_SIZE_MB': '20',
            'EXCEL_MAX_MEMORY_MB': '50',
            'EXCEL_MAX_ROWS': '20000',
            'EXCEL_MAX_COLUMNS': '100',
            'EXCEL_MAX_FILENAME_LENGTH': '500',
            'EXCEL_MAX_COLUMN_NAME_LENGTH': '200',
            'EXCEL_MAX_METADATA_VALUE_LENGTH': '2000',
        },
    )
    def test_config_from_environment(self):
        """Test configuration values from environment variables."""
        config = ExcelSecurityConfig()
        assert config.MAX_FILE_SIZE_MB == 20
        assert config.MAX_FILE_SIZE_BYTES == 20 * 1024 * 1024
        assert config.MAX_MEMORY_USAGE_MB == 50
        assert config.MAX_MEMORY_USAGE_BYTES == 50 * 1024 * 1024
        assert config.MAX_ROWS == 20000
        assert config.MAX_COLUMNS == 100
        assert config.MAX_FILENAME_LENGTH == 500
        assert config.MAX_COLUMN_NAME_LENGTH == 200
        assert config.MAX_METADATA_VALUE_LENGTH == 2000


class TestExcelMetadataUtils:
    """Test ExcelMetadataUtils class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = ExcelSecurityConfig()
        self.utils = ExcelMetadataUtils(self.config)

    def test_validate_and_truncate_string_normal(self):
        """Test string validation with normal input."""
        result = self.utils.validate_and_truncate_string('test', 10)
        assert result == 'test'

    def test_validate_and_truncate_string_truncation(self):
        """Test string truncation when exceeding max length."""
        long_string = 'a' * 15
        result = self.utils.validate_and_truncate_string(long_string, 10)
        assert result == 'a' * 10

    def test_validate_and_truncate_string_with_spaces(self):
        """Test string validation trims whitespace."""
        result = self.utils.validate_and_truncate_string('  test  ', 10)
        assert result == 'test'

    def test_validate_and_truncate_string_non_string_input(self):
        """Test string validation converts non-string input."""
        result = self.utils.validate_and_truncate_string(123, 10)
        assert result == '123'

    def test_is_valid_filename_length_valid(self):
        """Test filename length validation with valid filename."""
        filename = 'test.xlsx'
        result = self.utils.is_valid_filename_length(filename)
        assert result is True

    def test_is_valid_filename_length_invalid(self):
        """Test filename length validation with too long filename."""
        filename = 'x' * 300
        result = self.utils.is_valid_filename_length(filename)
        assert result is False

    def test_is_valid_filename_length_with_spaces(self):
        """Test filename length validation trims spaces."""
        filename = '  test.xlsx  '
        result = self.utils.is_valid_filename_length(filename)
        assert result is True
