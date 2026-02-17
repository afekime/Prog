import re
from datetime import date, datetime
from dataclasses import dataclass
from platform import release

@dataclass
class Phone:
    name: object
    release_date: object
    ram_capability: object

def build_obj(line: str):
    first_sim = line.find('"')
    last_sim = line.find('"', first_sim+1)

    line_rest = line[last_sim+1:].split()

    name = line[first_sim + 1:last_sim]
    release_date = line_rest[0]
    ram_capability = line_rest[1]

    return Phone(name, release_date, ram_capability)

line = input()
obj = build_obj(line)
print(obj)