import json
from datetime import datetime

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
                        # Ищем pid в data для событий process_start и process_end
                        pid = event.get("data", {}).get("pid")
                        if pid is None or pid != value:
                            match = False
                            break
                    elif key == "path":
                        # Ищем path в data для события file_modified
                        path = event.get("data", {}).get("path")
                        if path is None or path != value:
                            match = False
                            break
                    elif key == "name":
                        # Ищем name в data для события process_start
                        name = event.get("data", {}).get("name")
                        if name is None or name != value:
                            match = False
                            break
                    elif key == "type":
                        # Ищем type на верхнем уровне записи
                        if event.get("type") != value:
                            match = False
                            break
                    else:
                        # Если фильтр не соответствует известным ключам
                        match = False
                        break
                
                if match:
                    results.append(event)
        return results
