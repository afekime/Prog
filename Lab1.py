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

stroka="1+223456*+2+1*3345678+"

def arifm(s):
    best_start = 0
    best_end = 0
    for startSub in range(len(s)):
        if s[startSub] < '0' or s[startSub] > '9':
            continue

        endSub = startSub+1
        while endSub < len(s)-1:
            if (s[endSub] < '0' or s[endSub] > '9') and (s[endSub+1] < '0' or s[endSub+1] > '9'):
                break
            endSub+=1

        cur_start = startSub
        cur_end = endSub

        if cur_end - cur_start > best_end - best_start:
            best_start = cur_start
            best_end = cur_end

        best_s = s[best_start:best_end]
    return best_s

print(arifm(stroka))


line = input()
obj = build_obj(line)
print(obj)