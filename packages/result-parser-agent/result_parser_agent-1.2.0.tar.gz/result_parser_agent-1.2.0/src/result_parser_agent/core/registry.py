"""Tool Registry for workload-specific extraction tools."""

import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

from ..api import create_registry_client
from ..utils.downloader import ScriptDownloader


class ToolRegistry:
    """Manages workload-specific extraction tools via API registry and script downloader."""

    def __init__(self, scripts_dir: str = "scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.api_client = None  # Lazy initialization
        self.script_downloader = ScriptDownloader()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure scripts directory exists."""
        self.scripts_dir.mkdir(exist_ok=True)

    def _get_api_client(self):
        """Get API client with lazy initialization."""
        if self.api_client is None:
            self.api_client = create_registry_client()
        return self.api_client

    def _store_workload_metadata(
        self, workload_name: str, tool_info: dict[str, Any]
    ) -> None:
        """Store workload metadata alongside the script for future cache lookups."""
        try:
            import json

            # Normalize workload name for consistent storage
            normalized_name = workload_name.lower()
            metadata_path = (
                self.script_downloader.cache_dir / normalized_name / "metadata.json"
            )

            # Ensure directory exists
            metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Store metadata (excluding script_path as it will be regenerated)
            metadata = {k: v for k, v in tool_info.items() if k != "script_path"}
            metadata["cached"] = True

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.debug(
                f"Stored metadata for workload '{workload_name}' at {metadata_path}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to store metadata for workload '{workload_name}': {e}"
            )

    def _load_workload_metadata(self, workload_name: str) -> dict[str, Any] | None:
        """Load workload metadata from cache."""
        try:
            import json

            # Normalize workload name for consistent lookup
            normalized_name = workload_name.lower()
            metadata_path = (
                self.script_downloader.cache_dir / normalized_name / "metadata.json"
            )

            if not metadata_path.exists():
                return None

            with open(metadata_path) as f:
                metadata = json.load(f)

            # Add script path
            script_name = metadata.get("script", "extractor.sh")
            script_path = (
                self.script_downloader.cache_dir / normalized_name / script_name
            )
            metadata["script_path"] = str(script_path)

            return metadata
        except Exception as e:
            logger.warning(
                f"Failed to load metadata for workload '{workload_name}': {e}"
            )
            return None

    def list_cached_workloads(self) -> list[str]:
        """List workloads available in local cache (normalized to lowercase)."""
        try:
            cache_info = self.script_downloader.get_cache_info()
            return [workload["name"] for workload in cache_info.get("workloads", [])]
        except Exception as e:
            logger.error(f"Failed to list cached workloads: {e}")
            return []

    def get_cached_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get workload tool info from cache only (no API call)."""
        try:
            # Normalize workload name for consistent lookup
            normalized_name = workload_name.lower()
            script_name = "extractor.sh"  # Default script name
            script_path = (
                self.script_downloader.cache_dir / normalized_name / script_name
            )

            if not script_path.exists():
                return None

            # Try to load stored metadata first
            metadata = self._load_workload_metadata(workload_name)
            if metadata:
                return metadata

            # Fallback to basic info if no metadata found
            return {
                "script": script_name,
                "description": f"Cached workload: {normalized_name}",
                "metrics": [],  # Will be populated when script is executed
                "status": "active",
                "cached": True,
            }
        except Exception as e:
            logger.error(
                f"Failed to get cached workload tool for '{workload_name}': {e}"
            )
            return None

    def list_workloads_from_registry(self) -> list[str]:
        """List all available workloads from registry API."""
        try:
            api_client = self._get_api_client()
            return api_client.list_workload_names()
        except Exception as e:
            logger.error(f"Failed to list workloads from registry: {e}")
            return []

    def get_workload_tool_from_registry(
        self, workload_name: str
    ) -> dict[str, Any] | None:
        """Get extraction tool for a specific workload from registry API."""
        try:
            api_client = self._get_api_client()
            return api_client.get_workload_tool(workload_name)
        except Exception as e:
            logger.error(
                f"Failed to get workload tool from registry for '{workload_name}': {e}"
            )
            return None

    def download_workload_from_registry(
        self, workload_name: str
    ) -> dict[str, Any] | None:
        """Download workload script from registry and cache it."""
        try:
            # Get workload info from registry
            tool_info = self.get_workload_tool_from_registry(workload_name)
            if not tool_info:
                return None

            # Download the script
            script_name = tool_info.get("script", "extractor.sh")
            script_path = self.script_downloader.get_script(workload_name, script_name)

            # Store metadata alongside the script for future cache lookups
            self._store_workload_metadata(workload_name, tool_info)

            # Return the tool info with updated path
            tool_info["script_path"] = str(script_path)
            tool_info["cached"] = True
            return tool_info

        except Exception as e:
            logger.error(
                f"Failed to download workload '{workload_name}' from registry: {e}"
            )
            return None

    def get_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get extraction tool for a specific workload (cache-first, then registry)."""
        try:
            # First try cache
            cached_tool = self.get_cached_workload_tool(workload_name)
            if cached_tool:
                return cached_tool

            # If not in cache, try to download from registry
            return self.download_workload_from_registry(workload_name)
        except Exception as e:
            logger.error(f"Failed to get workload tool for '{workload_name}': {e}")
            return None

    def list_workloads(self) -> list[str]:
        """List all available workloads (cache-first, then registry)."""
        try:
            # Return cached workloads first
            cached_workloads = self.list_cached_workloads()

            # If no cached workloads, try to get from registry
            if not cached_workloads:
                registry_workloads = self.list_workloads_from_registry()
                return registry_workloads

            return cached_workloads
        except Exception as e:
            logger.error(f"Failed to list workloads: {e}")
            return []

    def execute_extraction_tool(
        self, workload_name: str, input_path: str
    ) -> dict[str, Any]:
        """Execute an extraction tool for a specific workload."""
        try:
            workload_name = workload_name.lower()
            tool_info = self.get_workload_tool(workload_name)

            if not tool_info:
                logger.error(
                    f"❌ No extraction tool found for workload: {workload_name}"
                )
                return {"error": f"No extraction tool for {workload_name}"}

            # Get script path from API and download if needed
            script_name = tool_info.get("script", "extractor.sh")
            try:
                script_path = self.script_downloader.get_script(
                    workload_name, script_name
                )
                logger.info(f"🔧 Using script: {script_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download script for {workload_name}: {e}")
                return {"error": f"Script download failed: {e}"}

            logger.info(f"🔧 Executing extraction script: {script_path}")
            # Scripts now extract all available metrics automatically
            result = subprocess.run(
                [str(script_path), input_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"✅ Data extraction successful for {workload_name}")
                return {
                    "success": True,
                    "raw_output": result.stdout.strip(),
                    "workload": workload_name,
                    "script": str(script_path),
                }
            else:
                logger.error(f"❌ Extraction script failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "workload": workload_name,
                    "script": str(script_path),
                }

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Data extraction script timed out for {workload_name}")
            return {"error": f"Script execution timed out for {workload_name}"}
        except Exception as e:
            logger.error(f"❌ Error executing data extraction script: {e}")
            return {"error": str(e)}

    def get_registry_info(self, include_registry: bool = False) -> dict[str, Any]:
        """Get registry information and statistics (cache-first, optionally include registry)."""
        try:
            # Get cache info
            cache_info = self.script_downloader.get_cache_info()
            cached_workloads = self.list_cached_workloads()

            result = {
                "total_workloads": len(cached_workloads),
                "workloads": cached_workloads,
                "scripts_directory": str(self.scripts_dir),
                "source": "Local Cache",
                "script_cache": cache_info,
            }

            # Optionally include registry info
            if include_registry:
                try:
                    api_client = self._get_api_client()
                    registry_workloads = api_client.get_all_workloads()
                    registry_workload_names = [
                        w.get("workloadName", "")
                        for w in registry_workloads
                        if w.get("workloadName")
                    ]

                    result.update(
                        {
                            "total_workloads": len(registry_workload_names),
                            "workloads": registry_workload_names,
                            "source": "Local Cache + API Registry",
                            "registry_workloads": registry_workload_names,
                            "cached_workloads": cached_workloads,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to get registry info: {e}")
                    result["registry_error"] = str(e)

            return result
        except Exception as e:
            logger.error(f"Failed to get registry info: {e}")
            return {
                "total_workloads": 0,
                "workloads": [],
                "scripts_directory": str(self.scripts_dir),
                "source": "Local Cache (Error)",
                "error": str(e),
            }

    def clear_script_cache(self, workload: str | None = None) -> None:
        """Clear script cache.

        Args:
            workload: Specific workload to clear, or None for all
        """
        self.script_downloader.clear_cache(workload)

    def add_workload(self, workload_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new workload to the registry.

        Args:
            workload_data: Dictionary containing workload information
                - workloadName: Name of the workload
                - metrics: List of metrics to extract
                - script: Script filename
                - description: Optional description
                - status: Workload status

        Returns:
            Dictionary with operation result

        Raises:
            RuntimeError: If workload creation fails
        """
        try:
            workload_name = workload_data.get("workloadName")
            if not workload_name:
                raise ValueError("workloadName is required")

            # Check if workload already exists
            api_client = self._get_api_client()
            if api_client.workload_exists(workload_name):
                raise RuntimeError(f"Workload '{workload_name}' already exists")

            # Validate required fields
            metrics = workload_data.get("metrics", [])
            if not metrics:
                raise ValueError("At least one metric is required")

            script = workload_data.get("script", "extractor.sh")

            logger.info(f"➕ Adding workload: {workload_name}")
            logger.info(f"   - Metrics: {', '.join(metrics)}")
            logger.info(f"   - Script: {script}")
            if workload_data.get("description"):
                logger.info(f"   - Description: {workload_data['description']}")

            # Create workload via API
            result = api_client.create_workload(workload_data)

            if result:
                return {
                    "success": True,
                    "message": f"Workload '{workload_name}' successfully created",
                    "workload": workload_name,
                    "data": result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create workload '{workload_name}' via API",
                }

        except Exception as e:
            error_msg = f"Failed to add workload: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def update_workload(
        self, workload_name: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing workload in the registry.

        Args:
            workload_name: Name of the workload to update
            updates: Dictionary containing fields to update
                - metrics: List of metrics to extract
                - script: Script filename
                - description: Description
                - status: Workload status

        Returns:
            Dictionary with operation result

        Raises:
            RuntimeError: If workload update fails
        """
        try:
            # Check if workload exists
            api_client = self._get_api_client()
            if not api_client.workload_exists(workload_name):
                raise RuntimeError(f"Workload '{workload_name}' not found")

            # Get current workload data to get the ID
            current_workload = api_client.get_workload_by_name(workload_name)
            if not current_workload:
                raise RuntimeError(f"Could not retrieve workload '{workload_name}'")

            workload_id = current_workload.get("workloadId")
            if not workload_id:
                raise RuntimeError(f"Workload '{workload_name}' has no ID")

            # Prepare update data
            update_data = {}
            if "workloadName" in updates:
                new_name = updates["workloadName"]
                if not new_name or not new_name.strip():
                    raise ValueError("New workload name cannot be empty")
                # Check if new name already exists
                if api_client.workload_exists(new_name.strip()):
                    raise ValueError(f"Workload with name '{new_name}' already exists")
                update_data["workloadName"] = new_name.strip()

            if "metrics" in updates:
                metrics = updates["metrics"]
                if not metrics:
                    raise ValueError("At least one metric is required")
                update_data["metrics"] = [metric.strip() for metric in metrics]

            if "script" in updates:
                update_data["script"] = updates["script"]

            if "description" in updates:
                update_data["description"] = updates["description"]

            if "status" in updates:
                update_data["status"] = updates["status"]

            if not update_data:
                return {"success": False, "error": "No updates specified"}

            # Update workload via API
            logger.info(f"🔄 Updating workload: {workload_name}")
            for field, value in update_data.items():
                logger.info(f"   - {field}: {value}")

            result = api_client.update_workload(workload_id, update_data)

            if result:
                return {
                    "success": True,
                    "message": f"Workload '{workload_name}' successfully updated",
                    "workload": workload_name,
                    "updates": update_data,
                    "data": result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update workload '{workload_name}' via API",
                }

        except Exception as e:
            error_msg = f"Failed to update workload: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_workload_details(self, workload_name: str) -> dict[str, Any] | None:
        """Get detailed information about a specific workload.

        Args:
            workload_name: Name of the workload

        Returns:
            Dictionary with workload details or None if not found
        """
        try:
            api_client = self._get_api_client()
            workload = api_client.get_workload_by_name(workload_name)
            if not workload:
                return None

            # Add cache status information
            try:
                script_name = workload.get("script", "extractor.sh")
                script_path = self.script_downloader.get_script(
                    workload_name, script_name
                )
                cache_status = "✅ Cached" if script_path.exists() else "❌ Not cached"
                script_path_str = str(script_path) if script_path.exists() else "N/A"
            except Exception:
                cache_status = "❌ Download failed"
                script_path_str = "N/A"

            workload["script_cache_status"] = cache_status
            workload["script_local_path"] = script_path_str

            return workload

        except Exception as e:
            logger.error(f"Failed to get workload details for '{workload_name}': {e}")
            return None

    def close(self) -> None:
        """Close the registry and cleanup resources."""
        if hasattr(self, "api_client"):
            self.api_client.close()
