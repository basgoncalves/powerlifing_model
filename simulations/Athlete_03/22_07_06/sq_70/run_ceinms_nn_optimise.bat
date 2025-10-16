@echo off
setlocal

rem Get the directory of the current script
set "SCRIPT_DIR=%~dp0"
set "CODE_DIR=%SCRIPT_DIR%..\..\..\..\code"
set "EXECUTABLES_DIR=%CODE_DIR%\executables"

rem Change working directory to the directory containing the calibration setup file
pushd "%SCRIPT_DIR%"

rem Paths to CEINMS calibration executable and setup file
set "CEINMS_EXE=%EXECUTABLES_DIR%\CEINMSoptimise.exe"
set "SETUP_XML=%SCRIPT_DIR%setup_ceinms_optimise.xml"

if not exist "%CEINMS_EXE%" (
    echo Error: executable not found at "%CEINMS_EXE%"
    exit /b 1
)

if not exist "%SETUP_XML%" (
    echo Error: setup file not found at "%SETUP_XML%"
    exit /b 1
)

rem Find the outputDirectory line in the setup file and extract the path
for /f "tokens=3 delims=<>" %%a in ('findstr /i "<outputDirectory>" "%SETUP_XML%"') do (
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
    echo Warning: Could not find <outputDirectory> tag in "%SETUP_XML%".
)

rem Construct and display the command
set "COMMAND="%CEINMS_EXE%" -S "%SETUP_XML%""
set "LOG_FILE=%OUTPUT_DIR%\optimise.log"
echo Running command: %COMMAND%

rem Run the command
%COMMAND% > "%LOG_FILE%" 2>&1

rem Check the exit code of the last command
if %errorlevel% neq 0 (
    echo Error running CEINMS optimise.
    exit /b %errorlevel%
)

endlocal
