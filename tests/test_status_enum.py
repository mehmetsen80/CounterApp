import unittest
from enums.status_enum import StatusEnum

class StatusEnumTestCase(unittest.TestCase):
    def test_enum_values(self):
        """Test that all enum values are correctly defined"""
        self.assertEqual(StatusEnum.SUCCESS.value, "success")
        self.assertEqual(StatusEnum.INCREMENTED.value, "incremented")
        self.assertEqual(StatusEnum.RESET.value, "reset")
        self.assertEqual(StatusEnum.ERROR.value, "error")
        self.assertEqual(StatusEnum.NOT_FOUND.value, "not_found")
        self.assertEqual(StatusEnum.BAD_REQUEST.value, "bad_request")

    def test_enum_names(self):
        """Test that enum names are correctly defined"""
        self.assertEqual(StatusEnum.SUCCESS.name, "SUCCESS")
        self.assertEqual(StatusEnum.INCREMENTED.name, "INCREMENTED")
        self.assertEqual(StatusEnum.RESET.name, "RESET")
        self.assertEqual(StatusEnum.ERROR.name, "ERROR")
        self.assertEqual(StatusEnum.NOT_FOUND.name, "NOT_FOUND")
        self.assertEqual(StatusEnum.BAD_REQUEST.name, "BAD_REQUEST")

    def test_enum_membership(self):
        """Test that enum values are unique and complete"""
        values = [status.value for status in StatusEnum]
        expected_values = ["success", "incremented", "reset", "error", "not_found", "bad_request"]
        
        self.assertEqual(len(values), len(expected_values))
        for expected_value in expected_values:
            self.assertIn(expected_value, values)

if __name__ == '__main__':
    unittest.main() 