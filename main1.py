import sys
import os
import time
import psutil
import customtkinter as ctk
from tkinter import ttk

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

    top_list = sorted(top.items(), key=lambda x: x[1])
    top_list.reverse()

    return top_list

def show_processes():
    # create a CTk window to display processes
    root = ctk.CTk()
    root.title("CPU Consuming Processes")
    root.geometry("800x600")

    # create a treeview with a vertical scrollbar
    tree = ttk.Treeview(root, style="Custom.Treeview", yscrollcommand=lambda *args: root.yview(*args))
    tree["columns"] = ("PID", "Name", "Status", "CPU %", "Num Threads", "Memory (MB)")
    tree.heading("#0", text="", anchor=ctk.W)
    tree.heading("PID", text="PID", anchor=ctk.W, command=lambda: sort_treeview("PID"))
    tree.heading("Name", text="Name", anchor=ctk.W, command=lambda: sort_treeview("Name"))
    tree.heading("Status", text="Status", anchor=ctk.W, command=lambda: sort_treeview("Status"))
    tree.heading("CPU %", text="CPU %", anchor=ctk.W, command=lambda: sort_treeview("CPU %"))
    tree.heading("Num Threads", text="Num Threads", anchor=ctk.W, command=lambda: sort_treeview("Num Threads"))
    tree.heading("Memory (MB)", text="Memory (MB)", anchor=ctk.W, command=lambda: sort_treeview("Memory (MB)"))

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Custom.Treeview", highlightthickness=0, bd=0, font=('Arial', 10))
    style.configure("Custom.Treeview.Heading", font=('Arial', 10, 'bold'))

    def sort_treeview(column):
        # Toggle sorting direction
        current_heading = tree.heading(column, "text")
        if current_heading.endswith(" ▼"):
            descending = False
        else:
            descending = True

        # Remove sorting indicators from all columns
        for col in tree["columns"]:
            tree.heading(col, text=col)

        # Sort the data
        data = [(tree.set(child, column), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=descending)
        except ValueError:
            data.sort(reverse=descending)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)

        # Update the column heading text with sorting indicator
        if descending:
            tree.heading(column, text=column + " ▼")
        else:
            tree.heading(column, text=column + " ▲")

    all_processes = get_processes()
    for p, cpu_percent in all_processes:
        try:
            with p.oneshot():
                tree.insert("", "end", text="", values=(p.pid, p.name(), p.status(), f'{cpu_percent:.2f}%', p.num_threads(), f'{p.memory_info().rss / 1e6:.3f}'))
        except Exception as e:
            pass

    # add a vertical scrollbar to the window
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    # configure treeview to use the scrollbar
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(expand=True, fill=ctk.BOTH)

    root.mainloop()

def main():
    while True:
        show_processes()
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    main()
