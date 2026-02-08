import re
from datetime import date, datetime
from dataclasses import dataclass
from platform import release


@dataclass
class Phone:
    name: str
    release_date: date
    ram_capability: int

def parse(line: str):
    tokens = re.findall(r'"[^"]*"|\S+', line)

    if "Phone" in tokens:
        tokens.remove("Phone")

    name = None
    release_date = None
    ram_capability = None

    for i in tokens:
        if i.startswith('"') and i.endswith('"'):
            name = i[1:-1]
        elif re.fullmatch(r'\d{4}\.\d{2}\.\d{2}', i):
            release_date = datetime.strptime(i, "%Y.%m.%d").date()
        elif re.fullmatch(r'\d+', i):
            ram_capability = int(i)
    return Phone(name, release_date, ram_capability)

line = input()
obj = parse(line)

print(f"{obj} \nНазвание:{obj.name} \nДата выпуска:{obj.release_date} \nОбъем ОЗУ:{obj.ram_capability} Гб")
