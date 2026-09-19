@echo off
setlocal EnableExtensions EnableDelayedExpansion

title UIDetect - Installation

REM =================================================
REM Installation Mode
REM =================================================
REM When launched by Inno Setup:
REM Install_UIDetect.bat /INSTALLER
REM
REM The BAT will run silently and report progress
REM through the status file.
REM =================================================

set "INSTALLER_MODE=0"

if /I "%~1"=="/INSTALLER" (
    set "INSTALLER_MODE=1"
)

REM =================================================
REM Configuration
REM =================================================

set "PYTHON_VERSION=3.13.14"
set "PYTHON_INSTALLER=python-3.13.14-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.13.14/python-3.13.14-amd64.exe"

set "OLLAMA_INSTALLER=OllamaSetup.exe"
set "OLLAMA_URL=https://ollama.com/download/OllamaSetup.exe"
set "OLLAMA_MODEL=qwen2.5:3b"

set "TEMP_DIR=%TEMP%\UIDetectInstaller"
set "STATUS_FILE=%TEMP_DIR%\install_status.txt"
set "LOG_FILE=%TEMP_DIR%\install.log"
set "OLLAMA_DEBUG_LOG=%TEMP_DIR%\ollama_debug_timeline.txt"
set "QWEN_DOWNLOAD_LOG=%TEMP_DIR%\qwen_download.log"


if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM =================================================
REM Ollama Debug / Timeline Log
REM =================================================

> "%OLLAMA_DEBUG_LOG%" echo ==============================================
>> "%OLLAMA_DEBUG_LOG%" echo UIDetect Ollama Installation Debug Timeline
>> "%OLLAMA_DEBUG_LOG%" echo Started: %DATE% %TIME%
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================


REM =================================================
REM Qwen Download Log
REM =================================================

> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
>> "%QWEN_DOWNLOAD_LOG%" echo UIDetect Qwen Model Download Log
>> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
>> "%QWEN_DOWNLOAD_LOG%" echo Started: %DATE% %TIME%
>> "%QWEN_DOWNLOAD_LOG%" echo Model: %OLLAMA_MODEL%
>> "%QWEN_DOWNLOAD_LOG%" echo Status: WAITING_FOR_MODEL_CHECK
>> "%QWEN_DOWNLOAD_LOG%" echo.


REM =================================================
REM Create / Reset Status File
REM =================================================

> "%STATUS_FILE%" echo 0^|Starting UIDetect installation...
> "%LOG_FILE%" echo ==============================================
>> "%LOG_FILE%" echo [!TIME!] UIDetect Installer Log
>> "%LOG_FILE%" echo [!TIME!] Started: %DATE% %TIME%
>> "%LOG_FILE%" echo ==============================================

REM =================================================
REM Redirect Output When Running From Installer
REM =================================================

if "%INSTALLER_MODE%"=="1" (
    >> "%LOG_FILE%" echo [!TIME!] INSTALLER MODE DETECTED
    >> "%LOG_FILE%" echo [!TIME!] BAT PATH: %~f0
    >> "%LOG_FILE%" echo [!TIME!] INSTALLER ARGUMENT: %~1
    goto INSTALLER_START
)

echo ==============================================
echo              UIDetect Installation
echo ==============================================
echo.
echo This process will check and install the required
echo software and Python dependencies for UIDetect.
echo.
echo Python %PYTHON_VERSION% and %OLLAMA_MODEL% are required.
echo Missing components will be downloaded automatically.
echo.
echo An Internet connection is required if Python,
echo Ollama, or the AI model is missing.
echo.

:INSTALLER_START

>> "%LOG_FILE%" echo [!TIME!] INSTALLER_START REACHED
>> "%LOG_FILE%" echo [!TIME!] Beginning Python check

REM =================================================
REM Check / Install Python
REM =================================================

call :SetStatus 10 "Checking Python installation"

set "PYTHON_EXE="

>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo ==============================================
>> "%LOG_FILE%" echo [!TIME!] PYTHON DETECTION STARTED
>> "%LOG_FILE%" echo ==============================================


