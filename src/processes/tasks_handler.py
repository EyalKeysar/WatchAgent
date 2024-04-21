import os
import sys

class Task:
    '''
    Task class is responsible for creating a task object
    '''
    def __init__(self, name, pid, session_name, session_num, memory_usage):
        self.name = name
        self.pid = pid
        self.session_name = session_name
        self.session_num = session_num
        self.memory_usage = memory_usage

    def __str__(self):
        return f"Name: {self.name}, PID: {self.pid}, Session Name: {self.session_name}, Session Num: {self.session_num}, Memory Usage: {self.memory_usage}"
    
    def __repr__(self):
        return f"Task({self.name}, {self.pid}, {self.session_name}, {self.session_num}, {self.memory_usage})"

class TaskHandler:
    '''
    TaskHandler class is responsible for handling the os tasks (processes)
    '''
    def __init__(self, task):
        self.task = task

    def get_tasks(self):
        '''
        get_tasks method is responsible for getting the tasks
        '''
        try:
            # Get the list of tasks
            tasks = os.popen('tasklist').read()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
        # make it Task objects
        task_list = []
        for task in tasks.split('\n')[3:-1]:
            task_info = task.split()
            task_list.append(Task(task_info[0], task_info[1], task_info[2], task_info[3], task_info[4]))

        return task_list
        

if __name__ == '__main__':
    task_handler = TaskHandler('tasklist')
    tasks = task_handler.get_tasks()
    print(tasks)
