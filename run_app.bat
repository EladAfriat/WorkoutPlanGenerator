@echo off
cd /d "%~dp0"
echo Starting Streamlit Workout Plan Generator...
echo Current directory: %CD%
echo.
if exist "src\streamlit_app.py" (
    echo Found streamlit_app.py
    echo The app will open in your browser automatically.
    echo.
    echo Local access: http://localhost:8501
    echo Network access: http://10.8.33.228:8501
    echo.
    echo Other computers on the same network can access using the network address above.
    echo.
    echo Press Ctrl+C to stop the server.
    echo.
    python -m streamlit run src\streamlit_app.py --server.port 8501 --server.address 0.0.0.0
) else (
    echo ERROR: streamlit_app.py not found!
    echo Looking for: %CD%\src\streamlit_app.py
    pause
    exit /b 1
)
pause
