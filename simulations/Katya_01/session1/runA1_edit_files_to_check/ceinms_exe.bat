@echo off
setlocal

rem Get the directory of the current script
set "SCRIPT_DIR=%~dp0"

rem Change the current working directory to the script's directory
cd /d "%SCRIPT_DIR%"

rem Paths to CEINMS calibration executable and setup file
set "CEINMS_EXE_DIR=%SCRIPT_DIR%..\..\..\..\code\executables"
set "CEINMS_EXE=%CEINMS_EXE_DIR%\CEINMS.exe"
set "EXE_SETUP=%SCRIPT_DIR%setup_ceinms.xml"

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
set CEINMS_EXIT_CODE=%errorlevel%

rem Check the exit code
if %CEINMS_EXIT_CODE% neq 0 (
    echo Error running CEINMS execution.
    exit /b %CEINMS_EXIT_CODE%
) else (
    echo CEINMS execution completed successfully.
)

echo Output files should be in the specified output directory: "%OUTPUT_DIR%"

endlocal
