cd dash
start /B python3 main.py
cd ../aws
start /B python3 aws_app.py
timeout 5 /nobreak
start "" http://127.0.0.1:8050/
