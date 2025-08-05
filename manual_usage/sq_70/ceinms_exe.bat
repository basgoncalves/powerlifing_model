@echo off
setlocal

rem Get the directory of the current script
set "SCRIPT_DIR=%~dp0"

echo Script directory is: "%SCRIPT_DIR%"

cd /d "%SCRIPT_DIR%"

rem Set CEINMS_EXE_DIR to two directories up plus code\executables
set "CEINMS_EXE_DIR=%SCRIPT_DIR%..\..\..\..\code\executables"

rem Paths to CEINMS calibration executable and setup file
set "CEINMS_EXE=%CEINMS_EXE_DIR%\CEINMS.exe"
set "EXE_SETUP=%SCRIPT_DIR%\setup_ceinms_exe.xml"

if not exist "%CEINMS_EXE%" (
    echo Error: CEINMS calibration executable not found at "%CEINMS_EXE%"
    exit /b 1
)

if not exist "%EXE_SETUP%" (
    echo Error: CEINMS calibration setup file not found at "%EXE_SETUP%"
    exit /b 1
)


rem Find the outputDirectory line in the setup file and extract the path
for /f "tokens=3 delims=<>" %%a in ('findstr /i "<outputDirectory>" "%EXE_SETUP%"') do (
    set "OUTPUT_DIR=%%a"
)

rem If OUTPUT_DIR was found, check if it exists and create it if not
if defined OUTPUT_DIR (
    echo Found output directory: %OUTPUT_DIR%
    if not exist "%OUTPUT_DIR%" (
        echo Output directory does not exist. Creating it...
        mkdir "%OUTPUT_DIR%"
        if errorlevel 1 (
            echo Failed to create directory: "%OUTPUT_DIR%"
            exit /b 1
        )
    )
) else (
    echo Warning: Could not find <outputDirectory> tag in "%EXE_SETUP%".
)

rem Construct and display the command
set "COMMAND="%CEINMS_EXE%" -S "%EXE_SETUP%""
echo Running command: %COMMAND%

rem Run the command
%COMMAND%

rem Check the exit code of the last command
if %errorlevel% neq 0 (
    echo Error running CEINMS execution.
    exit /b %errorlevel%
)

endlocal
