"""
Library service implementation for KiCad Library Manager.
Core functionality for managing KiCad libraries.
"""

import os
import platform
from pathlib import Path
from typing import Optional

import yaml

from ..utils.env_vars import expand_user_path, update_pinned_libraries
from ..utils.file_ops import (
    list_configured_libraries,
    list_libraries,
    validate_lib_table,
)
from ..utils.metadata import (
    generate_env_var_name,
    get_default_github_metadata,
    read_github_metadata,
    write_github_metadata,
)


class LibraryService:
    """Service for managing KiCad libraries."""

    def list_libraries(self, directory: Path) -> tuple[list[str], list[str]]:
        """List symbol and footprint libraries in a directory."""
        return list_libraries(str(directory))

    def initialize_library(
        self,
        directory: Path,
        name: Optional[str] = None,
        description: Optional[str] = None,
        env_var: Optional[str] = None,
        force: bool = False,
        no_env_var: bool = False,
    ) -> dict:
        """Initialize a library in the given directory."""
        # Check for existing metadata
        metadata = read_github_metadata(directory)

        if metadata and not force:
            # Use existing metadata with potential overrides
            if name:
                metadata["name"] = name
            if description:
                metadata["description"] = description
            if env_var:
                metadata["env_var"] = env_var
            elif no_env_var and "env_var" in metadata:
                del metadata["env_var"]

            if any([name, description, env_var, no_env_var]):
                metadata["updated_with"] = "kilm"
                write_github_metadata(directory, metadata)
        else:
            # Create new metadata
            metadata = get_default_github_metadata(directory)

            if name:
                metadata["name"] = name
                if not env_var and not no_env_var:
                    metadata["env_var"] = generate_env_var_name(name, "KICAD_LIB")

            if description:
                metadata["description"] = description

            if env_var:
                metadata["env_var"] = env_var
            elif no_env_var and "env_var" in metadata:
                del metadata["env_var"]

            write_github_metadata(directory, metadata)

        # Create library directory structure
        self._create_library_structure(directory)

        # Update capabilities
        capabilities: dict[str, bool] = {
            "symbols": (directory / "symbols").exists(),
            "footprints": (directory / "footprints").exists(),
            "templates": (directory / "templates").exists(),
        }
        metadata["capabilities"] = capabilities
        write_github_metadata(directory, metadata)

        return metadata

    def get_library_metadata(self, directory: Path) -> Optional[dict]:
        """Get metadata for a library directory."""
        return read_github_metadata(directory)

    def pin_libraries(
        self,
        symbol_libs: list[str],
        footprint_libs: list[str],
        kicad_config_dir: Path,
        dry_run: bool = False,
        max_backups: int = 5,
    ) -> bool:
        """Pin libraries in KiCad for quick access."""
        return update_pinned_libraries(
            kicad_config_dir,
            symbol_libs=symbol_libs,
            footprint_libs=footprint_libs,
            dry_run=dry_run,
            max_backups=max_backups,
        )

    def unpin_libraries(
        self,
        symbol_libs: list[str],
        footprint_libs: list[str],
        kicad_config_dir: Path,
        dry_run: bool = False,
        max_backups: int = 5,
    ) -> bool:
        """Unpin libraries in KiCad."""
        # This would need to be implemented in utils/env_vars.py
        # For now, we'll return False as it's not implemented
        # TODO: Implement unpin functionality
        _ = symbol_libs, footprint_libs, kicad_config_dir, dry_run, max_backups
        return False

    def _create_library_structure(self, directory: Path) -> tuple[list[str], list[str]]:
        """Create the required directory structure for a library."""
        required_folders = ["symbols", "footprints", "templates"]
        existing_folders = []
        created_folders = []

        for folder in required_folders:
            folder_path = directory / folder
            if folder_path.exists():
                existing_folders.append(folder)
            else:
                folder_path.mkdir(parents=True, exist_ok=True)
                created_folders.append(folder)

        return existing_folders, created_folders

    @staticmethod
    def add_libraries(
        kicad_lib_dir: str,
        kicad_config: Path,
        kicad_3d_dir: Optional[str] = None,
        additional_3d_dirs: Optional[dict[str, str]] = None,
        dry_run: bool = False,
    ) -> tuple[set[str], bool]:
        """
        Add KiCad libraries to the configuration.

        Args:
            kicad_lib_dir: Path to the KiCad library directory
            kicad_config: Path to the KiCad configuration directory
            kicad_3d_dir: Path to the KiCad 3D models directory (optional)
            additional_3d_dirs: Dictionary of additional 3D model directories with their
                            environment variable names as keys (optional)
            dry_run: If True, don't actually make any changes

        Returns:
            Tuple of (set of libraries added, whether changes were needed)

        Raises:
            FileNotFoundError: If the library directory does not exist
            ValueError: If the library directory does not contain symbols or footprints
        """
        # Check if library directory exists
        # First expand any environment variables in the path
        if kicad_lib_dir.startswith("${") and kicad_lib_dir.endswith("}"):
            env_var = kicad_lib_dir[2:-1]
            if env_var in os.environ:
                kicad_lib_dir = os.environ[env_var]
            else:
                raise FileNotFoundError(f"Environment variable {env_var} not found")
        # Check if it's NOT an absolute path (Unix/Windows) or UNC path (Windows)
        # and treat it as a potential environment variable name if it's not.
        elif not (
            kicad_lib_dir.startswith("/")
            or (
                len(kicad_lib_dir) > 2 and kicad_lib_dir[1] == ":"
            )  # Check for C: style paths
            or (
                kicad_lib_dir.startswith("\\\\")
            )  # Check for UNC paths like \\server\share
        ):
            # If it's an environment variable name without ${}
            if kicad_lib_dir in os.environ:
                kicad_lib_dir = os.environ[kicad_lib_dir]
            else:
                raise FileNotFoundError(
                    f"Environment variable {kicad_lib_dir} not found"
                )

        # Now expand any user paths
        kicad_lib_dir = expand_user_path(kicad_lib_dir)
        lib_dir = Path(kicad_lib_dir)
        if not lib_dir.exists():
            raise FileNotFoundError(
                f"KiCad library directory not found: {kicad_lib_dir}"
            )

        # Check if 3D models directory exists
        if kicad_3d_dir:
            kicad_3d_dir = expand_user_path(kicad_3d_dir)
            models_dir = Path(kicad_3d_dir)
            if not models_dir.exists():
                raise FileNotFoundError(
                    f"KiCad 3D models directory not found: {kicad_3d_dir}"
                )

        # Check if additional 3D model directories exist
        all_3d_dirs = {}
        if kicad_3d_dir:
            all_3d_dirs["KICAD_3D_LIB"] = kicad_3d_dir

        if additional_3d_dirs:
            for env_var, path in additional_3d_dirs.items():
                path = expand_user_path(path)
                dir_path = Path(path)
                if not dir_path.exists():
                    print(f"Warning: 3D models directory not found: {path} (skipping)")
                    continue

                # Only add if this is a different path than the main 3D models directory
                if kicad_3d_dir and os.path.normpath(path) == os.path.normpath(
                    kicad_3d_dir
                ):
                    continue

                all_3d_dirs[env_var] = path

        # Get list of available libraries
        symbols, footprints = list_libraries(kicad_lib_dir)
        if not symbols and not footprints:
            raise ValueError(f"No libraries found in {kicad_lib_dir}")

        # Check if library tables exist
        sym_table = kicad_config / "sym-lib-table"
        fp_table = kicad_config / "fp-lib-table"

        # Get existing libraries
        sym_libs, fp_libs = list_configured_libraries(kicad_config)
        sym_lib_names = {lib["name"] for lib in sym_libs}
        fp_lib_names = {lib["name"] for lib in fp_libs}

        # Check for new libraries
        new_symbols = [lib for lib in symbols if lib not in sym_lib_names]
        new_footprints = [lib for lib in footprints if lib not in fp_lib_names]

        # Generate variable references for 3D model paths
        env_var_refs = {}
        for env_var, path in all_3d_dirs.items():
            # Convert to format KiCad expects: ${ENV_VAR}
            env_var_refs[path] = f"${{{env_var}}}"

        # Add new libraries to symbol table
        sym_changes_needed = False
        new_sym_entries = []
        for lib in new_symbols:
            uri = LibraryService.format_uri(kicad_lib_dir, lib, "symbols")

            # Add the library with UTF-8 encoded description
            new_sym_entries.append(
                {
                    "name": lib,
                    "uri": uri,
                    "options": "",
                    "description": LibraryService.get_library_description(
                        "symbols", lib, kicad_lib_dir
                    )
                    .encode("utf-8")
                    .decode("utf-8"),
                }
            )
            sym_changes_needed = True

        # Add new libraries to footprint table
        fp_changes_needed = False
        new_fp_entries = []
        for lib in new_footprints:
            uri = LibraryService.format_uri(kicad_lib_dir, lib, "footprints")

            # Add the library with UTF-8 encoded description
            new_fp_entries.append(
                {
                    "name": lib,
                    "uri": uri,
                    "options": "",
                    "description": LibraryService.get_library_description(
                        "footprints", lib, kicad_lib_dir
                    )
                    .encode("utf-8")
                    .decode("utf-8"),
                }
            )
            fp_changes_needed = True

        # Only make changes if needed
        changes_needed = sym_changes_needed or fp_changes_needed
        if changes_needed and not dry_run:
            # Add new entries to symbol table
            if sym_changes_needed:
                LibraryService.add_entries_to_table(sym_table, new_sym_entries)

            # Add new entries to footprint table
            if fp_changes_needed:
                LibraryService.add_entries_to_table(fp_table, new_fp_entries)

        # Return the set of added libraries
        added_libraries = set(new_symbols + new_footprints)
        return added_libraries, changes_needed

    @staticmethod
    def find_kicad_config() -> Path:
        """
        Find the KiCad configuration directory for the current platform

        Returns:
            Path to the KiCad configuration directory

        Raises:
            FileNotFoundError: If KiCad configuration directory is not found
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Preferences" / "kicad"
        elif system == "Linux":
            config_dir = Path.home() / ".config" / "kicad"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA")
            if not appdata:
                raise FileNotFoundError("APPDATA environment variable not found")
            config_dir = Path(appdata) / "kicad"
        else:
            raise FileNotFoundError(f"Unsupported platform: {system}")

        if not config_dir.exists():
            raise FileNotFoundError(
                f"KiCad configuration directory not found at {config_dir}. "
                "Please run KiCad at least once before using this tool."
            )

        # Find the most recent KiCad version directory
        version_dirs = [d for d in config_dir.iterdir() if d.is_dir()]
        if not version_dirs:
            raise FileNotFoundError(
                f"No KiCad version directories found in {config_dir}. "
                "Please run KiCad at least once before using this tool."
            )

        # Sort directories by version number (assuming directories with numbers are version dirs)
        version_dirs = [d for d in version_dirs if any(c.isdigit() for c in d.name)]
        if not version_dirs:
            raise FileNotFoundError(
                f"No KiCad version directories found in {config_dir}. "
                "Please run KiCad at least once before using this tool."
            )

        latest_dir = sorted(version_dirs, key=lambda d: d.name)[-1]

        # Check for required files
        sym_table = latest_dir / "sym-lib-table"
        fp_table = latest_dir / "fp-lib-table"

        if not sym_table.exists() and not fp_table.exists():
            raise FileNotFoundError(
                f"KiCad library tables not found in {latest_dir}. "
                "Please run KiCad at least once before using this tool."
            )

        return latest_dir

    @staticmethod
    def get_library_description(
        lib_type: str, lib_name: str, kicad_lib_dir: str
    ) -> str:
        """
        Get a description for a library from the YAML file or generate a default one

        Args:
            lib_type: Either 'symbols' or 'footprints'
            lib_name: The name of the library
            kicad_lib_dir: The KiCad library directory

        Returns:
            A description for the library
        """
        yaml_file = Path(kicad_lib_dir) / "library_descriptions.yaml"

        # Check if YAML file exists
        if yaml_file.exists():
            try:
                with yaml_file.open() as f:
                    data = yaml.safe_load(f)

                if (
                    data
                    and isinstance(data, dict)
                    and lib_type in data
                    and isinstance(data[lib_type], dict)
                    and lib_name in data[lib_type]
                ):
                    return data[lib_type][lib_name]
            except Exception:
                pass

        # Default description if YAML file doesn't exist or doesn't contain the library
        if lib_type == "symbols":
            return f"{lib_name} symbol library"
        else:
            return f"{lib_name} footprint library"

    @staticmethod
    def format_uri(base_path: str, lib_name: str, lib_type: str) -> str:
        """
        Format a URI for a KiCad library.

        Args:
            base_path: The base path to the library directory
            lib_name: The name of the library
            lib_type: The type of library (symbols or footprints)

        Returns:
            The formatted URI string

        Raises:
            ValueError: If base_path is empty, lib_type is invalid, or path format is invalid
        """
        if not base_path:
            raise ValueError("Base path cannot be empty")

        if lib_type not in ["symbols", "footprints"]:
            raise ValueError(f"Invalid library type: {lib_type}")

        # Validate ${...} format if present
        if base_path.startswith("${") and not base_path.endswith("}"):
            raise ValueError(f"Invalid environment variable format: {base_path}")

        # Helper function to check if a path is absolute
        def is_absolute_path(path: str) -> bool:
            return (
                path.startswith("/")  # Unix-style
                or path.startswith("\\")  # Windows-style with backslash
                or (len(path) > 1 and path[1] == ":")  # Windows-style with drive letter
            )

        # Normalize path separators to forward slashes first
        base_path = base_path.replace("\\", "/")

        # Check if the path is already in ${...} format
        if base_path.startswith("${") and base_path.endswith("}"):
            # Extract the path from inside the curly braces
            path = base_path[2:-1]
            if is_absolute_path(path):
                # If it's an absolute path, remove the ${...} wrapper
                base_path = path
            # Otherwise, keep the ${...} wrapper for environment variables
        else:
            # If it's not in ${...} format, check if it's an absolute path
            if not is_absolute_path(base_path):
                # If it's not an absolute path, treat it as an environment variable
                base_path = f"${{{base_path}}}"

        # Construct the URI based on library type
        if lib_type == "symbols":
            return f"{base_path}/symbols/{lib_name}.kicad_sym"
        else:
            return f"{base_path}/footprints/{lib_name}.pretty"

    @staticmethod
    def add_entries_to_table(table_path: Path, entries: list[dict[str, str]]) -> None:
        """
        Add entries to a KiCad library table file

        Args:
            table_path: Path to the library table
            entries: List of entries to add
        """
        # Make sure the table exists and has a valid format
        validate_lib_table(table_path, False)

        # Read existing content, ensuring UTF-8 encoding
        with table_path.open(encoding="utf-8") as f:
            content = f.read()

        # Find the last proper closing parenthesis of the table
        closing_paren_index = -1
        lines = content.splitlines()
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == ")":
                closing_paren_index = i
                break

        if closing_paren_index == -1:
            raise ValueError(
                f"Could not find closing parenthesis in library table: {table_path}"
            )

        # Insert new entries before the closing parenthesis
        new_content = ""
        for i, line in enumerate(lines):
            if i == closing_paren_index:
                # Insert entries before the closing parenthesis line
                for entry in entries:
                    # Process the URI to make sure it's properly formatted
                    uri = entry["uri"]

                    # Check if URI starts with ${/ or ${\ - this indicates an improperly formatted path
                    if uri.startswith("${/") or uri.startswith("${\\"):
                        # Extract the path from inside the curly braces using a more robust method
                        try:
                            # Find the first { and last }
                            start = uri.find("{")
                            end = uri.rfind("}")
                            if start != -1 and end != -1 and end > start:
                                path = uri[start + 1 : end]
                                # Replace with the actual path without environment variable syntax
                                uri = path + uri[end + 1 :]
                        except Exception:
                            # If there's any error in processing, keep the original URI
                            pass

                    # Format the entry with proper escaping
                    entry_str = (
                        f"  (lib "
                        f'(name "{entry["name"]}")'
                        f'(type "KiCad")'
                        f'(uri "{uri}")'
                        f'(options "{entry["options"]}")'
                        f'(descr "{entry["description"]}"))\n'
                    )
                    new_content += entry_str

            new_content += line + "\n"

        # Write updated content, ensuring UTF-8 encoding
        with table_path.open("w", encoding="utf-8") as f:
            f.write(new_content)
