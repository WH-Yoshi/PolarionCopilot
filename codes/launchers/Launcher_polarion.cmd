@echo off
set PORT=22027
set SSH_COMMAND="ssh -N -f -p 41708 user@91.150.160.37 -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080"

rem Check if PORT is open (listening or established)
netstat -an | findstr /i ":%PORT%.*LISTENING" >nul
if %ERRORLEVEL% equ 0 (
    echo Port %PORT% is open on localhost
) else (
    start cmd /c %SSH_COMMAND%
    if %ERRORLEVEL% equ 0 (
        echo SSH command successful.
    ) else (
        echo Error: SSH command failed with exit code %ERRORLEVEL%.
    )
)

py .\codes\before_code.py
py .\codes\Polarion.py