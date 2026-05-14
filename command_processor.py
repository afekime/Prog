import re
import logging
from dataclasses import dataclass
from model import Phone, PhoneParseError

class CommandError(Exception):
    pass

class CommandParseError(CommandError):
    pass

class CommandExecuteError(CommandError):
    pass

@dataclass
class AddCommand:
    name: str
    release_date: str
    ram_capability: int

@dataclass
class RemCommand:
    condition: str

@dataclass
class SaveCommand:
    filename: str

class CommandParser:

    CONDITION_PATTERN = re.compile(
        r'^(name|date|ram)\s*(==|!=|<=|>=|<|>)\s*(.+)$'
    )

    def parse_line(self, line: str):
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        if line.upper().startswith('ADD '):
            return self._parse_add(line[4:].strip())
        if line.upper().startswith('REM '):
            return self._parse_rem(line[4:].strip())
        if line.upper().startswith('SAVE '):
            return self._parse_save(line[5:].strip())

        raise CommandParseError(f"Неизвестная команда: «{line}»")

    def _parse_add(self, data: str) -> AddCommand:
        parts = [p.strip() for p in data.split(';')]
        if len(parts) != 3:
            raise CommandParseError(
                f"ADD ожидает 3 поля (название; дата; ОЗУ), получено {len(parts)}: «{data}»"
            )

        name = parts[0].strip('"\'')
        release_date = parts[1].strip('"\'')

        try:
            ram = int(parts[2])
        except ValueError:
            raise CommandParseError(
                f"ОЗУ должен быть целым числом, получено: «{parts[2]}»"
            )

        return AddCommand(name, release_date, ram)

    def _parse_rem(self, condition: str) -> RemCommand:
        condition = condition.strip()
        if not self.CONDITION_PATTERN.match(condition):
            raise CommandParseError(
                f"Некорректное условие REM: «{condition}». "
                "Формат: <поле> <оператор> <значение>, "
                "поля: name, date, ram; операторы: ==, !=, <, >, <=, >="
            )
        return RemCommand(condition)

    def _parse_save(self, filename: str) -> SaveCommand:
        filename = filename.strip().strip('"\'')
        if not filename:
            raise CommandParseError("SAVE требует непустое имя файла")
        return SaveCommand(filename)

    def load_from_file(self, filename: str, logger: logging.Logger = None) -> list:
        commands = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    cmd = self.parse_line(stripped)
                    if cmd is not None:
                        commands.append(cmd)
                except CommandParseError as error:
                    if logger:
                        logger.warning(
                            f'Строка {line_number} пропущена: «{stripped}». Причина: {error}'
                        )
        return commands

class CommandExecutor:

    CONDITION_PATTERN = re.compile(
        r'^(name|date|ram)\s*(==|!=|<=|>=|<|>)\s*(.+)$'
    )

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def execute(self, phones: list, command) -> list:
        if isinstance(command, AddCommand):
            return self._execute_add(phones, command)
        if isinstance(command, RemCommand):
            return self._execute_rem(phones, command)
        if isinstance(command, SaveCommand):
            self._execute_save(phones, command)
            return phones
        raise CommandExecuteError(f"Неизвестный тип команды: {type(command)}")

    def execute_all(self, phones: list, commands: list) -> list:
        for cmd in commands:
            phones = self.execute(phones, cmd)
        return phones

    def _execute_add(self, phones: list, cmd: AddCommand) -> list:
        try:
            phone = Phone(cmd.name, cmd.release_date, cmd.ram_capability)
        except PhoneParseError as error:
            raise CommandExecuteError(f"Ошибка ADD: {error}") from error
        return phones + [phone]

    def _execute_rem(self, phones: list, cmd: RemCommand) -> list:
        return [p for p in phones if not self._matches(p, cmd.condition)]

    def _execute_save(self, phones: list, cmd: SaveCommand):
        self.file_manager.save_to_file(cmd.filename, phones)

    def _matches(self, phone: Phone, condition: str) -> bool:
        match = self.CONDITION_PATTERN.match(condition)
        if not match:
            return False

        field, op, raw_value = match.group(1), match.group(2), match.group(3).strip()

        if field == 'name':
            phone_val = phone.name
            cmp_val = raw_value.strip('"\'')
        elif field == 'date':
            phone_val = phone.release_date
            cmp_val = raw_value.strip('"\'')
        elif field == 'ram':
            phone_val = phone.ram_capability
            try:
                cmp_val = int(raw_value)
            except ValueError:
                return False
        else:
            return False

        return self._compare(phone_val, op, cmp_val)

    @staticmethod
    def _compare(a, op: str, b) -> bool:
        ops = {
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '<':  lambda x, y: x < y,
            '>':  lambda x, y: x > y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
        }
        fn = ops.get(op)
        return fn(a, b) if fn else False