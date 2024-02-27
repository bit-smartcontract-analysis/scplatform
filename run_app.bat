@echo off

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Run the Flask application
set FLASK_APP=app.py
flask run

