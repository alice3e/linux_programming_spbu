import tkinter as tk
from tkinter import ttk
from threading import Thread
from monitor import ProcessMonitor, start_file_monitoring
from loggerr import EventLogger
import os


class AuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Системный мониторинг")
        self.logger = EventLogger()
        self.observer = None
        self.monitoring = False
        
        
        # GUI элементы
        self.log_text = tk.Text(root, wrap=tk.WORD, height=20, width=80)
        self.log_text.pack(pady=10)

        filter_frame = ttk.Frame(root)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Искать по:").grid(row=0, column=0, padx=5)
        self.filter_option = ttk.Combobox(filter_frame, values=["pid", "type", "path", "name"], state="readonly")
        self.filter_option.grid(row=0, column=1, padx=5)
        self.filter_option.current(0)
    

        ttk.Label(filter_frame, text="Значение:").grid(row=0, column=2, padx=5)
        self.filter_entry = ttk.Entry(filter_frame, width=20)
        self.filter_entry.grid(row=0, column=3, padx=5)

        self.search_button = ttk.Button(filter_frame, text="Поиск", command=self.search_events)
        self.search_button.grid(row=0, column=4, padx=5)


        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Начать мониторинг", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(button_frame, text="Остановить мониторинг", command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=10)

    def log_event(self, event_type, event_data):
        """Обработчик для записи события и отправки уведомлений."""
        # Логируем событие в файл
        self.logger.log_event(event_type, event_data)
        
        # Добавляем событие в интерфейс
        self.log_text.insert(tk.END, f"{event_type}: {event_data}\n")
        self.log_text.see(tk.END)

        # Отправляем уведомление через monitor_process
        pid = event_data.get("pid")
        name = event_data.get("name")
        response = self.logger.monitor_process(pid=pid, name=name)
        
        # Логируем ответ от сервера в консоль (опционально)
        if response and response.status_code == 200:
            print(f"Notification sent: {response.json()}")
        else:
            print(f"Failed to send notification: {response}")


    def search_events(self):
        """Обработчик для поиска событий."""
        filter_key = self.filter_option.get()
        filter_value = self.filter_entry.get()

        # Преобразуем filter_value в нужный тип (например, для pid это должно быть int)
        if filter_key == "pid" and filter_value.isdigit():
            filter_value = int(filter_value)  # Преобразуем строку в int для pid

        filters = {filter_key: filter_value} if filter_value else {}
        results = self.logger.search_events(filters)

        # Очистка текстового поля и вывод результатов
        self.log_text.delete(1.0, tk.END)
        for event in results:
            self.log_text.insert(tk.END, f"{event}\n")

    def start_monitoring(self):
        """Запуск мониторинга."""
        if not self.monitoring:
            log_file = os.path.abspath(self.logger.log_file)
            self.monitoring = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            # Запуск процесса мониторинга
            self.process_thread = Thread(target=ProcessMonitor.monitor_processes, args=(self.log_event,), daemon=True)
            self.process_thread.start()
            
            # Запуск наблюдателя за файловой системой
            self.observer = start_file_monitoring(self.log_event, excluded_files=[log_file])
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def stop_monitoring(self):
        """Остановка мониторинга."""
        if self.monitoring:
            self.monitoring = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

            # Остановка процесса мониторинга
            ProcessMonitor.stop_monitoring()
            if self.process_thread.is_alive():
                self.process_thread.join()

            # Остановка наблюдателя
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None

    def on_close(self):
        """Закрытие приложения."""
        self.stop_monitoring()
        self.root.destroy()
        self.root.quit()



if __name__ == "__main__":
    root = tk.Tk()
    app = AuditApp(root)
    root.mainloop()
