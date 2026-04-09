import logging
from model import Phone, PhoneParseError, PhoneDateError, PhoneRamError, PhoneNameError


class PhoneFileManager:
    def __init__(self, log_filename: str = "phone_errors.log"):
        self.logger = logging.getLogger("phone_repository")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_filename, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def parse_line(self, line: str) -> Phone:
        line = line.strip()

        first_quote = line.find('"')
        if first_quote == -1:
            raise PhoneNameError("Не найдена открывающая кавычка")

        second_quote = line.find('"', first_quote + 1)
        if second_quote == -1:
            raise PhoneNameError("Не найдена закрывающая кавычка")

        name = line[first_quote + 1:second_quote]
        rest = line[second_quote + 1:].split()

        if len(rest) != 2:
            raise PhoneParseError(
                "После названия должны быть указаны дата и объем ОЗУ"
            )

        release_date = rest[0]

        try:
            ram_capability = int(rest[1])
        except ValueError:
            raise PhoneRamError("Объем ОЗУ должен быть целым числом")

        return Phone(name, release_date, ram_capability)

    def load_from_file(self, filename: str) -> list[Phone]:
        phones = []

        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                stripped_line = line.strip()

                if not stripped_line:
                    continue

                try:
                    phone = self.parse_line(stripped_line)
                    phones.append(phone)
                except PhoneParseError as error:
                    self.logger.info(
                        f'Строка {line_number} пропущена: "{stripped_line}". Причина: {error}'
                    )

        return phones

    def close(self):
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

    def save_to_file(self, filename: str, phones: list[Phone]):
        with open(filename, "w", encoding="utf-8") as file:
            for phone in phones:
                file.write(
                    f'"{phone.name}" {phone.release_date} {phone.ram_capability}\n'
                )

    def create_phone(self, name: str, release_date: str, ram_capability: str) -> Phone:
        name = name.strip()
        release_date = release_date.strip()
        ram_capability = ram_capability.strip()

        try:
            ram_value = int(ram_capability)
        except ValueError:
            raise PhoneRamError("Объем ОЗУ должен быть целым числом")

        return Phone(name, release_date, ram_value)