REM =====================================================
REM TEST 6 - Check Python from PATH
REM =====================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 6 - Checking Python from PATH

for /f "delims=" %%P in ('where python 2^>nul') do (

    set "PATH_CANDIDATE=%%P"

    >> "%LOG_FILE%" echo [!TIME!] PATH candidate found: !PATH_CANDIDATE!

    REM Ignore Windows Store / App Execution Alias
    echo !PATH_CANDIDATE! | findstr /I /C:"\WindowsApps\" >nul

    if not errorlevel 1 (

        >> "%LOG_FILE%" echo [!TIME!] Ignoring Windows Store Python alias: !PATH_CANDIDATE!

    ) else (

        if exist "!PATH_CANDIDATE!" (

            for /f "tokens=*" %%V in ('"!PATH_CANDIDATE!" --version 2^>nul') do (

                set "PYTHON_VERSION_FOUND=%%V"

                >> "%LOG_FILE%" echo [!TIME!] Version detected: !PYTHON_VERSION_FOUND!

            )

            echo !PYTHON_VERSION_FOUND! | findstr /I /C:"Python %PYTHON_VERSION%" >nul

            if not errorlevel 1 (

                set "PYTHON_EXE=!PATH_CANDIDATE!"

                >> "%LOG_FILE%" echo [!TIME!] Required Python found: !PYTHON_EXE!

                goto PYTHON_FOUND

            )

        )

    )
)

>> "%LOG_FILE%" echo [!TIME!] TEST 6 COMPLETED


REM ============================================================
REM TEST 7 - Check 64-bit Program Files
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 7 - Checking 64-bit Program Files
>> "%LOG_FILE%" echo [!TIME!] ProgramW6432=%ProgramW6432%

if exist "%ProgramW6432%\Python313\python.exe" goto PYTHON_PROGRAMW6432

>> "%LOG_FILE%" echo [!TIME!] Python not found in ProgramW6432.
>> "%LOG_FILE%" echo [!TIME!] TEST 7 COMPLETED

goto PYTHON_TEST_8


:PYTHON_PROGRAMW6432

>> "%LOG_FILE%" echo [!TIME!] Python executable found:
>> "%LOG_FILE%" echo [!TIME!] %ProgramW6432%\Python313\python.exe

"%ProgramW6432%\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_EXE=%ProgramW6432%\Python313\python.exe"
    >> "%LOG_FILE%" echo [!TIME!] Python %PYTHON_VERSION% accepted from ProgramW6432.
)

if defined PYTHON_EXE goto PYTHON_FOUND

>> "%LOG_FILE%" echo [!TIME!] TEST 7 COMPLETED


:PYTHON_TEST_8


REM ============================================================
REM TEST 8 - Check normal Program Files
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 8 - Checking Program Files

if exist "%ProgramFiles%\Python313\python.exe" goto PYTHON_PROGRAMFILES

>> "%LOG_FILE%" echo [!TIME!] Python not found in Program Files.
>> "%LOG_FILE%" echo [!TIME!] TEST 8 COMPLETED

goto PYTHON_TEST_9


:PYTHON_PROGRAMFILES

>> "%LOG_FILE%" echo [!TIME!] Python executable found:
>> "%LOG_FILE%" echo [!TIME!] %ProgramFiles%\Python313\python.exe

"%ProgramFiles%\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_EXE=%ProgramFiles%\Python313\python.exe"
    >> "%LOG_FILE%" echo [!TIME!] Python %PYTHON_VERSION% accepted from Program Files.
)

if defined PYTHON_EXE goto PYTHON_FOUND

>> "%LOG_FILE%" echo [!TIME!] TEST 8 COMPLETED


:PYTHON_TEST_9


REM ============================================================
REM TEST 9 - Check LocalAppData Python
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 9 - Checking LocalAppData Python

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" goto PYTHON_LOCALAPPDATA

