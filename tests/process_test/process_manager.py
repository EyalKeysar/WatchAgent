import psutil
import tkinter.messagebox as messagebox

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
        for p in proc:
            top[p] = p.cpu_percent() / psutil.cpu_count()

        top_list = sorted(top.items(), key=lambda x: x[1], reverse=True)

        return top_list
    
    def get_parent_process(parent_pid):
        return psutil.Process(parent_pid)


    @staticmethod
    def kill_process(tree, pid):
        try:
            p = psutil.Process(int(pid))
            response = messagebox.askyesno("Kill Process", f"Are you sure you want to kill process {p.name()} (PID: {pid})?")
            if response:
                p.terminate()
                # Update the GUI to remove the terminated process
                item = tree.get_children()
                for child in item:
                    if tree.item(child, "values")[0] == pid:
                        tree.delete(child)
                        break
        except psutil.NoSuchProcess:
            messagebox.showwarning("Process Not Found", f"Process with PID {pid} no longer exists.")
