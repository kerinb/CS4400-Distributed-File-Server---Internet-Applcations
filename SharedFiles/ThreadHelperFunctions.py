from threading import Thread
import Queue as queue


class MyThread(Thread):
    def __init__(self, queue_of_tasks):
        self.tasks = queue_of_tasks
        self.on = True
        Thread.__init__(self)
        self.start()  # start the thread

    def run(self):
        while self.on:
            funcs, args, kargs = self.tasks.get()
            self.on = funcs(*args, **kargs)


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
        for i in range(0, self.num_of_threads):
            self.add_task(False)
            self.threads[i].join()

    def add_task(self, task, *args, **kargs):
        self.queue.put(task, args, kargs)