>> "%LOG_FILE%" echo [!TIME!] Python not found in LocalAppData.
>> "%LOG_FILE%" echo [!TIME!] TEST 9 COMPLETED

goto PYTHON_TEST_10


:PYTHON_LOCALAPPDATA

>> "%LOG_FILE%" echo [!TIME!] Python executable found:
>> "%LOG_FILE%" echo [!TIME!] %LOCALAPPDATA%\Programs\Python\Python313\python.exe

"%LOCALAPPDATA%\Programs\Python\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

if not errorlevel 1 (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    >> "%LOG_FILE%" echo [!TIME!] Python %PYTHON_VERSION% accepted from LocalAppData.
)

if defined PYTHON_EXE goto PYTHON_FOUND

>> "%LOG_FILE%" echo [!TIME!] TEST 9 COMPLETED


:PYTHON_TEST_10


REM ============================================================
REM TEST 10 - Check HKCU Python Registry
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 10 - Checking HKCU Python registry

reg query "HKCU\Software\Python\PythonCore\3.13\InstallPath" /ve > "%TEMP_DIR%\python_hkcu.txt" 2>nul

if exist "%TEMP_DIR%\python_hkcu.txt" (

    for /f "tokens=2,*" %%A in (
        "%TEMP_DIR%\python_hkcu.txt"
    ) do (

        if /I "%%A"=="REG_SZ" (

            >> "%LOG_FILE%" echo [!TIME!] HKCU InstallPath: %%B

            if exist "%%Bpython.exe" (

                "%%Bpython.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

                type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

                findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

                if not errorlevel 1 (
                    set "PYTHON_EXE=%%Bpython.exe"
                    >> "%LOG_FILE%" echo [!TIME!] Python %PYTHON_VERSION% accepted from HKCU.
                )

            )

        )

    )

)

if defined PYTHON_EXE goto PYTHON_FOUND

>> "%LOG_FILE%" echo [!TIME!] TEST 10 COMPLETED


REM ============================================================
REM TEST 11 - Check 64-bit HKLM Python Registry
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] TEST 11 - Checking 64-bit HKLM Python registry

reg query "HKLM\SOFTWARE\Python\PythonCore\3.13\InstallPath" /ve /reg:64 > "%TEMP_DIR%\python_hklm.txt" 2>nul

if exist "%TEMP_DIR%\python_hklm.txt" (

    for /f "tokens=2,*" %%A in (
        "%TEMP_DIR%\python_hklm.txt"
    ) do (

        if /I "%%A"=="REG_SZ" (

            >> "%LOG_FILE%" echo [!TIME!] HKLM 64-bit InstallPath: %%B

            if exist "%%Bpython.exe" (

                "%%Bpython.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

                type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

                findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

                if not errorlevel 1 (
                    set "PYTHON_EXE=%%Bpython.exe"
                    >> "%LOG_FILE%" echo [!TIME!] Python %PYTHON_VERSION% accepted from HKLM 64-bit.
                )

            )

        )

    )

)

if defined PYTHON_EXE goto PYTHON_FOUND

>> "%LOG_FILE%" echo [!TIME!] TEST 11 COMPLETED


REM ============================================================
REM Python was not found
REM ============================================================

>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo ==============================================
>> "%LOG_FILE%" echo [!TIME!] PYTHON %PYTHON_VERSION% NOT FOUND
>> "%LOG_FILE%" echo ==============================================
>> "%LOG_FILE%" echo Proceeding to Python download and installation.

goto PYTHON_NOT_FOUND


REM ============================================================
REM Python found
REM ============================================================

:PYTHON_FOUND

>> "%LOG_FILE%" echo.
>> "%LOG_FILE%" echo ==============================================
>> "%LOG_FILE%" echo [!TIME!] PYTHON_FOUND LABEL REACHED
>> "%LOG_FILE%" echo [!TIME!] PYTHON_EXE=!PYTHON_EXE!
>> "%LOG_FILE%" echo ==============================================

call :SetStatus 15 "Python %PYTHON_VERSION% detected"

