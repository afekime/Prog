from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame
import os

@dataclass
class Phone:
    name: object
    release_date: object
    ram_capability: object

def build_obj(line: str):
    first_sim = line.find('"')
    last_sim = line.find('"', first_sim + 1)

    line_rest = line[last_sim + 1:].split()

    name = line[first_sim + 1:last_sim]
    release_date = line_rest[0]
    ram_capability = line_rest[1]

    return Phone(name, release_date, ram_capability)

def read_obj_from_file(filename: str):
    objects = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                objects.append(build_obj(line))
    return objects

def create_gui(objects: list[Phone], filename: str):
    root = tk.Tk()
    root.title("Список телефонов")
    root.geometry("500x450+500+200")
    root.resizable(False, False)

    tk.Label(root, text="Список объектов:").pack()

    table = ttk.Treeview(
        root,
        columns=("name", "release_date", "ram_capability"),
        show="headings",
        height=8,
    )
    table.heading("name", text="Название")
    table.heading("release_date", text="Дата выхода")
    table.heading("ram_capability", text="ОЗУ")

    table.column("name", width=220, anchor="center")
    table.column("release_date", width=120, anchor="center")
    table.column("ram_capability", width=80, anchor="center")

    table.pack(pady=5)

    for obj in objects:
        table.insert("", tk.END, values=(obj.name, obj.release_date, obj.ram_capability))

    tk.Label(root, text="Введите название:").pack()
    name_entry = tk.Entry(root, width=40)
    name_entry.pack()

    tk.Label(root, text="Введите дату выхода:").pack()
    date_entry = tk.Entry(root, width=40)
    date_entry.pack()

    tk.Label(root, text="Введите объем ОЗУ:").pack()
    ram_entry = tk.Entry(root, width=40)
    ram_entry.pack()

    def save_obj_to_file():
        with open(filename, "w", encoding="utf-8") as file:
            for obj in objects:
                file.write(f'"{obj.name}" {obj.release_date} {obj.ram_capability}\n')

    def add_obj():
        obj = Phone(
            name_entry.get(),
            date_entry.get(),
            int(ram_entry.get()),
        )

        objects.append(obj)
        table.insert("", tk.END, values=(obj.name, obj.release_date, obj.ram_capability))
        save_obj_to_file()

        name_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        ram_entry.delete(0, tk.END)

    def delete_obj():
        selected = table.selection()
        if not selected:
            return

        item = selected[0]
        index = table.index(item)

        table.delete(item)
        del objects[index]
        save_obj_to_file()

    def open_help():
        help_window = tk.Toplevel(root)
        help_window.title("Справка")
        help_window.geometry("500x350+900+300")
        help_window.resizable(False, False)

        html_window = HtmlFrame(help_window)
        html_window.pack(fill="both", expand=True)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        help_path = os.path.join(base_dir, "help.html")
        html_window.load_file(help_path)

        button_frame = tk.Frame(help_window)
        button_frame.pack(fill="x", pady=5)

        tk.Button(
            button_frame,
            text="Закрыть",
            command=help_window.destroy
        ).pack(side="right", padx=10)


    tk.Button(root, text="Добавить объект", command=add_obj).pack(pady=5)
    tk.Button(root, text="Удалить выделенный объект", command=delete_obj).pack(pady=5)
    tk.Button(root, text="Справка", command=open_help).pack(pady=5)

    root.mainloop()

FileName = "Lab2.txt"
objects = read_obj_from_file(FileName)
create_gui(objects, FileName)