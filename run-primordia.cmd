@echo off
setlocal
cd /d "%~dp0"

set "PRIMORDIA_PYTHON=.venv\Scripts\python.exe"

if not exist "%PRIMORDIA_PYTHON%" (
    echo [PRIMORDIA] Creating a local Python environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo [PRIMORDIA] Python 3.12 or newer is required.
        pause
        exit /b 1
    )

    echo [PRIMORDIA] Installing dependencies...
    "%PRIMORDIA_PYTHON%" -m pip install -e ".[dev]"
    if errorlevel 1 (
        echo [PRIMORDIA] Dependency installation failed.
        pause
        exit /b 1
    )
)

"%PRIMORDIA_PYTHON%" -m primordia %*
set "PRIMORDIA_EXIT=%ERRORLEVEL%"

if not "%PRIMORDIA_EXIT%"=="0" (
    echo.
    echo [PRIMORDIA] The program exited with code %PRIMORDIA_EXIT%.
    pause
)

exit /b %PRIMORDIA_EXIT%
