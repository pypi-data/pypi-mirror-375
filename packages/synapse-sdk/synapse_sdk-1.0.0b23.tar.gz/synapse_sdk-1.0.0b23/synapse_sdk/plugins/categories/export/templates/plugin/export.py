from pathlib import Path
from typing import Generator

from . import BaseExporter


class Exporter(BaseExporter):
    """Plugin export action interface for organizing files.

    This class provides a minimal interface for plugin developers to implement
    their own export logic.
    """

    def __init__(self, run, export_items: Generator, path_root: Path, **params):
        """Initialize the plugin export action class.
        Args:
            run: Plugin run object with logging capabilities.
            export_items (generator):
                - data (dict): dm_schema_data information.
                - files (dict): File information. Includes file URL, original file path, metadata, etc.
                - id (int): target ID (ex. assignment id, task id, ground_truth_event id)
            path_root: pathlib object, the path to export
            **params: Additional parameters
                - name (str): The name of the action.
                - description (str | None): The description of the action.
                - storage (int): The storage ID to save the exported data.
                - save_original_file (bool): Whether to save the original file.
                - path (str): The path to save the exported data.
                - target (str): The target source to export data from. (ex. ground_truth, assignment, task)
                - filter (dict): The filter criteria to apply.
                - extra_params (dict | None): Additional parameters for export customization.
                    Example: {"include_metadata": True, "compression": "gzip"}
                - count (int): Total number of results.
                - results (list): List of results fetched through the list API.
                - project_id (int): Project ID.
                - configuration (dict): Project configuration.
        """
        super().__init__(run, export_items, path_root, **params)

    def export(self, export_items=None, results=None, **kwargs) -> dict:
        """Executes the export task using the base class implementation.

        Args:
            export_items: Optional export items to process. If not provided, uses self.export_items.
            results: Optional results data to process alongside export_items.
            **kwargs: Additional parameters for export customization.

        Returns:
            dict: Result
        """
        return super().export(export_items, results, **kwargs)

    def convert_data(self, data):
        """Converts the data."""
        return data

    def before_convert(self, data):
        """Preprocesses the data before conversion."""
        return data

    def after_convert(self, data):
        """Post-processes the data after conversion."""
        return data
