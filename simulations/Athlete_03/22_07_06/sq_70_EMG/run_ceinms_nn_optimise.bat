@echo off
setlocal

rem Get the directory of the current script
set "SCRIPT_DIR=%~dp0"

rem Set CEINMS_EXE_DIR to two directories up plus code\executables
pushd "%SCRIPT_DIR%..\..\..\code\executables"
set "CEINMS_EXE_DIR=%CD%"

rem Paths to CEINMS calibration executable and setup file
set "CEINMS_CAL_EXE=%CEINMS_EXE_DIR%\CEINMSoptimise.exe"
set "CALIBRATION_SETUP=%SCRIPT_DIR%setup_ceinms_optimise.xml"

if not exist "%CEINMS_CAL_EXE%" (
    echo Error: CEINMS calibration executable not found at "%CEINMS_CAL_EXE%"
    exit /b 1
)

if not exist "%CALIBRATION_SETUP%" (
    echo Error: CEINMS calibration setup file not found at "%CALIBRATION_SETUP%"
    exit /b 1
)


rem Find the outputDirectory line in the setup file and extract the path
for /f "tokens=3 delims=<>" %%a in ('findstr /i "<outputDirectory>" "%CALIBRATION_SETUP%"') do (
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
    echo Warning: Could not find <outputDirectory> tag in "%CALIBRATION_SETUP%".
)

rem Construct and display the command
set "COMMAND="%CEINMS_CAL_EXE%" -S "%CALIBRATION_SETUP%""
echo Running command: %COMMAND%

rem Run the command
%COMMAND%

rem Check the exit code of the last command
if %errorlevel% neq 0 (
    echo Error running CEINMS optimise.
    exit /b %errorlevel%
)

endlocal
