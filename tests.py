import os
import unittest
from model import Phone, PhoneDateError, PhoneRamError, PhoneNameError
from file_manager import PhoneFileManager


class TestPhoneModel(unittest.TestCase):
    def setUp(self):
        self.repository = PhoneFileManager("test_phone_errors.log")

    def tearDown(self):
        if os.path.exists("test_data.txt"):
            os.remove("test_data.txt")

        if os.path.exists("test_save.txt"):
            os.remove("test_save.txt")

        self.repository.close()
        if os.path.exists("test_phone_errors.log"):
            os.remove("test_phone_errors.log")

    def test_parse_line(self):
        line = '"iPhone 17" 2025.02.02 8'
        phone = self.repository.parse_line(line)

        self.assertEqual(phone.name, "iPhone 17")
        self.assertEqual(phone.release_date, "2025.02.02")
        self.assertEqual(phone.ram_capability, 8)

    def test_phone_create(self):
        phone = Phone("iPhone 17", "2025.02.02", 8)
        self.assertEqual(phone.name, "iPhone 17")
        self.assertEqual(phone.release_date, "2025.02.02")
        self.assertEqual(phone.ram_capability, 8)

    def test_phone_create_invalid_date(self):
        with self.assertRaises(PhoneDateError):
            Phone("iPhone 17", "20250202", 8)

    def test_phone_create_invalid_ram(self):
        with self.assertRaises(PhoneRamError):
            Phone("iPhone 17", "2025.02.02", 8.1)

    def test_phone_create_empty_name(self):
        with self.assertRaises(PhoneNameError):
            Phone("", "2025.02.02", 8)

    def test_load_from_file(self):
        with open("test_data.txt", "w") as file:
            file.write('"iPhone 17" 2025.02.02 8\n')
            file.write('"xxx" 20220202 2\n')
            file.write('"iPhone 16" 2022.02.02 8\n')

        phones = self.repository.load_from_file("test_data.txt")

        self.assertEqual(phones[0].name, "iPhone 17")
        self.assertEqual(phones[1].name, "iPhone 16")

    def test_save_to_file(self):
        phones = [
            Phone("iPhone 17", "2025.02.02", 8),
            Phone("iPhone 16", "2022.02.02", 8)
        ]

        self.repository.save_to_file("test_save.txt", phones)

        with open("test_save.txt", "r") as file:
            content = file.read()

        expected = (
            '"iPhone 17" 2025.02.02 8\n'
            '"iPhone 16" 2022.02.02 8\n'
        )

        self.assertEqual(content, expected)


if __name__ == "__main__":
    unittest.main()
