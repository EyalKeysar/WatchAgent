py watchagent.py install
py watchagent.py start
@REM sc config WatchAgentService start=auto
echo "Installed WatchAgent service."

start powershell.exe -WindowStyle Hidden -File "./watchdog.ps1"
echo "Started Watchdog."

@REM powershell.exe ./watchdog.ps1