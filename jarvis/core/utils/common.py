from threading import Thread


def threadify(func, *args, **kwargs):
    """
    start 'fuc' as thread with *args and **kwargs
    """
    thread = Thread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread
