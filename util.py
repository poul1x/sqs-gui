from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional
import functools
import random
import string
import os


class TimeMeasure:

    start_time: Optional[datetime]
    finish_time: Optional[datetime]
    elapsed: Optional[timedelta]

    def __init__(self):
        self.start_time = None
        self.finish_time = None
        self.elapsed = None

    @contextmanager
    def measuring(self):

        try:
            self.start_time = datetime.utcnow()
            yield

        finally:
            self.finish_time = datetime.utcnow()
            self.elapsed = self.finish_time - self.start_time


def rfc3339(date: datetime) -> str:
    return date.replace(microsecond=0).isoformat() + "Z"


def rfc3339_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def random_string(n: int):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))