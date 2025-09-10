# PyAttackForge

A lightweight Python library for interacting with the AttackForge API.

---

## Features

- Create and fetch projects
- Manage assets
- Submit vulnerabilities
- Dry-run mode for testing

---

## Install

   ```bash
   mkdir PyAttackForgeEnv
   cd PyAttackForgeEnv
   virtualenv venv
   source ./venv/bin/activate
   pip install git+https://github.com/Tantalum-Labs/PyAttackForge.git
   ```

## Use

   ```python
   from pyattackforge import PyAttackForgeClient

   # Initialize client - Note: Make sure to set your AttackForge URL and API Key
   client = PyAttackForgeClient(api_key="your-api-key", base_url="https://demo.attackforge.com", dry_run=False)

   # Create a project
   project = client.create_project("My Project", scope=["Asset1", "Asset2"])

   ## Create a vulnerability with auto-created assets
   client.create_vulnerability(
       vulnerability_data={
           "projectId": "abc123",
           "title": "Open SSH Port",
           "affected_assets": [{"assetName": "ssh-prod-1"}],
           "priority": "High",
           "likelihood_of_exploitation": 10,
       },
       auto_create_assets=True,
       default_asset_type="Cloud",
       default_asset_library_ids=["your-lib-id"]
   )

   ```

---

## API Reference

### `PyAttackForgeClient`

- `__init__(api_key: str, base_url: str = ..., dry_run: bool = False)`
- `get_assets() -> dict`
- `get_asset_by_name(name: str) -> dict or None`
- `create_asset(asset_data: dict) -> dict`
- `get_project_by_name(name: str) -> dict or None`
- `get_project_scope(project_id: str) -> set`
- `update_project_scope(project_id: str, new_assets: list) -> dict`
- `create_project(name: str, **kwargs) -> dict`
- `update_project(project_id: str, update_fields: dict) -> dict`
- `create_vulnerability(vulnerability_data: dict, auto_create_assets: bool = False, ...) -> dict`

See the source code for full details and docstrings.

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests via GitHub.

- Ensure code is PEP8-compliant and includes docstrings and type hints.
- Add or update tests for new features or bugfixes.
- Do **not** commit API keys or other secrets.

---

## Security

**Never commit your API keys or other sensitive information to version control.**

---

## License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html).
