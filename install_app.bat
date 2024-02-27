@echo off

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Install the requirements from the local directory
pip install -r requirements.txt

REM Remove the migrations file if it exists
if exist migrations rmdir /S /Q migrations

REM Pause the script for 10 seconds
timeout /T 10

REM Run the Flask application
flask db init
flask db migrate
flask db upgrade

