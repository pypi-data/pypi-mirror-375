import json
import os


class PathAwareJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Path objects and datetime objects.

    Extends the default JSON encoder to properly serialize Path objects
    and datetime objects that are commonly used in upload operations.

    Supported object types:
    - Path objects (converts to string using __fspath__ or as_posix)
    - Datetime objects (converts using isoformat)
    - All other standard JSON-serializable types

    Example:
        >>> data = {"path": Path("/tmp/file.txt"), "timestamp": datetime.now()}
        >>> json.dumps(data, cls=PathAwareJSONEncoder)
        '{"path": "/tmp/file.txt", "timestamp": "2023-01-01T12:00:00"}'
    """

    def default(self, obj):
        if hasattr(obj, '__fspath__'):
            return obj.__fspath__()
        elif hasattr(obj, 'as_posix'):
            return obj.as_posix()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)


class ExcelSecurityConfig:
    """Configuration class for Excel file security limits.

    Manages security constraints for Excel file processing to prevent
    resource exhaustion and security vulnerabilities. All limits can
    be configured via environment variables.

    Attributes:
        MAX_FILE_SIZE_MB (int): Maximum file size in megabytes
        MAX_FILE_SIZE_BYTES (int): Maximum file size in bytes
        MAX_MEMORY_USAGE_MB (int): Maximum memory usage in megabytes
        MAX_MEMORY_USAGE_BYTES (int): Maximum memory usage in bytes
        MAX_ROWS (int): Maximum number of rows allowed
        MAX_COLUMNS (int): Maximum number of columns allowed
        MAX_FILENAME_LENGTH (int): Maximum filename length
        MAX_COLUMN_NAME_LENGTH (int): Maximum column name length
        MAX_METADATA_VALUE_LENGTH (int): Maximum metadata value length

    Environment Variables:
        EXCEL_MAX_FILE_SIZE_MB: Override default file size limit (default: 10)
        EXCEL_MAX_MEMORY_MB: Override default memory limit (default: 30)
        EXCEL_MAX_ROWS: Override default row limit (default: 10000)
        EXCEL_MAX_COLUMNS: Override default column limit (default: 50)
        EXCEL_MAX_FILENAME_LENGTH: Override filename length limit (default: 255)
        EXCEL_MAX_COLUMN_NAME_LENGTH: Override column name length (default: 100)
        EXCEL_MAX_METADATA_VALUE_LENGTH: Override metadata value length (default: 1000)
    """

    def __init__(self):
        self.MAX_FILE_SIZE_MB = int(os.getenv('EXCEL_MAX_FILE_SIZE_MB', '10'))
        self.MAX_FILE_SIZE_BYTES = self.MAX_FILE_SIZE_MB * 1024 * 1024

        self.MAX_MEMORY_USAGE_MB = int(os.getenv('EXCEL_MAX_MEMORY_MB', '30'))
        self.MAX_MEMORY_USAGE_BYTES = self.MAX_MEMORY_USAGE_MB * 1024 * 1024

        self.MAX_ROWS = int(os.getenv('EXCEL_MAX_ROWS', '10000'))
        self.MAX_COLUMNS = int(os.getenv('EXCEL_MAX_COLUMNS', '50'))

        self.MAX_FILENAME_LENGTH = int(os.getenv('EXCEL_MAX_FILENAME_LENGTH', '255'))
        self.MAX_COLUMN_NAME_LENGTH = int(os.getenv('EXCEL_MAX_COLUMN_NAME_LENGTH', '100'))
        self.MAX_METADATA_VALUE_LENGTH = int(os.getenv('EXCEL_MAX_METADATA_VALUE_LENGTH', '1000'))


class ExcelMetadataUtils:
    """Utility class for Excel metadata processing and validation.

    Provides helper methods for validating and processing Excel metadata
    while respecting security constraints defined in ExcelSecurityConfig.

    Args:
        config (ExcelSecurityConfig): Security configuration instance

    Example:
        >>> config = ExcelSecurityConfig()
        >>> utils = ExcelMetadataUtils(config)
        >>> safe_value = utils.validate_and_truncate_string("long text", 10)
        >>> is_valid = utils.is_valid_filename_length("file.xlsx")
    """

    def __init__(self, config: ExcelSecurityConfig):
        self.config = config

    def validate_and_truncate_string(self, value: str, max_length: int) -> str:
        """Validate and truncate string to maximum length.

        Converts non-string values to strings, trims whitespace, and
        truncates to the specified maximum length if necessary.

        Args:
            value (str): Value to validate and truncate
            max_length (int): Maximum allowed length

        Returns:
            str: Validated and truncated string

        Example:
            >>> utils.validate_and_truncate_string("  long text  ", 5)
            'long '
        """
        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        if len(value) > max_length:
            return value[:max_length]

        return value

    def is_valid_filename_length(self, filename: str) -> bool:
        """Check if filename length is within security limits.

        Validates that the filename (after trimming whitespace) does not
        exceed the maximum filename length configured in security settings.

        Args:
            filename (str): Filename to validate

        Returns:
            bool: True if filename length is valid, False otherwise

        Example:
            >>> utils.is_valid_filename_length("file.xlsx")
            True
            >>> utils.is_valid_filename_length("x" * 300)
            False
        """
        return len(filename.strip()) <= self.config.MAX_FILENAME_LENGTH
