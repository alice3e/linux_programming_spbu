import json
import os
import pandas as pd
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from plots import generate_plots  # Используем функцию для построения графиков

# Создаем директорию для графиков
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# Загрузка логов
def load_log_data(log_file):
    events = []
    with open(log_file, "r") as f:
        for line in f:
            events.append(json.loads(line))
    return events


# Генерация статистики по событиям
def generate_statistics(df):
    stats = {}

    # Общее количество событий
    stats["total_events"] = len(df)

    # Распределение событий по типам
    stats["event_type_distribution"] = df["type"].value_counts().to_dict()

    # Топ изменяемых файлов
    modified_files = df[df["type"] == "file_modified"]["data"].apply(lambda x: x["path"])
    stats["top_files_modified"] = modified_files.value_counts().head(5).to_dict()

    # Топ запускаемых процессов
    started_processes = df[df["type"] == "process_start"]["data"].apply(lambda x: x["name"])
    stats["top_processes_started"] = started_processes.value_counts().head(5).to_dict()

    # Топ завершённых процессов (если тип события есть в логах)
    if "process_end" in df["type"].unique():
        ended_processes = (
            df[df["type"] == "process_end"]["data"]
            .apply(lambda x: x["name"] if "name" in x else "Unknown")
        )
        stats["top_processes_ended"] = ended_processes.value_counts().head(5).to_dict()
    else:
        stats["top_processes_ended"] = {}


    return stats

# Генерация графиков и сохранение их как изображений
def save_graphs(log_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Используем существующую функцию для построения графиков
    plt.ioff()  # Отключаем интерактивный режим
    generate_plots(log_file, output_dir)  # Передаём директорию для сохранения графиков

    # Получаем пути к сохранённым графикам
    graph_files = [
        os.path.join(output_dir, fname)
        for fname in os.listdir(output_dir)
        if fname.endswith(".png")
    ]

    return graph_files



# Создание отчёта в формате Markdown
def generate_markdown_report(stats, graphs, output_file):
    with open(output_file, "w") as f:
        # Заголовок
        f.write("# Отчёт по логам событий\n\n")
        f.write(f"Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Общее количество событий
        f.write(f"## Общее количество событий: {stats['total_events']}\n\n")

        # Распределение событий по типам
        f.write("## Распределение событий по типам:\n")
        for event_type, count in stats["event_type_distribution"].items():
            f.write(f"- {event_type}: {count}\n")
        f.write("\n")

        # Топ изменяемых файлов
        f.write("## Топ изменяемых файлов:\n")
        for file_path, count in stats["top_files_modified"].items():
            f.write(f"- {file_path}: {count}\n")
        f.write("\n")

        # Топ запускаемых процессов
        f.write("## Топ запускаемых процессов:\n")
        for process, count in stats["top_processes_started"].items():
            f.write(f"- {process}: {count}\n")
        f.write("\n")

        # Топ завершённых процессов
        f.write("## Топ завершённых процессов:\n")
        for process, count in stats["top_processes_ended"].items():
            f.write(f"- {process}: {count}\n")
        f.write("\n")

        # Вставка графиков
        f.write("## Графики:\n")
        for graph_path in graphs:
            f.write(f"![График]({graph_path})\n\n")


# Основная функция
def main():
    log_file = "event_log.json"  # Путь к файлу логов
    output_dir = "graphs"       # Папка для сохранения графиков
    output_md = "report.md"     # Путь для сохранения отчёта

    # Загружаем данные и преобразуем в DataFrame
    events = load_log_data(log_file)
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Генерируем статистику
    stats = generate_statistics(df)

    # Создаём графики и сохраняем их
    graphs = save_graphs(log_file, output_dir)

    # Генерируем Markdown-отчёт
    generate_markdown_report(stats, graphs, output_md)
    print(f"Отчёт сохранён в {output_md}")


if __name__ == "__main__":
    main()
