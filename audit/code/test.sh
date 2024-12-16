curl -X POST http://127.0.0.1:5000/send_notification \
-H "Content-Type: application/json" \
-d '{"process_name": "test_process", "pid": 12345}'
