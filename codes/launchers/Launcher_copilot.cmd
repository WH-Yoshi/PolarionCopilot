@echo off
set PORT1=22027
set PORT2=22028
set SSH_COMMAND="ssh -N -f -p 22002 user@idaho-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000"

rem Check if PORT1 is open (listening or established)
netstat -an | findstr /i ":%PORT1%.*LISTENING" >nul
if %ERRORLEVEL% equ 0 (
  set PORT1_STATUS=0
) else (
  set PORT1_STATUS=1
)

rem Check if PORT2 is open (listening or established)
netstat -an | findstr /i ":%PORT2%.*LISTENING" >nul
if %ERRORLEVEL% equ 0 (
  set PORT2_STATUS=0
) else (
  set PORT2_STATUS=1
)

rem If either port is closed, run the SSH command in a new terminal
if %PORT1_STATUS% neq 0 (
  %SSH_COMMAND%
  if %ERRORLEVEL% equ 0 (
    echo SSH command successful.
  ) else (
    echo Error: SSH command failed with exit code %ERRORLEVEL%.
  )
) else if %PORT2_STATUS% neq 0 (
  %SSH_COMMAND%
  if %ERRORLEVEL% equ 0 (
    echo SSH command successful. Leave the terminal open.
  ) else (
    echo Error: SSH command failed with exit code %ERRORLEVEL%.
  )
)

py .\codes\before_code.py
py .\codes\Copilot.py