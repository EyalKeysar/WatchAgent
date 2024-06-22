import psutil

def update_usage(serverapi, logging):
    if serverapi.is_authenticated and serverapi.is_connected:
        for proc in psutil.process_iter():
            start_time = proc.create_time()
            serverapi.update_program_usage(proc.name(), str(int(start_time)))
        logging.debug("Usage updated")