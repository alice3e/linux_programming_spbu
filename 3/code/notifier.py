from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# Хранение последних уведомлений
notifications = []

@app.route('/')
def index():
    # Отображаем простой HTML с кнопкой
    return render_template('index.html')

@app.route('/send_notification', methods=['POST'])
def send_notification():
    # Получаем данные из POST-запроса
    process_name = request.json.get('process_name', 'Unknown process')
    pid = request.json.get('pid', 'Unknown PID')
    
    # Формируем сообщение
    notification = f"Process {process_name} (PID: {pid}) started!"
    
    # Добавляем уведомление в список
    notifications.append(notification)
    
    # Ограничиваем количество уведомлений
    if len(notifications) > 10:  # Сохраняем только последние 10 уведомлений
        notifications.pop(0)
    
    return jsonify({"message": notification})

if __name__ == '__main__':
    app.run(debug=True)