>> "%LOG_FILE%" echo [!TIME!] STATUS 15 WRITTEN
>> "%LOG_FILE%" echo [!TIME!] Beginning final Python verification

goto FINAL_PYTHON_VERIFICATION


REM ============================================================
REM Python not found - download and install
REM ============================================================

:PYTHON_NOT_FOUND

call :SetStatus 15 "Downloading Python %PYTHON_VERSION%..."

>> "%LOG_FILE%" echo [!TIME!] Starting Python download.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP_DIR%\%PYTHON_INSTALLER%' -UseBasicParsing -ErrorAction Stop } catch { exit 1 }"

if errorlevel 1 goto PythonDownloadFailed

if not exist "%TEMP_DIR%\%PYTHON_INSTALLER%" goto PythonDownloadFailed


call :SetStatus 20 "Installing Python %PYTHON_VERSION%..."

>> "%LOG_FILE%" echo [!TIME!] Starting Python installer.

start /wait "" "%TEMP_DIR%\%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=0 Include_pip=1

set "PYTHON_INSTALL_EXIT=%ERRORLEVEL%"

>> "%LOG_FILE%" echo [!TIME!] Python installer exit code: !PYTHON_INSTALL_EXIT!

timeout /t 3 /nobreak >nul


REM ============================================================
REM Locate Python after installation
REM ============================================================

if exist "%ProgramW6432%\Python313\python.exe" (

    "%ProgramW6432%\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

    type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

    findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

    if not errorlevel 1 (
        set "PYTHON_EXE=%ProgramW6432%\Python313\python.exe"
        >> "%LOG_FILE%" echo [!TIME!] Python installed successfully in ProgramW6432.
    )

)


if not defined PYTHON_EXE if exist "%ProgramFiles%\Python313\python.exe" (

    "%ProgramFiles%\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

    type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

    findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

    if not errorlevel 1 (
        set "PYTHON_EXE=%ProgramFiles%\Python313\python.exe"
        >> "%LOG_FILE%" echo [!TIME!] Python installed successfully in Program Files.
    )

)


if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (

    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

    type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

    findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

    if not errorlevel 1 (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        >> "%LOG_FILE%" echo [!TIME!] Python installed successfully in LocalAppData.
    )

)


if not defined PYTHON_EXE (

    for /f "tokens=2,*" %%A in (
        'reg query "HKLM\SOFTWARE\Python\PythonCore\3.13\InstallPath" /ve /reg:64 2^>nul ^| findstr /I "REG_SZ"'
    ) do (

        if exist "%%Bpython.exe" (

            "%%Bpython.exe" --version > "%TEMP_DIR%\python_check.txt" 2>&1

            type "%TEMP_DIR%\python_check.txt" >> "%LOG_FILE%"

            findstr /C:"Python %PYTHON_VERSION%" "%TEMP_DIR%\python_check.txt" >nul 2>&1

            if not errorlevel 1 (
                set "PYTHON_EXE=%%Bpython.exe"
                >> "%LOG_FILE%" echo [!TIME!] Python installed successfully from registry.
            )

        )

    )

)


if not defined PYTHON_EXE (
    call :SetStatus 100 "ERROR: Python installer completed but Python could not be located."
    goto Failed
)

call :SetStatus 23 "Python installation process completed"



REM ============================================================
REM Final Python verification
REM ============================================================

:FINAL_PYTHON_VERIFICATION

call :SetStatus 24 "Verifying Python %PYTHON_VERSION%..."

>> "%LOG_FILE%" echo [!TIME!] STATUS 24 WRITTEN
>> "%LOG_FILE%" echo [!TIME!] Python verification starting.
>> "%LOG_FILE%" echo [!TIME!] PYTHON_EXE=!PYTHON_EXE!

if not defined PYTHON_EXE (
    call :SetStatus 100 "ERROR: Python could not be located."
    goto Failed
)


REM ============================================================
REM Verify Python version
REM ============================================================

