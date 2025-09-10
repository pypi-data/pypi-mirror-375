"""
PyAttackForge is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyAttackForge is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import requests
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Set, Tuple, List


logger = logging.getLogger("pyattackforge")

class PyAttackForgeClient:
    """
    Python client for interacting with the AttackForge API.

    Provides methods to manage assets, projects, and vulnerabilities.
    Supports dry-run mode for testing without making real API calls.
    """

    def __init__(self, api_key: str, base_url: str = "https://demo.attackforge.com", dry_run: bool = False):
        """
        Initialize the PyAttackForgeClient.

        Args:
            api_key (str): Your AttackForge API key.
            base_url (str, optional): The base URL for the AttackForge instance. Defaults to "https://demo.attackforge.com".
            dry_run (bool, optional): If True, no real API calls are made. Defaults to False.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-SSAPI-KEY": api_key,
            "Content-Type": "application/json",
            "Connection": "close"
        }
        self.dry_run = dry_run
        self._asset_cache = None
        self._project_scope_cache = {}  # {project_id: set(asset_names)}

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Internal method to send an HTTP request to the AttackForge API.

        Args:
            method (str): HTTP method (get, post, put, etc.).
            endpoint (str): API endpoint path.
            json_data (dict, optional): JSON payload for the request.
            params (dict, optional): Query parameters.

        Returns:
            Response: The HTTP response object.
        """
        url = f"{self.base_url}{endpoint}"
        if self.dry_run:
            logger.info("[DRY RUN] %s %s", method.upper(), url)
            if json_data:
                logger.info("Payload: %s", json_data)
            if params:
                logger.info("Params: %s", params)
            return DummyResponse()
        return requests.request(method, url, headers=self.headers, json=json_data, params=params)

    def get_assets(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all assets from AttackForge.

        Returns:
            dict: Mapping of asset names to asset details.
        """
        if self._asset_cache is None:
            self._asset_cache = {}
            skip, limit = 0, 500
            while True:
                resp = self._request("get", "/api/ss/assets", params={"skip": skip, "limit": limit})
                data = resp.json()
                for asset in data.get("assets", []):
                    name = asset.get("asset")
                    if name:
                        self._asset_cache[name] = asset
                if skip + limit >= data.get("count", 0):
                    break
                skip += limit
        return self._asset_cache

    def get_asset_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an asset by its name.

        Args:
            name (str): The asset name.

        Returns:
            dict or None: Asset details if found, else None.
        """
        return self.get_assets().get(name)

    def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new asset in AttackForge.

        Args:
            asset_data (dict): Asset details.

        Returns:
            dict: Created asset details.

        Raises:
            RuntimeError: If asset creation fails.
        """
        resp = self._request("post", "/api/ss/library/asset", json_data=asset_data)
        if resp.status_code == 201:
            asset = resp.json()
            self._asset_cache = None  # Invalidate cache
            return asset
        if "Asset Already Exists" in resp.text:
            return self.get_asset_by_name(asset_data["name"])
        raise RuntimeError(f"Asset creation failed: {resp.text}")

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a project by its name.

        Args:
            name (str): The project name.

        Returns:
            dict or None: Project details if found, else None.
        """
        params = {
            "startDate": "2000-01-01T00:00:00.000Z",
            "endDate": "2100-01-01T00:00:00.000Z",
            "status": "All"
        }
        resp = self._request("get", "/api/ss/projects", params=params)
        for proj in resp.json().get("projects", []):
            if proj.get("project_name") == name:
                return proj
        return None

    def get_project_scope(self, project_id: str) -> Set[str]:
        """
        Retrieve the scope (assets) of a project.

        Args:
            project_id (str): The project ID.

        Returns:
            set: Set of asset names in the project scope.

        Raises:
            RuntimeError: If project retrieval fails.
        """
        if project_id in self._project_scope_cache:
            return self._project_scope_cache[project_id]

        resp = self._request("get", f"/api/ss/project/{project_id}")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to retrieve project: {resp.text}")

        scope = set(resp.json().get("scope", []))
        self._project_scope_cache[project_id] = scope
        return scope

    def update_project_scope(self, project_id: str, new_assets: List[str]) -> Dict[str, Any]:
        """
        Update the scope (assets) of a project.

        Args:
            project_id (str): The project ID.
            new_assets (iterable): Asset names to add to the scope.

        Returns:
            dict: Updated project details.

        Raises:
            RuntimeError: If update fails.
        """
        current_scope = self.get_project_scope(project_id)
        updated_scope = list(current_scope.union(new_assets))
        resp = self._request("put", f"/api/ss/project/{project_id}", json_data={"scope": updated_scope})
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to update project scope: {resp.text}")
        self._project_scope_cache[project_id] = set(updated_scope)
        return resp.json()

    def create_project(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new project in AttackForge.

        Args:
            name (str): Project name.
            **kwargs: Additional project fields.

        Returns:
            dict: Created project details.

        Raises:
            RuntimeError: If project creation fails.
        """
        start, end = get_default_dates()
        payload = {
            "name": name,
            "code": kwargs.get("code", "DEFAULT"),
            "groups": kwargs.get("groups", []),
            "startDate": kwargs.get("startDate", start),
            "endDate": kwargs.get("endDate", end),
            "scope": kwargs.get("scope", []),
            "testsuites": kwargs.get("testsuites", []),
            "organization_code": kwargs.get("organization_code", "ORG_DEFAULT"),
            "vulnerability_code": kwargs.get("vulnerability_code", "VULN_"),
            "scoringSystem": kwargs.get("scoringSystem", "CVSSv3.1"),
            "team_notifications": kwargs.get("team_notifications", []),
            "admin_notifications": kwargs.get("admin_notifications", []),
            "custom_fields": kwargs.get("custom_fields", []),
            "asset_library_ids": kwargs.get("asset_library_ids", []),
            "sla_activation": kwargs.get("sla_activation", "automatic")
        }
        resp = self._request("post", "/api/ss/project", json_data=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(f"Project creation failed: {resp.text}")

    def update_project(self, project_id: str, update_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing project.

        Args:
            project_id (str): The project ID.
            update_fields (dict): Fields to update.

        Returns:
            dict: Updated project details.

        Raises:
            RuntimeError: If update fails.
        """
        resp = self._request("put", f"/api/ss/project/{project_id}", json_data=update_fields)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(f"Project update failed: {resp.text}")

    def create_vulnerability(
        self,
        vulnerability_data: Dict[str, Any],
        auto_create_assets: bool = False,
        default_asset_type: str = "Placeholder",
        default_asset_library_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new vulnerability in AttackForge.

        Args:
            vulnerability_data (dict): Vulnerability details (must include 'projectId').
            auto_create_assets (bool, optional): If True, create missing assets automatically.
            default_asset_type (str, optional): Asset type for auto-created assets.
            default_asset_library_ids (list, optional): Library IDs for auto-created assets.

        Returns:
            dict: Created vulnerability details.

        Raises:
            ValueError: If 'projectId' is missing.
            RuntimeError: If vulnerability creation fails.
        """
        affected_assets = vulnerability_data.get("affected_assets", [])
        project_id = vulnerability_data.get("projectId")
        if not project_id:
            raise ValueError("vulnerability_data must include 'projectId'")

        new_asset_names = []

        if auto_create_assets:
            for asset_ref in affected_assets:
                asset_name = asset_ref.get("assetName")
                if not asset_name:
                    continue
                if not self.get_asset_by_name(asset_name):
                    logger.info("Asset '%s' not found. Creating it.", asset_name)
                    asset_payload = {
                        "name": asset_name,
                        "type": default_asset_type,
                        "external_id": asset_name,
                        "details": "Auto-created by PyAttackForge",
                        "groups": [],
                        "custom_fields": [],
                    }
                    if default_asset_library_ids:
                        asset_payload["asset_library_ids"] = default_asset_library_ids
                    self.create_asset(asset_payload)
                    new_asset_names.append(asset_name)

        if new_asset_names:
            logger.info("Adding %d new assets to project '%s' scope.", len(new_asset_names), project_id)
            self.update_project_scope(project_id, new_asset_names)

        resp = self._request("post", "/api/ss/vulnerability", json_data=vulnerability_data)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(f"Vulnerability creation failed: {resp.text}")


class DummyResponse:
    """
    Dummy response object for dry-run mode.
    """
    def __init__(self) -> None:
        self.status_code = 200

    def json(self) -> Dict[str, Any]:
        return {}


def get_default_dates() -> Tuple[str, str]:
    """
    Get default start and end dates for a project (now and 30 days from now, in ISO format).

    Returns:
        tuple: (start_date, end_date) as ISO 8601 strings.
    """
    now = datetime.now(timezone.utc)
    start = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    end = (now + timedelta(days=30)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return start, end
