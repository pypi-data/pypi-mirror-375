import unittest
from pyattackforge import PyAttackForgeClient

class TestPyAttackForgeClient(unittest.TestCase):
    def setUp(self):
        # Use dummy values for dry-run mode
        self.client = PyAttackForgeClient(api_key="dummy", dry_run=True)

    def test_get_assets_dry_run(self):
        assets = self.client.get_assets()
        self.assertIsInstance(assets, dict)

    def test_create_asset_dry_run(self):
        asset = self.client.create_asset({"name": "TestAsset"})
        self.assertIsInstance(asset, dict)

    def test_get_project_by_name_dry_run(self):
        project = self.client.get_project_by_name("TestProject")
        self.assertIsNone(project)

    def test_create_project_dry_run(self):
        project = self.client.create_project("TestProject")
        self.assertIsInstance(project, dict)

    def test_create_vulnerability_dry_run(self):
        vuln = self.client.create_vulnerability(
            vulnerability_data={
                "projectId": "dummy",
                "title": "Test Vuln",
                "affected_assets": [{"assetName": "TestAsset"}],
            },
            auto_create_assets=True
        )
        self.assertIsInstance(vuln, dict)

if __name__ == "__main__":
    unittest.main()