"%PYTHON_EXE%" --version > "%TEMP_DIR%\python_version.txt" 2>&1

type "%TEMP_DIR%\python_version.txt" >> "%LOG_FILE%"

if errorlevel 1 (
    call :SetStatus 100 "ERROR: Python could not be started."
    goto Failed
)

"%PYTHON_EXE%" -c "import sys; sys.exit(0 if sys.version_info[:3] == (3,13,14) else 1)" >nul 2>&1

if errorlevel 1 (
    call :SetStatus 100 "ERROR: UIDetect requires Python 3.13.14."
    goto Failed
)


REM ============================================================
REM Verify / Repair pip
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] Checking Python pip.

"%PYTHON_EXE%" -m pip --version >> "%LOG_FILE%" 2>&1

if not errorlevel 1 (
    >> "%LOG_FILE%" echo [!TIME!] pip is already available.
    goto PIP_VERIFIED
)


REM ============================================================
REM pip not available - repair using ensurepip
REM ============================================================

>> "%LOG_FILE%" echo [!TIME!] pip is not available.
>> "%LOG_FILE%" echo [!TIME!] Attempting to install pip using ensurepip.

call :SetStatus 25 "Installing Python pip..."

"%PYTHON_EXE%" -m ensurepip --upgrade >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    >> "%LOG_FILE%" echo [!TIME!] ensurepip failed.
    call :SetStatus 100 "ERROR: Python pip could not be installed."
    goto Failed
)


REM ============================================================
REM Verify pip after ensurepip
REM ============================================================

:PIP_VERIFIED

"%PYTHON_EXE%" -m pip --version >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    call :SetStatus 100 "ERROR: Python pip is not available."
    goto Failed
)

>> "%LOG_FILE%" echo [!TIME!] pip verification successful.

call :SetStatus 27 "Python %PYTHON_VERSION% and pip verified"

>> "%LOG_FILE%" echo [!TIME!] STATUS 27 WRITTEN
>> "%LOG_FILE%" echo [!TIME!] PYTHON CHECK COMPLETED SUCCESSFULLY


REM =================================================
REM Check / Install Ollama
REM =================================================

call :SetStatus 30 "Checking Ollama installation"

>> "%OLLAMA_DEBUG_LOG%" echo.
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================
>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] OLLAMA INSTALLATION STAGE STARTED
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================

set "OLLAMA_EXE="

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Checking Ollama from PATH

for /f "delims=" %%A in ('where ollama 2^>nul') do (
    if not defined OLLAMA_EXE (
        set "OLLAMA_EXE=%%A"
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found in PATH: %%A
    )
)

if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found in LocalAppData
)

if not defined OLLAMA_EXE if exist "%ProgramFiles%\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%ProgramFiles%\Ollama\ollama.exe"
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found in Program Files
)


REM =================================================
REM Ollama Not Found - Download Installer
REM =================================================

