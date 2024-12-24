@echo off

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Run celery to sending mail
celery -A app.mycelery worker --loglevel=info -P gevent

