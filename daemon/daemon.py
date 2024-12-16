import os
import time
import json
import shutil
import logging
from datetime import datetime
import signal
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

is_running = False

def load_config(config_path):
    """Загрузить конфигурацию из файла.""" 
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def setup_logging(log_file):
    """Настроить журналирование."""
    logging.basicConfig(filename=log_file, level=logging.INFO, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def backup_files(source_dir, backup_dir):
    """Создать резервные копии файлов из исходного каталога в каталог резервных копий."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
    
    try:
        shutil.copytree(source_dir, backup_path)
        logging.info(f"Backup successful: {backup_path}")
    except Exception as e:
        logging.error(f"Backup failed: {e}")

def run_backup_daemon(config_path):
    """Запустить демон резервного копирования."""
    global is_running
    is_running = True

    config = load_config(config_path)
    source_dir = config['source_dir']
    backup_dir = config['backup_dir']
    interval = config['interval_seconds']
    log_file = config['log_file']
    
    setup_logging(log_file)
    
    logging.info("Starting backup daemon...")
    
    while is_running:
        backup_files(source_dir, backup_dir)
        time.sleep(interval)

    logging.info("Daemon stopped.")

def stop_daemon():
    """Остановить демон."""
    global is_running
    is_running = False
    logging.info("Stopping daemon...")

def start_daemon(config_path):
    """Запустить демон в отдельном потоке."""
    threading.Thread(target=run_backup_daemon, args=(config_path,), daemon=True).start()

class BackupConfigGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Backup Daemon Configuration")

        # Исходный каталог
        self.source_label = tk.Label(master, text="Source Directory:")
        self.source_label.pack()
        self.source_entry = tk.Entry(master)
        self.source_entry.pack()

        # Каталог резервных копий
        self.backup_label = tk.Label(master, text="Backup Directory:",)
        self.backup_label.pack()
        self.backup_entry = tk.Entry(master)
        self.backup_entry.pack()

        # Интервал копирования
        self.interval_label = tk.Label(master, text="Backup Interval (seconds):")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(master)
        self.interval_entry.pack()

        # Кнопка сохранения
        self.save_button = tk.Button(master, text="Save Configuration", command=self.save_config)
        self.save_button.pack()

        # Кнопка запуска демона
        self.run_daemon_button = tk.Button(master, text="Run Backup Daemon", command=self.run_daemon)
        self.run_daemon_button.pack()

        # Кнопка остановки демона
        self.stop_daemon_button = tk.Button(master, text="Stop Backup Daemon", command=stop_daemon)
        self.stop_daemon_button.pack()

        # Загрузка конфигурации
        self.load_config()

    def save_config(self):
        config = {
            "source_dir": self.source_entry.get(),
            "backup_dir": self.backup_entry.get(),
            "interval_seconds": int(self.interval_entry.get()),
            "log_file": "lesson2/backup_daemon.log" 
        }
        with open('lesson2/backup_config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        messagebox.showinfo("Info", "Configuration saved successfully!")

    def load_config(self):
        if os.path.exists('lesson2/backup_config.json'):
            with open('lesson2/backup_config.json', 'r') as config_file:
                config = json.load(config_file)
                self.source_entry.insert(0, config.get('source_dir', ''))
                self.backup_entry.insert(0, config.get('backup_dir', ''))
                self.interval_entry.insert(0, config.get('interval_seconds', ''))

    def run_daemon(self):
        self.save_config()
        start_daemon('lesson2/backup_config.json')

if __name__ == "__main__":
    root = tk.Tk()
    gui = BackupConfigGUI(root)
    root.mainloop()
# /home/alicee/Desktop/linux_programming_spbu/lesson2/backup_config.json