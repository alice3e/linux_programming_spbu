import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
from datetime import datetime


# Функция для загрузки логов
def load_log_data(log_file):
    events = []
    with open(log_file, "r") as f:
        for line in f:
            events.append(json.loads(line))
    return events


# Функция для обработки событий
def process_events(events):
    # Преобразуем в DataFrame для удобства работы
    df = pd.DataFrame(events)
    # Преобразуем timestamp в datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    # Добавляем колонку с только временем (для удобства группировки)
    df["time"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def plot_file_modifications(df, output_dir):
    """Строит круговую диаграмму изменений файлов и сохраняет в файл."""
    file_modifications = df[df["type"] == "file_modified"]
    file_count = file_modifications['data'].apply(lambda x: x['path']).value_counts()

    plt.figure(figsize=(8, 8))
    plt.pie(file_count, labels=file_count.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Количество изменений файлов")
    plt.axis('equal')
    plt.tight_layout()
    output_path = f"{output_dir}/file_modifications.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_event_type_distribution(df, output_dir):
    """Строит круговую диаграмму распределения типов событий и сохраняет в файл."""
    event_types = df["type"].value_counts()

    plt.figure(figsize=(7, 7))
    event_types.plot(kind="pie", autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    plt.title("Распределение типов событий")
    plt.ylabel("")
    plt.tight_layout()
    output_path = f"{output_dir}/event_type_distribution.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_process_distribution(df, output_dir):
    """Строит гистограмму распределения запускаемых процессов и сохраняет в файл."""
    process_names = df[df["type"] == "process_start"]["data"].apply(lambda x: x["name"])
    process_counts = process_names.value_counts()

    plt.figure(figsize=(10, 6))
    process_counts.plot(kind="bar", color="lightgreen")
    plt.title("Распределение запускаемых процессов")
    plt.xlabel("Имя процесса")
    plt.ylabel("Количество запусков")
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = f"{output_dir}/process_distribution.png"
    plt.savefig(output_path)
    plt.close()
    return output_path


# Основная функция для генерации графиков
def generate_plots(log_file, output_dir):
    """Генерация графиков на основе логов и сохранение их в директорию."""
    events = load_log_data(log_file)
    df = process_events(events)

    # Сохраняем все графики
    file_modifications_path = plot_file_modifications(df, output_dir)
    event_type_distribution_path = plot_event_type_distribution(df, output_dir)
    process_distribution_path = plot_process_distribution(df, output_dir)

    return {
        "file_modifications": file_modifications_path,
        "event_type_distribution": event_type_distribution_path,
        "process_distribution": process_distribution_path,
    }


if __name__ == "__main__":
    log_file = "event_log.json"
    output_dir = "plots"
    import os
    os.makedirs(output_dir, exist_ok=True)
    generate_plots(log_file, output_dir)
