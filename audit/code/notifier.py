from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
notifications = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_notification', methods=['POST'])
def send_notification():
    process_name = request.json.get('process_name', 'Unknown process')
    pid = request.json.get('pid', 'Unknown PID')
    notification = f"Process {process_name} (PID: {pid}) started!"
    notifications.append(notification)
    if len(notifications) > 10:
        notifications.pop(0)
    return jsonify({"message": notification})

@app.route('/notifications', methods=['GET'])
def get_notifications():
    return jsonify(notifications)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
