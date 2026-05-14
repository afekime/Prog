import os
import unittest
from model import Phone, PhoneDateError, PhoneRamError, PhoneNameError
from file_manager import PhoneFileManager
from command_processor import (
    CommandParser, CommandExecutor,
    AddCommand, RemCommand, SaveCommand,
    CommandParseError, CommandExecuteError,
)


class TestPhoneModel(unittest.TestCase):

    def test_phone_create(self):
        phone = Phone("iPhone 17", "2025.02.02", 8)
        self.assertEqual(phone.name, "iPhone 17")
        self.assertEqual(phone.release_date, "2025.02.02")
        self.assertEqual(phone.ram_capability, 8)

    def test_phone_create_invalid_date(self):
        with self.assertRaises(PhoneDateError):
            Phone("iPhone 17", "20250202", 8)

    def test_phone_create_invalid_ram_float(self):
        with self.assertRaises(PhoneRamError):
            Phone("iPhone 17", "2025.02.02", 8.1)

    def test_phone_create_zero_ram(self):
        with self.assertRaises(PhoneRamError):
            Phone("iPhone 17", "2025.02.02", 0)

    def test_phone_create_negative_ram(self):
        with self.assertRaises(PhoneRamError):
            Phone("iPhone 17", "2025.02.02", -4)

    def test_phone_create_empty_name(self):
        with self.assertRaises(PhoneNameError):
            Phone("", "2025.02.02", 8)

    def test_phone_create_whitespace_name(self):
        with self.assertRaises(PhoneNameError):
            Phone("   ", "2025.02.02", 8)


class TestPhoneFileManager(unittest.TestCase):

    def setUp(self):
        self.repository = PhoneFileManager("test_phone_errors.log")

    def tearDown(self):
        for path in ("test_data.txt", "test_save.txt"):
            if os.path.exists(path):
                os.remove(path)
        self.repository.close()
        if os.path.exists("test_phone_errors.log"):
            os.remove("test_phone_errors.log")

    def test_parse_line(self):
        phone = self.repository.parse_line('"iPhone 17" 2025.02.02 8')
        self.assertEqual(phone.name, "iPhone 17")
        self.assertEqual(phone.release_date, "2025.02.02")
        self.assertEqual(phone.ram_capability, 8)

    def test_parse_line_invalid_ram(self):
        from model import PhoneRamError
        with self.assertRaises(PhoneRamError):
            self.repository.parse_line('"iPhone 17" 2025.02.02 abc')

    def test_parse_line_missing_quote(self):
        from model import PhoneNameError
        with self.assertRaises(PhoneNameError):
            self.repository.parse_line('iPhone 17 2025.02.02 8')

    def test_parse_line_wrong_field_count(self):
        from model import PhoneParseError
        with self.assertRaises(PhoneParseError):
            self.repository.parse_line('"iPhone 17" 2025.02.02')

    def test_load_from_file_skips_invalid(self):
        with open("test_data.txt", "w") as f:
            f.write('"iPhone 17" 2025.02.02 8\n')
            f.write('"xxx" 20220202 2\n')
            f.write('"iPhone 16" 2022.02.02 8\n')

        phones = self.repository.load_from_file("test_data.txt")

        self.assertEqual(len(phones), 2)
        self.assertEqual(phones[0].name, "iPhone 17")
        self.assertEqual(phones[1].name, "iPhone 16")

    def test_load_from_file_empty_lines_ignored(self):
        with open("test_data.txt", "w") as f:
            f.write('"iPhone 17" 2025.02.02 8\n')
            f.write('\n')
            f.write('"iPhone 16" 2022.02.02 8\n')

        phones = self.repository.load_from_file("test_data.txt")
        self.assertEqual(len(phones), 2)

    def test_save_to_file(self):
        phones = [
            Phone("iPhone 17", "2025.02.02", 8),
            Phone("iPhone 16", "2022.02.02", 8),
        ]
        self.repository.save_to_file("test_save.txt", phones)

        with open("test_save.txt", "r") as f:
            content = f.read()

        expected = '"iPhone 17" 2025.02.02 8\n"iPhone 16" 2022.02.02 8\n'
        self.assertEqual(content, expected)

    def test_create_phone_valid(self):
        phone = self.repository.create_phone("iPhone 17", "2025.02.02", "8")
        self.assertEqual(phone.name, "iPhone 17")
        self.assertEqual(phone.ram_capability, 8)


