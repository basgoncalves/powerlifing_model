@echo off
REM Print OpenSim version
echo Checking OpenSim version...
opensim-cmd -V

pause

SET "TRIAL_DIR=%~dp0"
SET "IK_SETUP=%TRIAL_DIR%setup_IK.xml"
echo Trial directory is: "%TRIAL_DIR%"
echo IK setup file is: "%IK_SETUP%"
pause

opensim-cmd run-tool "%IK_SETUP%"