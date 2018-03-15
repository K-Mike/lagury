import multiprocessing as mp
import threading
from tqdm import tqdm
from typing import Callable, Any, Dict, Iterable


class EmptyObject:
    def __getattr__(self, item):
        return lambda *args, **kwargs: None


def _chunks_generator(iterable, chunk_size):
    """Yield successive chunks from iterable"""
    chunk = []

    for item in iterable:
        chunk.append(item)

        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

    # return the last smaller chunk if available
    if chunk:
        yield chunk


def _producer_wrapper(task: Callable, in_queue: mp.JoinableQueue, out_queue: mp.JoinableQueue,
                      out_chunk_size: int, kwargs: Dict[str, Any]):
    result_chunk = []

    while True:
        job_chunk = in_queue.get()

        if job_chunk is None:
            # don't forget partially completed chunk
            if result_chunk:
                out_queue.put(result_chunk)

            in_queue.task_done()
            return

        for job in job_chunk:
            result = task(job, **kwargs)

            if result is None:
                continue

            result_chunk.append(result)

            if len(result_chunk) == out_chunk_size:
                out_queue.put(result_chunk)
                result_chunk = []

        in_queue.task_done()


def _consumer_wrapper(task: Callable, queue: mp.JoinableQueue, kwargs: Dict[str, Any]):
    while True:
        job_chunk = queue.get()

        if job_chunk is None:
            queue.task_done()
            return

        for job in job_chunk:
            task(job, **kwargs)

        queue.task_done()


def many_producers_single_consumer(producer_task: Callable, consumer_task: Callable, jobs: Iterable,
                                   producer_kwargs: Dict[str, Any]=None, consumer_kwargs: Dict[str, Any]=None,
                                   producer_queue_size=10, consumer_queue_size=10,
                                   producer_chunk_size=1, consumer_chunk_size=1,
                                   producers_num=1, show_progress=False):
    """
    Generic implementation of producer-consumer pattern with additional features: producers intended to be heavily
    computational functions launched as separate processes while consumer is a single-threaded lightweight aggregation
    task running in the main process (via threading).

    No jobs should be None. The producer_task can return None - this result meant to be ignored and not passed to the
    consumer.

    For payload balancing the jobs can be combined in chunks:
    1. From main thread to producer processes - via producer_chunk_size.
    2. From producer processes to a consumer thread - via consumer_chunk_size.
    """
    producer_kwargs = producer_kwargs or {}
    consumer_kwargs = consumer_kwargs or {}

    producer_queue = mp.JoinableQueue(producer_queue_size)
    consumer_queue = mp.JoinableQueue(consumer_queue_size)

    consumer_thread = threading.Thread(target=_consumer_wrapper,
                                       args=(consumer_task, consumer_queue, consumer_kwargs))
    consumer_thread.start()

    progress_bar = tqdm() if show_progress else EmptyObject()

    with mp.Pool(processes=producers_num, initializer=_producer_wrapper,
                 initargs=(producer_task, producer_queue, consumer_queue, consumer_chunk_size, producer_kwargs)):

        for job_chunk in _chunks_generator(jobs, producer_chunk_size):
            producer_queue.put(job_chunk)
            progress_bar.update(len(job_chunk))

        for _ in range(producers_num):
            producer_queue.put(None)

        producer_queue.join()

    consumer_queue.put(None)
    consumer_queue.join()
    consumer_thread.join()

    progress_bar.close()
