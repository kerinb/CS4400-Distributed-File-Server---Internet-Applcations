import sys
from threading import Thread

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue


class ListOfThreads:
    def __init__(self, num_of_threads, size_of_queue):
        self.queue = queue.Queue(size_of_queue)
        self.num_of_threads = num_of_threads
        self.threads = []
        for i in range(0, num_of_threads):
            self.threads.append(MyThread(self.queue))

    def wait_for_thread_to_complete(self):
        self.task.join()

    def end_threads(self):
        for i in range(0, self.num):
            self.addTask(False)
        for i in range(0, self.num):
            self.threads[i].join()

    def add_task(self, func, *args, **kargs):
        self.queue.put((func, args, kargs))


class MyThread(Thread):
    def __init__(self, _queue):
        self.tasks = _queue
        self.on = True
        Thread.__init__(self)
        self.start()  # Start thread

    def run(self):
        while self.on:
            func, args, kargs = self.tasks.get()
            self.on = func(*args, **kargs)