if not defined OLLAMA_EXE (

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama executable NOT FOUND
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama installer download required

    call :SetStatus 35 "Downloading Ollama..."

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Starting Ollama installer download
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Source: %OLLAMA_URL%
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Destination: %TEMP_DIR%\%OLLAMA_INSTALLER%

    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Invoke-WebRequest -Uri '%OLLAMA_URL%' -OutFile '%TEMP_DIR%\%OLLAMA_INSTALLER%'"

    set "OLLAMA_DOWNLOAD_EXIT=!ERRORLEVEL!"

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama download exit code: !OLLAMA_DOWNLOAD_EXIT!

    if not "!OLLAMA_DOWNLOAD_EXIT!"=="0" (
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - Ollama installer download failed
        goto OllamaDownloadFailed
    )

    if not exist "%TEMP_DIR%\%OLLAMA_INSTALLER%" (
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - Ollama installer file not found after download
        goto OllamaDownloadFailed
    )

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama installer download completed successfully
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Installer file exists: %TEMP_DIR%\%OLLAMA_INSTALLER%

    call :SetStatus 40 "Installing Ollama..."

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Starting Ollama installation
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Installer: %TEMP_DIR%\%OLLAMA_INSTALLER%

    "%TEMP_DIR%\%OLLAMA_INSTALLER%" /VERYSILENT /NORESTART /SUPPRESSMSGBOXES

    set "OLLAMA_INSTALL_EXIT=!ERRORLEVEL!"

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama installer exit code: !OLLAMA_INSTALL_EXIT!

    if not "!OLLAMA_INSTALL_EXIT!"=="0" (
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - Ollama installation failed
        goto OllamaInstallFailed
    )

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama installer completed successfully

    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%ProgramFiles%\Ollama;%PATH%"

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Updated PATH for Ollama

    timeout /t 3 /nobreak >nul

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Waiting period after Ollama installation completed

    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found after installation in LocalAppData
    )

    if not defined OLLAMA_EXE if exist "%ProgramFiles%\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%ProgramFiles%\Ollama\ollama.exe"
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found after installation in Program Files
    )

    if not defined OLLAMA_EXE (
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Checking PATH again for Ollama
        for /f "delims=" %%A in ('where ollama 2^>nul') do (
            if not defined OLLAMA_EXE (
                set "OLLAMA_EXE=%%A"
                >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama found through PATH after installation: %%A
            )
        )
    )
)


REM =================================================
REM Verify Ollama Installation
REM =================================================

if not defined OLLAMA_EXE (
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - Ollama could not be located after installation
    call :SetStatus 100 "ERROR: Ollama could not be located after installation."
    goto Failed
)

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama executable: !OLLAMA_EXE!
>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Verifying Ollama version

"%OLLAMA_EXE%" --version > "%TEMP_DIR%\ollama_version_check.txt" 2>&1

set "OLLAMA_VERSION_EXIT=!ERRORLEVEL!"

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama version command exit code: !OLLAMA_VERSION_EXIT!

if exist "%TEMP_DIR%\ollama_version_check.txt" (
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama version output:
    type "%TEMP_DIR%\ollama_version_check.txt" >> "%OLLAMA_DEBUG_LOG%"
)

if not "!OLLAMA_VERSION_EXIT!"=="0" (
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - Ollama installation verification failed
    call :SetStatus 100 "ERROR: Ollama installation could not be verified."
    goto Failed
)

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama installation verified successfully

call :SetStatus 45 "Ollama installation verified"


REM =================================================
REM Check Ollama Server
REM =================================================

call :SetStatus 48 "Checking Ollama server"

>> "%OLLAMA_DEBUG_LOG%" echo.
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================
>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] OLLAMA SERVER CHECK STARTED
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================

"%OLLAMA_EXE%" list >nul 2>&1

if errorlevel 1 (

    call :SetStatus 50 "Starting Ollama server..."

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama server is not responding
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Starting Ollama server

    start "" /min "%OLLAMA_EXE%" serve

    set "OLLAMA_READY=0"

    for /L %%A in (1,1,20) do (

        timeout /t 2 /nobreak >nul

        "%OLLAMA_EXE%" list >nul 2>&1

        if not errorlevel 1 (
            set "OLLAMA_READY=1"
            goto OllamaServerReady
        )

        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Waiting for Ollama server - attempt %%A of 20
        call :SetStatus 50 "Waiting for Ollama server..."

    )

    if "!OLLAMA_READY!"=="0" goto OllamaServerFailed
)

:OllamaServerReady

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] OLLAMA SERVER READY

call :SetStatus 55 "Ollama server is ready"


REM =================================================
REM Check / Download Qwen 2.5 3B
REM =================================================

>> "%OLLAMA_DEBUG_LOG%" echo.
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================
>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] AI MODEL CHECK STARTED
>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Required model: %OLLAMA_MODEL%
>> "%OLLAMA_DEBUG_LOG%" echo ==============================================

call :SetStatus 58 "Checking AI model %OLLAMA_MODEL%..."

"%OLLAMA_EXE%" list > "%TEMP_DIR%\ollama_model_list.txt" 2>&1

