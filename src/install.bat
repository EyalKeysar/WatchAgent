py watchagent.py install
py watchagent.py start
py screen_share.py start
@REM sc config WatchAgentService start=auto
echo "Installed WatchAgent service."

@REM start powershell.exe -WindowStyle Hidden -File "./watchdog.ps1"
@REM echo "Started Watchdog."

@REM powershell.exe ./watchdog.ps1