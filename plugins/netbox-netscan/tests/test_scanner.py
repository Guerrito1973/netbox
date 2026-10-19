import unittest

from module_loader import scanner

NmapScanner = scanner.NmapScanner
ScanError = scanner.ScanError


class ScannerSafetyTests(unittest.TestCase):
    def test_accepts_private_24(self):
        scanner = NmapScanner()
        self.assertEqual(scanner.validate_target("192.168.100.0/24"), "192.168.100.0/24")

    def test_rejects_non_network_address(self):
        with self.assertRaises(ValueError):
            NmapScanner().validate_target("192.168.100.12/24")

    def test_rejects_range_larger_than_configured(self):
        with self.assertRaises(ScanError):
            NmapScanner().validate_target("192.168.0.0/16")

    def test_rejects_public_target(self):
        with self.assertRaises(ScanError):
            NmapScanner().validate_target("8.8.8.0/24")


if __name__ == "__main__":
    unittest.main()