set "OLLAMA_LIST_EXIT=!ERRORLEVEL!"

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama list exit code: !OLLAMA_LIST_EXIT!

if exist "%TEMP_DIR%\ollama_model_list.txt" (
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Current Ollama models:
    type "%TEMP_DIR%\ollama_model_list.txt" >> "%OLLAMA_DEBUG_LOG%"
)

"%OLLAMA_EXE%" list | findstr /I /C:"%OLLAMA_MODEL%" >nul 2>&1

if errorlevel 1 (

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] %OLLAMA_MODEL% NOT FOUND
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Model download is required

    call :SetStatus 60 "Downloading AI model %OLLAMA_MODEL%..."

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Starting %OLLAMA_MODEL% download
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Ollama command: ollama pull %OLLAMA_MODEL%

    >> "%QWEN_DOWNLOAD_LOG%" echo.
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo QWEN DOWNLOAD STARTED
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo Time: %DATE% %TIME%
    >> "%QWEN_DOWNLOAD_LOG%" echo Model: %OLLAMA_MODEL%
    >> "%QWEN_DOWNLOAD_LOG%" echo Status: DOWNLOAD_STARTED
    >> "%QWEN_DOWNLOAD_LOG%" echo.

    "%OLLAMA_EXE%" pull %OLLAMA_MODEL% >> "%QWEN_DOWNLOAD_LOG%" 2>&1

    set "MODEL_PULL_EXIT=!ERRORLEVEL!"

    >> "%QWEN_DOWNLOAD_LOG%" echo.
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo QWEN DOWNLOAD PROCESS FINISHED
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo Exit code: !MODEL_PULL_EXIT!
    >> "%QWEN_DOWNLOAD_LOG%" echo Finished: %DATE% %TIME%

    if "!MODEL_PULL_EXIT!"=="0" (
        >> "%QWEN_DOWNLOAD_LOG%" echo Status: DOWNLOAD_COMPLETED
    ) else (
        >> "%QWEN_DOWNLOAD_LOG%" echo Status: DOWNLOAD_FAILED
    )

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Model pull process exit code: !MODEL_PULL_EXIT!

    if not "!MODEL_PULL_EXIT!"=="0" (
        >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] ERROR - %OLLAMA_MODEL% download failed
        goto ModelDownloadFailed
    )

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] %OLLAMA_MODEL% download completed successfully

) else (

    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] %OLLAMA_MODEL% already exists
    >> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] Model download skipped

    >> "%QWEN_DOWNLOAD_LOG%" echo.
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo QWEN MODEL CHECK
    >> "%QWEN_DOWNLOAD_LOG%" echo ==============================================
    >> "%QWEN_DOWNLOAD_LOG%" echo Time: %DATE% %TIME%
    >> "%QWEN_DOWNLOAD_LOG%" echo Model: %OLLAMA_MODEL%
    >> "%QWEN_DOWNLOAD_LOG%" echo Status: MODEL_ALREADY_INSTALLED
    >> "%QWEN_DOWNLOAD_LOG%" echo Download: SKIPPED
)

call :SetStatus 70 "AI model %OLLAMA_MODEL% is ready"

>> "%OLLAMA_DEBUG_LOG%" echo [!TIME!] AI MODEL READY


REM =================================================
REM Test Ollama + Qwen
REM =================================================

call :SetStatus 72 "Testing AI model communication..."

"%OLLAMA_EXE%" run %OLLAMA_MODEL% "Reply with exactly: UIDETECT_TEST_OK" >nul 2>&1

if errorlevel 1 goto ModelTestFailed

call :SetStatus 75 "AI model communication verified"


REM =================================================
REM Check / Install UIDetect Python Dependencies
REM =================================================

call :SetStatus 78 "Checking UIDetect Python dependencies..."

if not exist "%~dp0requirements.txt" goto RequirementsFailed

REM -------------------------------------------------
REM Install dependencies
REM -------------------------------------------------

