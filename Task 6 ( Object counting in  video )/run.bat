@echo off
REM Activate virtual environment and run the Flask application

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask application...
python app.py
