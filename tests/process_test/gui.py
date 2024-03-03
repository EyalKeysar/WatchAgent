import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from process_manager import ProcessManager

class AppGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CPU Consuming Processes")
        self.root.geometry("800x600")

        self.tree = ttk.Treeview(self.root, style="Custom.Treeview")
        self.tree["columns"] = ("PID", "Name", "Status", "CPU %", "Num Threads", "Memory (MB)")
        self.tree.heading("#0", text="", anchor=ctk.W)
        self.tree.heading("PID", text="PID", anchor=ctk.W)
        self.tree.heading("Name", text="Name", anchor=ctk.W)
        self.tree.heading("Status", text="Status", anchor=ctk.W)
        self.tree.heading("CPU %", text="CPU %", anchor=ctk.W)
        self.tree.heading("Num Threads", text="Num Threads", anchor=ctk.W)
        self.tree.heading("Memory (MB)", text="Memory (MB)", anchor=ctk.W)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Custom.Treeview", highlightthickness=0, bd=0, font=('Arial', 10))
        style.configure("Custom.Treeview.Heading", font=('Arial', 10, 'bold'))

        # Add a vertical scrollbar to the window
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        
        # Configure treeview to use the scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure treeview to adjust column widths
        for column in ("PID", "Name", "Status", "CPU %", "Num Threads", "Memory (MB)"):
            self.tree.column(column, width=100, minwidth=50, anchor=ctk.W)

        self.tree.bind("<Button-3>", self.kill_process)
        self.tree.pack(expand=True, fill=ctk.BOTH)

        for column in ("PID", "Name", "Status", "CPU %", "Num Threads", "Memory (MB)"):
            self.tree.heading(column, text=column, anchor=ctk.W, command=lambda col=column: self.sort_treeview(col))

    def sort_treeview(self, column):
        # Toggle sorting direction
        current_heading = self.tree.heading(column, "text")
        descending = False
        if current_heading.endswith(" ▼"):
            descending = True

        # Remove sorting indicators from all columns
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        # Sort the data
        data = [(self.tree.set(child, column), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=descending)
        except ValueError:
            data.sort(reverse=descending)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

        # Update the column heading text with sorting indicator
        if descending:
            self.tree.heading(column, text=column + " ▲")
        else:
            self.tree.heading(column, text=column + " ▼")

    def show_processes(self):
        all_processes = ProcessManager.get_processes()
        self._update_processes(all_processes)

    def _update_processes(self, all_processes):
        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        parent_processes = {}  # Dictionary to store parent processes and their corresponding subprocesses

        for p, cpu_percent in all_processes:
            try:
                parent_pid = p.ppid()  # Get the parent process ID
                if parent_pid not in parent_processes:
                    parent_processes[parent_pid] = []  # Initialize list for subprocesses of this parent
                parent_processes[parent_pid].append((p, cpu_percent))  # Add subprocess to the list of subprocesses of this parent
            except:
                pass

        for parent_pid, subprocesses in parent_processes.items():
            try:
                parent_process = ProcessManager.get_process_by_id(parent_pid)  # Get the parent process
                with parent_process.oneshot():
                    parent_item = self.tree.insert("", "end", text="", values=(parent_process.pid, parent_process.name(), parent_process.status(), f'{parent_process.cpu_percent():.2f}%', parent_process.num_threads(), f'{parent_process.memory_info().rss / 1e6:.3f}'))
            except:
                continue

            # Add subprocesses as children of their parent process
            for subprocess, cpu_percent in subprocesses:
                try:
                    with subprocess.oneshot():
                        self.tree.insert(parent_item, "end", text="", values=(subprocess.pid, "    " + subprocess.name(), subprocess.status(), f'{cpu_percent:.2f}%', subprocess.num_threads(), f'{subprocess.memory_info().rss / 1e6:.3f}'))
                except:
                    continue

        self.root.mainloop()

    def kill_process(self, event):
        item = self.tree.selection()[0]
        pid = self.tree.item(item, "values")[0]
        ProcessManager.kill_process(self.tree, pid)
