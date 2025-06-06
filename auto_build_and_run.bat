@echo off
SETLOCAL ENABLEEXTENSIONS

set "BASE_DIR=%~dp0"
rem Remove trailing backslash from BASE_DIR to avoid quoting issues
if "%BASE_DIR:~-1%"=="\\" set "BASE_DIR=%BASE_DIR:~0,-1%"
cd /d "%BASE_DIR%"
set "PYTHON_DIR=%BASE_DIR%\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

REM -------------------------------------------------------------
REM Update repository before building if git is available
REM -------------------------------------------------------------
if exist "%BASE_DIR%.git" (
    git --version >nul 2>&1
    if not errorlevel 1 (
        echo Checking for updates in repository...
        git -C "%BASE_DIR%" pull
    )
)

REM -------------------------------------------------------------
REM Install portable Python locally if it does not exist
REM -------------------------------------------------------------
if not exist "%PYTHON_EXE%" (
    echo Downloading portable Python...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip -OutFile '%BASE_DIR%python.zip'"
    powershell -Command "Expand-Archive -Path '%BASE_DIR%python.zip' -DestinationPath '%PYTHON_DIR%'"
    del "%BASE_DIR%python.zip"
    rem Enable site packages in the embedded distribution
    powershell -Command "(Get-Content '%PYTHON_DIR%\\python310._pth') -replace '#import site','import site' | Set-Content '%PYTHON_DIR%\\python310._pth'"
    powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile '%BASE_DIR%get-pip.py'"
    "%PYTHON_EXE%" "%BASE_DIR%get-pip.py" >nul
    del "%BASE_DIR%get-pip.py"
)

REM -------------------------------------------------------------
REM Install Python dependencies using the local interpreter
REM -------------------------------------------------------------
"%PYTHON_EXE%" -m pip install -r requirements.txt
"%PYTHON_EXE%" -m pip install pyinstaller

REM -------------------------------------------------------------
REM Ensure portable Tesseract is downloaded before building
REM -------------------------------------------------------------
"%PYTHON_EXE%" -c "import ocr_screen; ocr_screen.ensure_tesseract()"

REM -------------------------------------------------------------
REM Build executable in the current directory if not already built
REM -------------------------------------------------------------
if not exist "%BASE_DIR%gui_app.exe" (
    "%PYTHON_EXE%" -m PyInstaller --noconsole --onefile gui_app.py --distpath "%BASE_DIR%"
)

REM -------------------------------------------------------------
REM Launch the GUI application
REM -------------------------------------------------------------
start "" "%BASE_DIR%gui_app.exe"
ENDLOCAL

