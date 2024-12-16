import json
from datetime import datetime
import requests
import psutil

class EventLogger:
    """Класс для работы с журналом событий."""

    def __init__(self, log_file="event_log.json"):
        self.log_file = log_file

    def log_event(self, event_type, event_data):
        """Запись события в журнал."""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def search_events(self, filters):
        """Поиск событий по критериям."""
        results = []
        with open(self.log_file, "r") as f:
            for line in f:
                event = json.loads(line)
                match = True
                
                for key, value in filters.items():
                    if key == "pid":
                        pid = event.get("data", {}).get("pid")
                        if pid is None or pid != value:
                            match = False
                            break
                    elif key == "path":
                        path = event.get("data", {}).get("path")
                        if path is None or path != value:
                            match = False
                            break
                    elif key == "name":
                        name = event.get("data", {}).get("name")
                        if name is None or name != value:
                            match = False
                            break
                    elif key == "type":
                        if event.get("type") != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if match:
                    results.append(event)
        return results
    
    def monitor_process(self, pid=None, name=None):
        """Мониторинг процесса по pid или name. Отправка уведомлений при старте или завершении."""
        # Если pid или name не переданы, заменяем их на 'Unknown'
        process_name = name if name else 'Unknown'
        process_pid = pid if pid else 'Unknown'
        
        # Отправка уведомления через POST запрос
        response = requests.post("http://127.0.0.1:8080/send_notification", json={
            "process_name": process_name,
            "pid": process_pid
        })
        return response

