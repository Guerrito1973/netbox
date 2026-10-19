import unittest

from module_loader import risk

assess_risk = risk.assess_risk
classify_device = risk.classify_device


class RiskTests(unittest.TestCase):
    def test_unknown_telnet_device_is_high_risk(self):
        host = {"mac": "00:11:22:33:44:55", "vendor": "Example", "services": [{"port": 23}]}
        score, reasons, recommendations = assess_risk(host, known_in_netbox=False)
        self.assertEqual(score, 65)
        self.assertTrue(any("Telnet" in reason for reason in reasons))
        self.assertTrue(any("SSH" in recommendation for recommendation in recommendations))

    def test_changed_mac_is_flagged(self):
        host = {"mac": "00:11:22:33:44:66", "vendor": "Example", "services": []}
        score, reasons, _ = assess_risk(host, known_in_netbox=True, previous_mac="00:11:22:33:44:55")
        self.assertEqual(score, 35)
        self.assertTrue(any("changed" in reason for reason in reasons))

    def test_printer_classification(self):
        self.assertEqual(classify_device({"services": [{"port": 9100}]}), "printer")


if __name__ == "__main__":
    unittest.main()
