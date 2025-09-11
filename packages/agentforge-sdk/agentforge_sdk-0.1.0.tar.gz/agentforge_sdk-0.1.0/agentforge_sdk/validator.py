# in agentforge_sdk/validator.py

import json
from pathlib import Path

MANIFEST_FILE = "agentforge.json"

class ManifestValidator:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.manifest_path = self.root / MANIFEST_FILE
        self.errors = []
        self.manifest_data = None
        self.required_fields = [
            "manifestVersion", "name", "pluginId", "version",
            "author", "description", "roleName", "tools"
        ]

    def _add_error(self, message):
        self.errors.append(message)

    def _check_file_exists(self):
        if not self.manifest_path.is_file():
            self._add_error(f"Manifest file '{MANIFEST_FILE}' not found in the project root.")
            return False
        return True

    def _parse_json(self):
        try:
            with open(self.manifest_path, 'r') as f:
                self.manifest_data = json.load(f)
        except json.JSONDecodeError:
            self._add_error(f"Manifest file '{MANIFEST_FILE}' is not a valid JSON.")
            return False
        except Exception as e:
            self._add_error(f"Could not read manifest file: {e}")
            return False
        return True

    def _check_required_fields(self):
        for field in self.required_fields:
            if field not in self.manifest_data:
                self._add_error(f"Missing required top-level field in manifest: '{field}'")

    def _validate_tools_section(self):
        tools = self.manifest_data.get("tools")
        if not isinstance(tools, list):
            self._add_error("'tools' field must be a list.")
            return

        if not tools:
            self._add_error("'tools' list cannot be empty. A plugin must have at least one tool.")

        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                self._add_error(f"Tool at index {i} is not a valid object.")
                continue

            # Check required fields for each tool
            for field in ["name", "description", "entrypoint"]:
                if field not in tool:
                    self._add_error(f"Tool at index {i} is missing required field: '{field}'")

            # Check if the entrypoint file exists
            entrypoint = tool.get("entrypoint")
            if entrypoint:
                # Entrypoint format is "path.to.file:ClassName"
                try:
                    module_path_str, _ = entrypoint.split(":")
                    file_path_str = module_path_str.replace(".", "/") + ".py"
                    full_path = self.root / file_path_str
                    if not full_path.is_file():
                        self._add_error(f"Entrypoint file not found for tool '{tool.get('name')}': {full_path}")
                except ValueError:
                    self._add_error(f"Invalid entrypoint format for tool '{tool.get('name')}': '{entrypoint}'. Expected 'path.to.file:ClassName'.")


    def run(self) -> bool:
        """Runs all validation checks and returns True if valid, False otherwise."""
        if not self._check_file_exists():
            return False # Stop if manifest doesn't exist

        if not self._parse_json():
            return False # Stop if JSON is invalid

        self._check_required_fields()
        self._validate_tools_section()

        return not self.errors