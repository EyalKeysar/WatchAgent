import psutil
import tkinter.messagebox as messagebox
import time
class ProcessManager:
    @staticmethod
    def get_processes():
        # Fetch process data
        proc = []
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
                p.cpu_percent()  # Trigger cpu_percent() for measurement
                proc.append(p)
            except Exception as e:
                pass

        # Sort processes by CPU percentage
        top = {}
        time.sleep(0.1)
        for p in proc:
            top[p] = p.cpu_percent() / psutil.cpu_count()

        top_list = sorted(top.items(), key=lambda x: x[1], reverse=True)

        return top_list

    @staticmethod
    def kill_process(tree, pid):
        try:
            p = psutil.Process(int(pid))
            response = messagebox.askyesno("Kill Process", f"Are you sure you want to kill process {p.name()} (PID: {pid})?")
            if response:
                p.terminate()
                tree.delete(item)
        except psutil.NoSuchProcess:
            messagebox.showwarning("Process Not Found", f"Process with PID {pid} no longer exists.")
