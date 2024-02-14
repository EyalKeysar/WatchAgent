import sys
import os
import time
import psutil
import tkinter as tk
from tkinter import ttk

def get_processes():
    # get all running processes and sort by CPU percentage
    processes = []
    for proc in psutil.process_iter():
        with proc.oneshot():
            pid = proc.pid
            name = proc.name()
            cpu_percent = proc.cpu_percent(interval=0.001)
            memory_percent = proc.memory_percent()
            processes.append((pid, name, cpu_percent, memory_percent))

    # sort processes by CPU percentage
    processes.sort(key=lambda x: x[2], reverse=True)
    return processes

def show_processes():
    # create a Tkinter window to display processes
    root = tk.Tk()
    root.title("Running Processes")

    # create a treeview with a vertical scrollbar
    tree = ttk.Treeview(root, yscrollcommand=lambda *args: root.yview(*args))
    tree["columns"] = ("PID", "Name", "CPU %", "Memory %")
    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("PID", text="PID", anchor=tk.W)
    tree.heading("Name", text="Name", anchor=tk.W)
    tree.heading("CPU %", text="CPU %", anchor=tk.W)
    tree.heading("Memory %", text="Memory %", anchor=tk.W)

    processes = get_processes()
    for pid, name, cpu_percent, memory_percent in processes:
        tree.insert("", "end", text="", values=(pid, name, cpu_percent, memory_percent))

    # function to sort treeview when column header clicked
    def sort_treeview(column, descending=False):
        data = [(tree.set(child, column), child) for child in tree.get_children('')]
        data.sort(reverse=descending)
        for index, item in enumerate(data):
            tree.move(item[1], '', index)
        tree.heading(column, command=lambda c=col: sort_treeview(c, not descending))

    for col in tree["columns"]:
        tree.heading(col, text=col, command=lambda c=col: sort_treeview(c))

    # add a vertical scrollbar to the window
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')

    # configure treeview to use the scrollbar
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(expand=True, fill=tk.BOTH)

    root.mainloop()

def main():
    while True:
        show_processes()
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    main()