class TestCommandParser(unittest.TestCase):

    def setUp(self):
        self.parser = CommandParser()


    def test_parse_add_with_quotes(self):
        cmd = self.parser.parse_line('ADD "iPhone 17"; 2025.02.02; 8')
        self.assertIsInstance(cmd, AddCommand)
        self.assertEqual(cmd.name, "iPhone 17")
        self.assertEqual(cmd.release_date, "2025.02.02")
        self.assertEqual(cmd.ram_capability, 8)

    def test_parse_add_without_quotes(self):
        cmd = self.parser.parse_line('ADD iPhone 17; 2025.02.02; 8')
        self.assertIsInstance(cmd, AddCommand)
        self.assertEqual(cmd.name, "iPhone 17")

    def test_parse_add_wrong_field_count(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('ADD "iPhone 17"; 2025.02.02')

    def test_parse_add_invalid_ram(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('ADD "iPhone 17"; 2025.02.02; abc')

    def test_parse_rem_ram_lt(self):
        cmd = self.parser.parse_line('REM ram < 8')
        self.assertIsInstance(cmd, RemCommand)
        self.assertEqual(cmd.condition, "ram < 8")

    def test_parse_rem_name_eq(self):
        cmd = self.parser.parse_line('REM name == "iPhone 17"')
        self.assertIsInstance(cmd, RemCommand)

    def test_parse_rem_date_gte(self):
        cmd = self.parser.parse_line('REM date >= 2024.01.01')
        self.assertIsInstance(cmd, RemCommand)

    def test_parse_rem_invalid_operator(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('REM ram ~ 8')

    def test_parse_rem_no_condition(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('REM ')

    def test_parse_save(self):
        cmd = self.parser.parse_line('SAVE output.txt')
        self.assertIsInstance(cmd, SaveCommand)
        self.assertEqual(cmd.filename, "output.txt")

    def test_parse_save_strips_quotes(self):
        cmd = self.parser.parse_line('SAVE "my file.txt"')
        self.assertEqual(cmd.filename, "my file.txt")

    def test_parse_save_empty_filename(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('SAVE ')

    def test_parse_empty_line_returns_none(self):
        self.assertIsNone(self.parser.parse_line(''))
        self.assertIsNone(self.parser.parse_line('   '))

    def test_parse_unknown_command(self):
        with self.assertRaises(CommandParseError):
            self.parser.parse_line('DELETE all')

    def test_load_from_file_skips_bad_lines(self):
        path = "test_commands.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write('ADD "iPhone 17"; 2025.02.02; 8\n')
                f.write('BADCMD foo\n')
                f.write('REM ram > 4\n')

            commands = self.parser.load_from_file(path)
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], AddCommand)
            self.assertIsInstance(commands[1], RemCommand)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_load_from_file_ignores_empty_lines(self):
        path = "test_commands.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write('\n')
                f.write('SAVE out.txt\n')
                f.write('\n')

            commands = self.parser.load_from_file(path)
            self.assertEqual(len(commands), 1)
        finally:
            if os.path.exists(path):
                os.remove(path)

class TestCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.repository = PhoneFileManager("test_exec_errors.log")
        self.executor = CommandExecutor(self.repository)
        self.phones = [
            Phone("iPhone 17", "2025.02.02", 8),
            Phone("Samsung S24", "2024.01.17", 12),
            Phone("Pixel 9", "2024.08.14", 12),
        ]

    def tearDown(self):
        self.repository.close()
        for path in ("test_exec_errors.log", "test_exec_save.txt"):
            if os.path.exists(path):
                os.remove(path)

    def test_execute_add(self):
        cmd = AddCommand("Xiaomi 14", "2023.12.28", 16)
        result = self.executor.execute(self.phones, cmd)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[-1].name, "Xiaomi 14")

    def test_execute_add_does_not_mutate_original(self):
        original_len = len(self.phones)
        cmd = AddCommand("Xiaomi 14", "2023.12.28", 16)
        self.executor.execute(self.phones, cmd)
        self.assertEqual(len(self.phones), original_len)

    def test_execute_add_invalid_phone_raises(self):
        cmd = AddCommand("", "2025.02.02", 8)
        with self.assertRaises(CommandExecuteError):
            self.executor.execute(self.phones, cmd)

    def test_execute_rem_by_ram(self):
        cmd = RemCommand("ram == 12")
        result = self.executor.execute(self.phones, cmd)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "iPhone 17")

    def test_execute_rem_by_name_eq(self):
        cmd = RemCommand('name == "Samsung S24"')
        result = self.executor.execute(self.phones, cmd)
        self.assertEqual(len(result), 2)
        self.assertNotIn("Samsung S24", [p.name for p in result])

    def test_execute_rem_by_date_lte(self):
        cmd = RemCommand("date <= 2024.08.14")
        result = self.executor.execute(self.phones, cmd)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "iPhone 17")

    def test_execute_rem_invalid_ram_value(self):
        cmd = RemCommand("ram < abc")
        result = self.executor.execute(self.phones, cmd)
        self.assertEqual(len(result), 3)

    def test_execute_save(self):
        cmd = SaveCommand("test_exec_save.txt")
        self.executor.execute(self.phones, cmd)
        self.assertTrue(os.path.exists("test_exec_save.txt"))

    def test_execute_save_content(self):
        cmd = SaveCommand("test_exec_save.txt")
        self.executor.execute(self.phones, cmd)

        with open("test_exec_save.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3)
        self.assertIn("iPhone 17", lines[0])

    def test_execute_all_sequence(self):
        commands = [
            AddCommand("Xiaomi 14", "2023.12.28", 16),
            RemCommand("ram < 12"),
            SaveCommand("test_exec_save.txt"),
        ]
        result = self.executor.execute_all(self.phones, commands)

        self.assertEqual(len(result), 3)
        self.assertNotIn("iPhone 17", [p.name for p in result])
        self.assertTrue(os.path.exists("test_exec_save.txt"))

    def test_execute_all_empty_commands(self):
        result = self.executor.execute_all(self.phones, [])
        self.assertEqual(len(result), 3)

    def test_execute_unknown_command_raises(self):
        with self.assertRaises(CommandExecuteError):
            self.executor.execute(self.phones, object())

if __name__ == "__main__":
    unittest.main()