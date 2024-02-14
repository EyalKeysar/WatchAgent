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
        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_processes = ProcessManager.get_processes()
        for p, cpu_percent in all_processes:
            try:
                with p.oneshot():
                    self.tree.insert("", "end", text="", values=(p.pid, p.name(), p.status(), f'{cpu_percent:.2f}%', p.num_threads(), f'{p.memory_info().rss / 1e6:.3f}'))
            except Exception as e:
                pass

        self.root.mainloop()

    def kill_process(self, event):
        item = self.tree.selection()[0]
        pid = self.tree.item(item, "values")[0]
        ProcessManager.kill_process(self.tree, pid)
