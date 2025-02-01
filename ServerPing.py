import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ping3 import ping
import json
import os
import time
import socket

# Глобальные переменные для хранения данных
server_labels = {}  # Хранение меток с IP-адресами или именами серверов
server_statuses = {}  # Хранение меток со статусами
server_frames = {}  # Хранение фреймов для каждого сервера
continuous_ping_active = False  # Флаг для постоянного пинга

# Функция для проверки доступности сервера
def check_server(ip_or_hostname, status_label):
    try:
        # Пытаемся разрешить имя сервера в IP-адрес
        ip_address = socket.gethostbyname(ip_or_hostname)
        response = ping(ip_address, timeout=2)
        if response is not None:
            status_label.config(text="●", fg="green", font=("Arial", 16))  # Зеленый кружок
        else:
            status_label.config(text="●", fg="red", font=("Arial", 16))  # Красный кружок
    except Exception as e:
        status_label.config(text="●", fg="red", font=("Arial", 16))  # Красный кружок при ошибке

# Функция для запуска проверки всех серверов
def start_ping():
    for ip_or_hostname, status_label in server_statuses.items():
        threading.Thread(target=check_server, args=(ip_or_hostname, status_label)).start()

# Функция для добавления сервера
def add_server():
    ip_or_hostname = ip_entry.get().strip()
    if ip_or_hostname:
        if ip_or_hostname in server_labels:
            messagebox.showwarning("Ошибка", "Сервер уже добавлен!")
            return
        # Создаем фрейм для сервера
        server_frame_item = tk.Frame(server_frame)
        server_frame_item.pack(pady=5, fill=tk.X)

        # Кружок статуса
        status_label = tk.Label(server_frame_item, text="●", fg="gray", font=("Arial", 16))  # Серый кружок по умолчанию
        status_label.pack(side=tk.LEFT, padx=5)

        # Метка с IP-адресом или именем сервера
        ip_label = tk.Label(server_frame_item, text=ip_or_hostname, font=("Arial", 10))
        ip_label.pack(side=tk.LEFT, padx=5)

        # Кнопка удаления
        delete_button = tk.Button(server_frame_item, text="Удалить", command=lambda: delete_server(ip_or_hostname, server_frame_item), font=("Arial", 9))
        delete_button.pack(side=tk.RIGHT, padx=5)

        # Сохраняем элементы
        server_labels[ip_or_hostname] = ip_label
        server_statuses[ip_or_hostname] = status_label
        server_frames[ip_or_hostname] = server_frame_item

        ip_entry.delete(0, tk.END)
        save_servers()

# Функция для удаления сервера
def delete_server(ip_or_hostname, server_frame_item):
    server_frame_item.destroy()
    del server_labels[ip_or_hostname]
    del server_statuses[ip_or_hostname]
    del server_frames[ip_or_hostname]
    save_servers()

# Функция для сохранения списка серверов в файл
def save_servers():
    with open("servers.json", "w") as file:
        json.dump(list(server_labels.keys()), file)

# Функция для загрузки списка серверов из файла
def load_servers():
    if os.path.exists("servers.json"):
        with open("servers.json", "r") as file:
            servers = json.load(file)
            for ip_or_hostname in servers:
                add_server_from_file(ip_or_hostname)

# Функция для добавления сервера из файла (без проверки на дубликаты)
def add_server_from_file(ip_or_hostname):
    # Создаем фрейм для сервера
    server_frame_item = tk.Frame(server_frame)
    server_frame_item.pack(pady=5, fill=tk.X)

    # Кружок статуса
    status_label = tk.Label(server_frame_item, text="●", fg="gray", font=("Arial", 16))  # Серый кружок по умолчанию
    status_label.pack(side=tk.LEFT, padx=5)

    # Метка с IP-адресом или именем сервера
    ip_label = tk.Label(server_frame_item, text=ip_or_hostname, font=("Arial", 10))
    ip_label.pack(side=tk.LEFT, padx=5)

    # Кнопка удаления
    delete_button = tk.Button(server_frame_item, text="Удалить", command=lambda: delete_server(ip_or_hostname, server_frame_item), font=("Arial", 9))
    delete_button.pack(side=tk.RIGHT, padx=5)

    # Сохраняем элементы
    server_labels[ip_or_hostname] = ip_label
    server_statuses[ip_or_hostname] = status_label
    server_frames[ip_or_hostname] = server_frame_item

# Функция для запуска постоянного пинга
def start_continuous_ping():
    def ping_loop():
        while continuous_ping_active:
            start_ping()
            time.sleep(int(interval_entry.get()))
    global continuous_ping_active
    continuous_ping_active = True
    threading.Thread(target=ping_loop).start()

# Функция для остановки постоянного пинга
def stop_continuous_ping():
    global continuous_ping_active
    continuous_ping_active = False

# Функция для сброса статусов серверов
def reset_server_statuses():
    for status_label in server_statuses.values():
        status_label.config(text="●", fg="gray", font=("Arial", 16))  # Серый кружок

# Функция для показа/скрытия кнопок постоянного пинга
def toggle_settings():
    if continuous_ping_frame.winfo_ismapped():
        continuous_ping_frame.pack_forget()
    else:
        continuous_ping_frame.pack(pady=10)

# Создание графического интерфейса
def create_gui():
    global root, server_frame, continuous_ping_frame, interval_entry

    root = tk.Tk()
    root.title("Server Ping Monitor")
    root.geometry("400x400")  # Компактный размер окна

    # Поле для ввода IP-адресов или имен серверов
    ip_frame = tk.Frame(root)
    ip_frame.pack(pady=10, fill=tk.X)

    tk.Label(ip_frame, text="Введите IP-адрес или имя сервера:", font=("Arial", 10)).pack()

    global ip_entry
    ip_entry = tk.Entry(ip_frame, width=30, font=("Arial", 10))
    ip_entry.pack(pady=5)

    # Кнопка для добавления сервера
    add_button = tk.Button(ip_frame, text="Добавить сервер", command=add_server, font=("Arial", 10))
    add_button.pack(pady=5)

    # Фрейм для отображения серверов и их статусов
    global server_frame
    server_frame = tk.Frame(root)
    server_frame.pack(fill=tk.BOTH, expand=True)

    # Кнопка для запуска проверки
    ping_button = tk.Button(root, text="Проверить серверы", command=start_ping, font=("Arial", 10))
    ping_button.pack(pady=10)

    # Кнопка "Настройки"
    settings_button = tk.Button(root, text="Настройки", command=toggle_settings, font=("Arial", 10))
    settings_button.pack(pady=10)

    # Фрейм для кнопок постоянного пинга и сброса статусов
    global continuous_ping_frame
    continuous_ping_frame = tk.Frame(root)

    tk.Label(continuous_ping_frame, text="Интервал пинга (сек):", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    interval_entry = tk.Entry(continuous_ping_frame, width=5, font=("Arial", 9))
    interval_entry.insert(0, "30")
    interval_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(continuous_ping_frame, text="Запустить пинг", command=start_continuous_ping, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Button(continuous_ping_frame, text="Остановить пинг", command=stop_continuous_ping, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    tk.Button(continuous_ping_frame, text="Обнулить состояние", command=reset_server_statuses, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

    # Загрузка сохраненных серверов при запуске
    load_servers()

    root.mainloop()

# Запуск GUI
if __name__ == "__main__":
    create_gui()