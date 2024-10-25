import tarfile
import os
import csv
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import calendar
import sys

# Глобальные переменные для эмуляции файловой системы и логирования
path = ['/']
log_file = None
all_f = []

def load_files_from_tar(tar_path):
    """Загружает файлы и папки из TAR архива в глобальный список all_f."""
    global all_f
    all_f = []  # Инициализируем пустой список
    with tarfile.open(tar_path, 'r') as tar:
        for tarinfo in tar.getmembers():
            if tarinfo.isdir():  # Если это директория
                all_f.append('/'+tarinfo.name)  # Добавляем слеш в конце
            else:
                all_f.append(tarinfo.name)  # Просто добавляем имя файла


def log_action(command, param):
    """Записывает действия в лог-файл."""
    with open(log_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([str(datetime.now()), command, param])

def who():
    """Команда who: Возвращает информацию о текущем пользователе."""
    return f"Current user: {os.getlogin()}"

def cal():
    """Команда cal: Возвращает текущий календарь."""
    now = datetime.now()
    return calendar.month(now.year, now.month)

def touch(filename):
    """Команда touch: Создает пустой файл."""
    filepath = ''.join(filename)
    if filepath not in all_f:  # Изменено на all_f
        all_f.append(filepath)  # Добавляем файл в список
        log_action("touch", filename)
        return f"File '{filename}' created."
    else:
        return f"File '{filename}' already exists."


def ls():
    """Команда ls: Показывает содержимое текущей директории."""
    global all_f  # Убедитесь, что all_f объявлена как глобальная
    current_path = '/'.join(path).rstrip('/')  # Формируем текущий путь без лишних слешей

    # Если текущий путь пустой, выбираем корень
    if not current_path:
        contents = [f for f in all_f if f.startswith('')]  # все файлы в корне
    else:
        contents = [f[len(current_path) + 1:] for f in all_f if f.startswith(current_path + '/')]


    if contents:
        return "\n".join(contents)
    else:
        return f"No files or directories in '{current_path}'"


def cd(directory):
    """Команда cd: Переход в указанную директорию."""
    global path
    if directory == '..':
        if len(path) > 1:
            path.pop()  # Убираем последний элемент пути
    else:
        potential_path = ''.join(path + [directory]).rstrip('/')
        print(all_f)
        print(potential_path)
        if potential_path in all_f:  # Проверяем наличие директории с / в конце
            path.append(directory)  # Переход в новую директорию
        else:
            return f"Directory '{directory}' not found"
    return f"Changed directory to {''.join(path)}"


def process_command(command_line, text_area):
    """Обрабатывает команды пользователя."""
    try:
        command, *param = command_line.split()
    except ValueError:
        return

    output = ""

    if command == "who":
        output = who()

    elif command == "cal":
        output = cal()

    elif command == "touch":
        if param:
            output = touch(param[0])
        else:
            output = "You need to specify a file name."

    elif command == "ls":
        output = ls()

    elif command == "cd":
        if param:
            output = cd(param[0]) or f"Changed directory to {'/'.join(path)}"
        else:
            output = "You need to specify a directory."

    elif command == "exit":
        log_action("exit", "")
        text_area.insert(tk.END, "Exiting...\n")
        text_area.master.quit()

    else:
        output = f"Command '{command}' not recognized."

    text_area.insert(tk.END, "\n" + output)
    log_action(command, param)

def create_shell_gui(computer_name):
    """Создает GUI для эмулятора оболочки."""
    window = tk.Tk()
    window.title("Shell Emulator")

    # Текстовое поле для вывода
    text_area = scrolledtext.ScrolledText(window, height=30, width=100, bg='black', fg='white', insertbackground='white')
    text_area.pack()

    # Ввод команд и вывод приглашения
    def on_enter(event):
        command_line = text_area.get("end-2l linestart", "end-1c").split("$")[-1].strip()
        if command_line:
            process_command(command_line, text_area)
        text_area.insert(tk.END, f"\n[user@{computer_name}] : {''.join(path)} $ ")
        text_area.see(tk.END)
        return "break"

    text_area.bind("<Return>", on_enter)

    text_area.insert(tk.END, f"[user@{computer_name}] : {'/'.join(path)} $ ")
    window.mainloop()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python emulator.py <computer_name> <tar_path> <log_file>")
        sys.exit(1)

    # Получение аргументов командной строки
    computer_name = sys.argv[1]
    tar_path = sys.argv[2]
    log_file = sys.argv[3]

    # Инициализация лог-файла
    with open(log_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Command", "Parameter"])

    # Загружаем файловую систему
    load_files_from_tar(tar_path)

    # Запускаем GUI
    create_shell_gui(computer_name)
