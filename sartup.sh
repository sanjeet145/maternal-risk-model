pip install -r requirements.txt
gunicorn app:app -b 0.0.0.0:8001 --workers 4 --threads 2