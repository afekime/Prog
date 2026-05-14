import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from model import PhoneParseError
from file_manager import PhoneFileManager
from command_processor import CommandParser, CommandExecutor, CommandError


class PhoneApp:
    def __init__(self, objects: list, filename: str, repository: PhoneFileManager):
        self.objects = objects
        self.filename = filename
        self.repository = repository
        self.command_parser = CommandParser()
        self.command_executor = CommandExecutor(repository)

        self.root = tk.Tk()
        self.root.title("Список телефонов")
        self.root.geometry("500x500+500+200")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Список объектов:").pack()

        self.table = ttk.Treeview(
            self.root,
            columns=("name", "release_date", "ram_capability"),
            show="headings",
            height=8
        )
        self.table.heading("name", text="Название")
        self.table.heading("release_date", text="Дата выхода")
        self.table.heading("ram_capability", text="ОЗУ")

        self.table.column("name", width=220, anchor="center")
        self.table.column("release_date", width=120, anchor="center")
        self.table.column("ram_capability", width=80, anchor="center")

        self.table.pack(pady=5)

        self._refresh_table()

        tk.Label(self.root, text="Введите название:").pack()
        self.name_entry = tk.Entry(self.root, width=40)
        self.name_entry.pack()

        tk.Label(self.root, text="Введите дату выхода (гггг.мм.дд):").pack()
        self.date_entry = tk.Entry(self.root, width=40)
        self.date_entry.pack()

        tk.Label(self.root, text="Введите объем ОЗУ:").pack()
        self.ram_entry = tk.Entry(self.root, width=40)
        self.ram_entry.pack()

        tk.Button(self.root, text="Добавить объект",
                  command=self.add_obj).pack(pady=5)
        tk.Button(self.root, text="Удалить выделенный объект",
                  command=self.delete_obj).pack(pady=2)
        tk.Button(self.root, text="Загрузить файл команд",
                  command=self.load_commands).pack(pady=5)

    def add_obj(self):
        try:
            obj = self.repository.create_phone(
                self.name_entry.get(),
                self.date_entry.get(),
                self.ram_entry.get()
            )
        except PhoneParseError as error:
            messagebox.showerror("Ошибка", str(error))
            return

        self.objects.append(obj)
        self.table.insert(
            "", tk.END,
            values=(obj.name, obj.release_date, obj.ram_capability)
        )
        self.repository.save_to_file(self.filename, self.objects)

        self.name_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.ram_entry.delete(0, tk.END)

    def delete_obj(self):
        selected = self.table.selection()
        if not selected:
            return

        item = selected[0]
        index = self.table.index(item)

        self.table.delete(item)
        del self.objects[index]
        self.repository.save_to_file(self.filename, self.objects)

    def load_commands(self):
        cmd_filename = filedialog.askopenfilename(
            title="Выберите файл команд",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not cmd_filename:
            return

        try:
            commands = self.command_parser.load_from_file(
                cmd_filename, self.repository.logger
            )
            self.objects = self.command_executor.execute_all(self.objects, commands)
            self._refresh_table()
        except (CommandError, PhoneParseError, OSError) as error:
            messagebox.showerror("Ошибка при выполнении команд", str(error))

    def _refresh_table(self):
        """Перерисовывает таблицу из self.objects."""
        for item in self.table.get_children():
            self.table.delete(item)
        for obj in self.objects:
            self.table.insert(
                "", tk.END,
                values=(obj.name, obj.release_date, obj.ram_capability)
            )

    def run(self):
        self.root.mainloop()