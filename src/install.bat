py watchagent.py install
py watchagent.py start
sc config WatchAgentService start=auto
echo "Installed WatchAgent service."