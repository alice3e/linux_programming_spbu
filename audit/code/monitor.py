import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
import os
import requests


class ProcessMonitor:
    """Класс для мониторинга процессов в системе."""

    stop_flag = False

    @staticmethod
    def monitor_processes(callback):
        """Мониторинг запуска и завершения процессов."""
        current_processes = set(p.pid for p in psutil.process_iter())
        while not ProcessMonitor.stop_flag:
            time.sleep(0.3)
            updated_processes = set(p.pid for p in psutil.process_iter())
        
            # Новые процессы
            new_processes = updated_processes - current_processes
            for pid in new_processes:
                try:
                    proc = psutil.Process(pid)
                    callback("process_start", {"pid": pid, "name": proc.name(), "user": proc.username()})
                except psutil.NoSuchProcess:
                    pass
            
            # Завершенные процессы
            terminated_processes = current_processes - updated_processes
            for pid in terminated_processes:
                callback("process_end", {"pid": pid})
            
            current_processes = updated_processes

    @staticmethod
    def stop_monitoring():
        """Установка флага завершения для мониторинга процессов."""
        ProcessMonitor.stop_flag = True


class FileMonitor(FileSystemEventHandler):
    """Класс для отслеживания изменений в файловой системе."""

    def __init__(self, callback, excluded_files=None):
        """
        :param callback: Функция обратного вызова для обработки событий.
        :param excluded_files: Список абсолютных путей, которые нужно исключить.
        """
        self.callback = callback
        self.excluded_files = [os.path.abspath(f) for f in (excluded_files or [])]

    def on_any_event(self, event):
        """Обрабатывает любое событие файловой системы."""
        event_path = os.path.abspath(event.src_path)
        if not event.is_directory and event_path not in self.excluded_files:
            event_type = {
                "modified": "file_modified",
                "created": "file_created",
                "deleted": "file_deleted",
            }.get(event.event_type, "unknown")
            self.callback(event_type, {"path": event_path})


def start_file_monitoring(callback, path=".", excluded_files=None):
    """Запуск наблюдения за файловой системой."""
    observer = Observer()
    event_handler = FileMonitor(callback, excluded_files)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer


def send_notification(event_type, event_data):
    """Отправка уведомлений на сервер."""
    url = "http://127.0.0.1:5000/send_notification"
    payload = {
        "process_name": event_data.get("name", "Unknown"),
        "pid": event_data.get("pid", "Unknown")
    }
    try:
        print(f"Sending notification: {payload}")
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Проверка HTTP-статуса

        # Попробуем прочитать JSON
        try:
            response_data = response.json()
            print(f"Notification sent successfully: {response_data}")
        except ValueError:
            print(f"Server returned non-JSON response: {response.text}")
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}")



# Запуск мониторинга
if __name__ == "__main__":
    # Запуск мониторинга процессов
    process_thread = threading.Thread(target=ProcessMonitor.monitor_processes, args=(send_notification,))
    process_thread.start()

    # Запуск мониторинга файловой системы
    observer = start_file_monitoring(send_notification, path=".")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ProcessMonitor.stop_monitoring()
        observer.stop()
        observer.join()
        process_thread.join()
