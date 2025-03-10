@echo off
REM Run as Administrator
setlocal
set SCRIPT_DIR=%~dp0
set TASK_NAME="Uproject Autoshortcut"
set BATCH_FILE="%SCRIPT_DIR%run_daemon.bat"

REM Check elevation
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~f0' -Verb RunAs"
    exit /b
)

REM Create XML template
set XML_TEMP=%TEMP%\task_template.xml
(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo ^<RegistrationInfo^>
echo ^<Description^>Manages Unreal Engine project shortcuts in Start Menu^</Description^>
echo ^</RegistrationInfo^>
echo ^<Triggers^>
echo ^<LogonTrigger^>
echo ^<Enabled^>true^</Enabled^>
echo ^</LogonTrigger^>
echo ^</Triggers^>
echo ^<Principals^>
echo ^<Principal id="Author"^>
echo ^<RunLevel^>HighestAvailable^</RunLevel^>
echo ^</Principal^>
echo ^</Principals^>
echo ^<Settings^>
echo ^<Hidden^>true^</Hidden^>
echo ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
echo ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
echo ^<AllowHardTerminate^>true^</AllowHardTerminate^>
echo ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo ^<AllowStartOnDemand^>true^</AllowStartOnDemand^>
echo ^<IdleSettings^>
echo ^<StopOnIdleEnd^>false^</StopOnIdleEnd^>
echo ^</IdleSettings^>
echo ^</Settings^>
echo ^<Actions Context="Author"^>
echo ^<Exec^>
echo ^<Command^>cmd.exe^</Command^>
echo ^<Arguments^>/c "%BATCH_FILE%"^</Arguments^>
echo ^</Exec^>
echo ^</Actions^>
echo ^</Task^>
) > "%XML_TEMP%"

REM Create task
schtasks /Create /TN %TASK_NAME% /XML "%XML_TEMP%" /F
del "%XML_TEMP%"

if %ERRORLEVEL% EQU 0 (
    echo Task created successfully!
    echo You can verify in Task Scheduler (taskschd.msc)
) else (
    echo Failed to create task. Check administrator permissions.
)

endlocal