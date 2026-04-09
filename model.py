from dataclasses import dataclass
from datetime import datetime


class PhoneError(Exception):
    pass


class PhoneParseError(PhoneError):
    pass


class PhoneDateError(PhoneParseError):
    pass


class PhoneRamError(PhoneParseError):
    pass


class PhoneNameError(PhoneParseError):
    pass


@dataclass
class Phone:
    name: str
    release_date: str
    ram_capability: int

    def __post_init__(self):
        if not self.name.strip():
            raise PhoneNameError("Название телефона не может быть пустым")

        try:
            datetime.strptime(self.release_date, "%Y.%m.%d")
        except ValueError:
            raise PhoneDateError(
                "Дата должна быть в формате гггг.мм.дд"
            )

        if not isinstance(self.ram_capability, int):
            raise PhoneRamError("Объем ОЗУ должен быть целым числом")

        if self.ram_capability <= 0:
            raise PhoneRamError("Объем ОЗУ должен быть больше нуля")