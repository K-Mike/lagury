import multiprocessing as mp
import threading
from tqdm import tqdm
from typing import Callable, Any, Dict, Iterable


class EmptyObject:
    def __getattr__(self, item):
        return lambda *args, **kwargs: None


def _producer_wrapper(task: Callable, in_queue: mp.JoinableQueue, out_queue: mp.JoinableQueue, kwargs: Dict[str, Any]):
    while True:
        job = in_queue.get()

        if job is None:
            in_queue.task_done()
            return

        result = task(job, **kwargs)
        out_queue.put(result)
        in_queue.task_done()


def _consumer_wrapper(task: Callable, queue: mp.JoinableQueue, kwargs: Dict[str, Any], show_progress: bool):

    progress_bar = tqdm() if show_progress else EmptyObject()

    while True:
        job = queue.get()
        progress_bar.update(1)

        if job is None:
            queue.task_done()
            return

        task(job, **kwargs)
        queue.task_done()


def many_producers_single_consumer(producer_task: Callable, consumer_task: Callable, jobs: Iterable,
                                   producer_kwargs: Dict[str, Any]=None, consumer_kwargs: Dict[str, Any]=None,
                                   producers_num=1, queue_size=10, show_progress=False):
    """"""
    producer_kwargs = producer_kwargs or {}
    consumer_kwargs = consumer_kwargs or {}

    producer_queue = mp.JoinableQueue(queue_size)
    consumer_queue = mp.JoinableQueue(queue_size)

    consumer_thread = threading.Thread(target=_consumer_wrapper,
                                       args=(consumer_task, consumer_queue, consumer_kwargs, show_progress))
    consumer_thread.start()

    with mp.Pool(processes=producers_num, initializer=_producer_wrapper,
                 initargs=(producer_task, producer_queue, consumer_queue, producer_kwargs)):

        for job in jobs:
            producer_queue.put(job)

        for _ in range(producers_num):
            producer_queue.put(None)

        producer_queue.join()

    consumer_queue.put(None)
    consumer_queue.join()
    consumer_thread.join()
