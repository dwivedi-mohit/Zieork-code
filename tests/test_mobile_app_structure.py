"""Automated test suite verifying the native Expo mobile app structure and Grok UI components."""
import os
import sys
import json
import unittest

class TestMobileAppStructure(unittest.TestCase):
    """Test suite verifying Expo Go mobile app configuration and components."""

    def test_mobile_package_json(self):
        """Verify mobile/package.json exists and contains required libraries."""
        pkg_path = "mobile/package.json"
        self.assertTrue(os.path.exists(pkg_path), "mobile/package.json must exist")
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        deps = data.get("dependencies", {})
        self.assertIn("expo", deps)
        self.assertIn("react-native", deps)
        self.assertIn("expo-linear-gradient", deps)
        self.assertIn("expo-haptics", deps)
        self.assertIn("expo-clipboard", deps)
        self.assertIn("@expo/vector-icons", deps)

    def test_mobile_app_json(self):
        """Verify mobile/app.json contains dark theme and Expo config."""
        app_json_path = "mobile/app.json"
        self.assertTrue(os.path.exists(app_json_path), "mobile/app.json must exist")
        with open(app_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        expo = data.get("expo", {})
        self.assertEqual(expo.get("userInterfaceStyle"), "dark")
        self.assertEqual(expo.get("orientation"), "portrait")
        self.assertIn("com.mohitdwivedi.zieork", expo.get("ios", {}).get("bundleIdentifier", ""))

    def test_grok_components_exist(self):
        """Verify all Grok UI components and screens exist."""
        required_files = [
            "mobile/App.js",
            "mobile/src/theme/colors.js",
            "mobile/src/services/api.js",
            "mobile/src/components/CodeBlock.js",
            "mobile/src/components/Header.js",
            "mobile/src/components/FloatingInput.js",
            "mobile/src/components/MessageItem.js",
            "mobile/src/components/TabBar.js",
            "mobile/src/screens/ChatScreen.js",
            "mobile/src/screens/ExploreScreen.js",
            "mobile/src/screens/HistoryScreen.js",
            "mobile/src/screens/SettingsScreen.js"
        ]
        for fpath in required_files:
            self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")

    def test_mohit_dwivedi_attribution_in_mobile(self):
        """Verify Mohit Dwivedi attribution is present across mobile app screens."""
        with open("mobile/src/screens/SettingsScreen.js", "r", encoding="utf-8") as f:
            settings_code = f.read()
        self.assertIn("Mohit Dwivedi", settings_code)
        self.assertIn("mohitdwivedi.in", settings_code)
        self.assertIn("hackORtech", settings_code)

        with open("mobile/src/screens/ExploreScreen.js", "r", encoding="utf-8") as f:
            explore_code = f.read()
        self.assertIn("Mohit Dwivedi", explore_code)
        self.assertIn("hackORtech", explore_code)

    def test_codeblock_1_tap_copy(self):
        """Verify CodeBlock implements Clipboard and Haptics."""
        with open("mobile/src/components/CodeBlock.js", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("expo-clipboard", code)
        self.assertIn("expo-haptics", code)
        self.assertIn("handleCopy", code)

if __name__ == "__main__":
    unittest.main()
