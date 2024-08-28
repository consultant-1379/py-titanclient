import os
import re
import hashlib
import uuid as _uuid

from functools import wraps, reduce
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor, as_completed

class LenientNamespace(SimpleNamespace):

    def __getattribute__(self, attribute):
        try:
            return super().__getattribute__(attribute.lower())
        except AttributeError:
            return None


def retry(n, callback=lambda v: v is v):

    def func_wrapper(func):
        @wraps(func)
        def args_wrapper(*args, **kwargs):
            for i in range(0, n):
                val = func(*args, **kwargs)
                if not callback(val):
                    continue
                else:
                    break
            if callback(val):
                return val
            else:
                raise ValueError("all retry callbacks failed")
        return args_wrapper

    return func_wrapper


def tmap(func, items):

    results = {}
    idlist = []

    with ThreadPoolExecutor() as e:

        futures = []

        for i in items:
            f = e.submit(func, i)
            idlist.append(id(f))
            results[id(f)] = None
            futures.append(f)

        for f in as_completed(futures):
            results[id(f)] = f.result()

    return [results[i] for i in idlist]


def defattr(object, name):
    return hasattr(object, name) and getattr(object, name)


def uuid(seed):
    m = hashlib.md5()
    if seed:
        m.update(str(seed).encode('utf-8'))
    return str(_uuid.UUID(m.hexdigest()))

def list_files(path, regex):
	files = []
	rx = re.compile(regex)
	for name in os.listdir(path):
		if rx.search(name):
			files.append(os.path.join(path, name))
	return files