call :SetStatus 80 "Installing UIDetect Python dependencies..."

"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt" >> "%LOG_FILE%" 2>&1

if errorlevel 1 goto PythonDependenciesFailed

call :SetStatus 88 "UIDetect Python dependencies installed"


REM =================================================
REM Verify UIDetect Python Environment
REM =================================================

call :SetStatus 90 "Verifying UIDetect Python environment..."

"%PYTHON_EXE%" -c "import flask; import flask_cors; import requests; import dotenv; import whois; import ollama; print('UIDETECT_ENV_OK')" >> "%LOG_FILE%" 2>&1

if errorlevel 1 goto PythonEnvironmentFailed

call :SetStatus 93 "Python environment verified"


REM =================================================
REM Verify Python Ollama Client
REM =================================================

call :SetStatus 95 "Testing UIDetect Ollama connection..."

"%PYTHON_EXE%" -c "import ollama; ollama.list()" >> "%LOG_FILE%" 2>&1

if errorlevel 1 goto PythonOllamaFailed

call :SetStatus 98 "UIDetect Ollama connection verified"




REM =================================================
REM Installation Complete
REM =================================================

call :SetStatus 100 "UIDetect installation completed successfully."

if "%INSTALLER_MODE%"=="1" (
    exit /b 0
)

echo.
echo ==============================================
echo UIDetect installation completed successfully.
echo ==============================================
echo.
echo All required components have been installed.
echo.
echo Please follow the system instruction below to continue.
echo.

pause
endlocal
exit /b 0


REM =================================================
REM Status Function
REM =================================================

:SetStatus

set "STATUS_PERCENT=%~1"
set "STATUS_MESSAGE=%~2"

REM -------------------------------------------------
REM Write status to a temporary file first.
REM This prevents the frontend from competing with
REM the BAT while the main status file is being written.
REM -------------------------------------------------

set "STATUS_TEMP_FILE=%STATUS_FILE%.tmp"

> "%STATUS_TEMP_FILE%" echo %STATUS_PERCENT%^|%STATUS_MESSAGE%

REM -------------------------------------------------
REM Replace the main status file.
REM -------------------------------------------------

move /Y "%STATUS_TEMP_FILE%" "%STATUS_FILE%" >nul 2>&1

if "%INSTALLER_MODE%"=="0" (
    echo [%STATUS_PERCENT%%%] %STATUS_MESSAGE%
)

exit /b 0


REM =================================================
REM Error Handlers
REM =================================================

:PythonDownloadFailed
call :SetStatus 100 "ERROR: Failed to download Python from Python.org."
goto Failed

:OllamaDownloadFailed
call :SetStatus 100 "ERROR: Failed to download the official Ollama installer."
goto Failed

:OllamaInstallFailed
call :SetStatus 100 "ERROR: Ollama installation failed."
goto Failed

:OllamaServerFailed
call :SetStatus 100 "ERROR: Ollama server did not respond."
goto Failed

:ModelDownloadFailed
call :SetStatus 100 "ERROR: Unable to download %OLLAMA_MODEL%."
goto Failed

:ModelTestFailed
call :SetStatus 100 "ERROR: Ollama failed to run %OLLAMA_MODEL%."
goto Failed

:RequirementsFailed
call :SetStatus 100 "ERROR: requirements.txt was not found."
goto Failed

:PythonDependenciesFailed
call :SetStatus 100 "ERROR: UIDetect Python dependencies could not be installed."
goto Failed

:PythonEnvironmentFailed
call :SetStatus 100 "ERROR: UIDetect Python environment verification failed."
goto Failed

:PythonOllamaFailed
call :SetStatus 100 "ERROR: UIDetect could not communicate with Ollama through Python."
goto Failed

:Failed

if "%INSTALLER_MODE%"=="1" (
    exit /b 1
)

echo.
echo ==============================================
echo UIDetect installation FAILED.
echo ==============================================
echo.
echo Please check the error above.
echo.

pause
endlocal
exit /b 1