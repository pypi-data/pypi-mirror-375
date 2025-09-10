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

   ## Create a security finding (vulnerability)
   client.create_vulnerability(
       project_id="abc123",
       title="Open SSH Port",
       affected_asset_name="ssh-prod-1",
       priority="High",
       likelihood_of_exploitation=10,
       description="SSH port 22 is open to the internet.",
       attack_scenario="An attacker can brute-force SSH credentials.",
       remediation_recommendation="Restrict SSH access to trusted IPs.",
       steps_to_reproduce="1. Scan the host\n2. Observe port 22 is open",
       tags=["ssh", "exposure"],
       notes=["Observed on 2025-09-09"],
       is_zeroday=False,
       is_visible=True
   )

   ```

---

## Creating Security Findings

To create a security finding (vulnerability) in AttackForge, use the `create_vulnerability` method:

```python
client.create_vulnerability(
    project_id="abc123",
    title="Open SSH Port",
    affected_asset_name="ssh-prod-1",
    priority="High",
    likelihood_of_exploitation=10,
    description="SSH port 22 is open to the internet.",
    attack_scenario="An attacker can brute-force SSH credentials.",
    remediation_recommendation="Restrict SSH access to trusted IPs.",
    steps_to_reproduce="1. Scan the host\n2. Observe port 22 is open",
    tags=["ssh", "exposure"],
    notes=["Observed on 2025-09-09"],
    is_zeroday=False,
    is_visible=True
)
```

**Parameters:**
- `project_id` (str): The project ID.
- `title` (str): The title of the finding.
- `affected_asset_name` (str): The name of the affected asset.
- `priority` (str): The priority (e.g., "Critical", "High", "Medium", "Low").
- `likelihood_of_exploitation` (int): Likelihood of exploitation (e.g., 10).
- `description` (str): Description of the finding.
- `attack_scenario` (str): Attack scenario details.
- `remediation_recommendation` (str): Remediation recommendation.
- `steps_to_reproduce` (str): Steps to reproduce the finding.
- `tags` (list, optional): List of tags.
- `notes` (list, optional): List of notes.
- `is_zeroday` (bool, optional): Whether this is a zero-day finding.
- `is_visible` (bool, optional): Whether the finding is visible.
- `import_to_library` (str, optional): Library to import to.
- `import_source` (str, optional): Source of import.
- `import_source_id` (str, optional): Source ID for import.
- `custom_fields` (list, optional): List of custom fields.
- `linked_testcases` (list, optional): List of linked testcases.
- `custom_tags` (list, optional): List of custom tags.

See the source code for full details and docstrings.

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
- `create_vulnerability(
      project_id: str,
      title: str,
      affected_asset_name: str,
      priority: str,
      likelihood_of_exploitation: int,
      description: str,
      attack_scenario: str,
      remediation_recommendation: str,
      steps_to_reproduce: str,
      tags: Optional[list] = None,
      notes: Optional[list] = None,
      is_zeroday: bool = False,
      is_visible: bool = True,
      import_to_library: Optional[str] = None,
      import_source: Optional[str] = None,
      import_source_id: Optional[str] = None,
      custom_fields: Optional[list] = None,
      linked_testcases: Optional[list] = None,
      custom_tags: Optional[list] = None,
  ) -> dict`

See the source code for full details and docstrings.

---
- `create_vulnerability(
      project_id: str,
      title: str,
      affected_asset_name: str,
      priority: str,
      likelihood_of_exploitation: int,
      description: str,
      attack_scenario: str,
      remediation_recommendation: str,
      steps_to_reproduce: str,
      tags: Optional[list] = None,
      notes: Optional[list] = None,
      is_zeroday: bool = False,
      is_visible: bool = True,
      import_to_library: Optional[str] = None,
      import_source: Optional[str] = None,
      import_source_id: Optional[str] = None,
      custom_fields: Optional[list] = None,
      linked_testcases: Optional[list] = None,
      custom_tags: Optional[list] = None,
  ) -> dict`

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
