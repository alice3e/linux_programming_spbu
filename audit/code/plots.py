import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
from datetime import datetime
import logging
import loggerr


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

def plot_file_modifications(df):
    # Фильтруем события, относящиеся к изменениям файлов
    file_modifications = df[df['type'] == 'file_modified']
    
    # Подсчитываем количество изменений для каждого файла
    file_count = file_modifications['data'].apply(lambda x: x['path']).value_counts()

    # Строим круговую диаграмму
    plt.figure(figsize=(8, 8))
    plt.pie(file_count, labels=file_count.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Количество изменений файлов")
    plt.axis('equal')  # Чтобы круг был кругом
    plt.tight_layout()
    plt.show()

# Построение круговой диаграммы по типу событий
def plot_event_type_distribution(df):
    event_types = df["type"].value_counts()
    
    plt.figure(figsize=(7, 7))
    event_types.plot(kind="pie", autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    plt.title("Распределение типов событий")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

# Построение гистограммы по процессам
def plot_process_distribution(df):
    process_names = df[df["type"] == "process_start"]["data"].apply(lambda x: x["name"])
    process_counts = process_names.value_counts()
    
    plt.figure(figsize=(10, 6))
    process_counts.plot(kind="bar", color="lightgreen")
    plt.title("Распределение запускаемых процессов")
    plt.xlabel("Имя процесса")
    plt.ylabel("Количество запусков")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Основная функция для генерации графиков
def generate_plots(log_file):
    events = load_log_data(log_file)
    df = process_events(events)
    
    plot_file_modifications(df)
    plot_event_type_distribution(df)
    plot_process_distribution(df)

if __name__ == "__main__":
    log_file = "event_log.json"  # Укажите путь к вашему файлу лога
    generate_plots(log_file)
