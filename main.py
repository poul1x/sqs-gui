from dataclasses import dataclass
from queue import Queue
from socket import timeout
from threading import Lock, Thread
from time import sleep
from typing import List, Optional, Set
import boto3
import os

from mypy_boto3_sqs.client import SQSClient
from mypy_boto3_sqs.service_resource import (
    SQSServiceResource,
    Queue as SQSQueue,
    Message,
)

from botocore.exceptions import ClientError
from util import TimeMeasure, random_string

from concurrent.futures import ThreadPoolExecutor, wait

QUEUE_TEST = os.environ["MQ_QUEUE_TEST1"]

# def ping(self):
#     try:
#         self._client.list_queues(MaxResults=1)
#     except (ClientConnectionError, ClientError) as e:
#         raise ChannelError(str(e)) from e


@dataclass
class ReceiveConditions:

    all: bool
    """Receive all messages"""

    count: int
    """Receive at least N messages"""

    timeout: int
    """Receive messages until timeout expiration"""


@dataclass
class Credentials:
    access_key: int
    secret_key: int
    region_name: str
    endpoint_url: Optional[str]


def send_many_messages(n: int, credentials: Credentials):

    session = boto3.Session()
    sqs: SQSServiceResource = session.resource(
        service_name="sqs",
        region_name=credentials.region_name,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
    )

    queue: SQSQueue = sqs.get_queue_by_name(QueueName=QUEUE_TEST)
    queue.purge()

    for _ in range(n):
        queue.send_message(MessageBody=random_string(40))

def receive_message(credentials: Credentials):

    session = boto3.Session()
    sqs: SQSServiceResource = session.resource(
        service_name="sqs",
        region_name=credentials.region_name,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
    )

    queue: SQSQueue = sqs.get_queue_by_name(QueueName=QUEUE_TEST)
    queue.receive_messages(MaxNumberOfMessages=1)


class SQSMessageIterator:

    _lock: Lock
    _shutdown: bool
    _queue_name: str
    _unique_messages: Queue
    _unique_message_ids: set
    _conditions: ReceiveConditions
    _worker_threads: List[Thread]
    _checker_thread: Thread
    _max_num_of_msgs = 10
    _service_name = "sqs"

    def __init__(
        self,
        queue_name: str,
        credentials: Credentials,
        conditions: ReceiveConditions,
        num_workers: Optional[int] = None,
    ):
        if num_workers is None:
            num_workers = (os.cpu_count() or 1) * 5

        if num_workers <= 0:
            raise ValueError("num_workers must be greater than 0")

        self._lock = Lock()
        self._shutdown = False
        self._worker_threads = list()
        self._unique_messages = Queue()
        self._unique_message_ids = set()
        self._checker_thread = Thread(target=self.checker_thread)
        self._conditions = conditions
        self._queue_name = queue_name

        for _ in range(num_workers):
            session = self._create_session(credentials)
            thread = Thread(target=self.worker_thread, args=(session,))
            self._worker_threads.append(thread)

    def __iter__(self):
        self.start_message_receiving()
        return self

    def __next__(self):

        message = self._unique_messages.get()
        if message is not None:
            return message

        self._checker_thread.join()
        raise StopIteration()

    def start_message_receiving(self):

        for thread in self._worker_threads:
            thread.start()

        self._checker_thread.start()

    def _create_session(self, credentials: Credentials):
        return boto3.Session().resource(
            service_name=self._service_name,
            region_name=credentials.region_name,
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            endpoint_url=credentials.endpoint_url,
        )

    def worker_thread(self, sqs: SQSServiceResource):

        """This thread receives messages and puts unique ones into queue"""

        queue: SQSQueue = sqs.get_queue_by_name(
            QueueName=self._queue_name,
        )

        while True:

            # Checker thread signals to exit
            # `Timeout` condition is fulfilled
            if self._shutdown:
                return

            # Receive messages from queue
            # Each received message will be
            # invisible for `timeout` seconds
            messages = queue.receive_messages(
                MaxNumberOfMessages=self._max_num_of_msgs,
                VisibilityTimeout=self._conditions.timeout,
                WaitTimeSeconds=0,
            )

            # No messages left in queue -> exit
            # `All` condition is fulfilled
            if not messages:
                return

            with self._lock:

                for message in messages:

                    # Skip already received message
                    if message.message_id in self._unique_message_ids:
                        continue

                    # Save received message
                    self._unique_message_ids.add(message.message_id)
                    self._unique_messages.put(message)

                # First N messages have been received -> exit
                # `Count` condition is fulfilled
                if not self._conditions.all:
                    if len(self._unique_message_ids) >= self._conditions.count:
                        return

    def checker_thread(self):

        """This thread waits until all worker threads finish"""

        interval = 0.5
        iters = round(self._conditions.timeout / interval)

        for _ in range(iters):
            sleep(interval)
            if all(not th.is_alive() for th in self._worker_threads):
                break

        self._shutdown = True
        for thread in self._worker_threads:
            thread.join()

        self._unique_messages.put(None)


if __name__ == "__main__":

    credentials = Credentials(
        access_key=os.environ["MQ_USERNAME"],
        secret_key=os.environ["MQ_PASSWORD"],
        region_name=os.environ["MQ_REGION"],
        endpoint_url=os.environ["MQ_URL"],
    )

    conditions = ReceiveConditions(
        all=False,
        count=500,
        timeout=2,
    )

    # receive_message(credentials)
    # exit(0)

    send_many_messages(5000, credentials)

    measure = TimeMeasure()
    i = 0
    with measure.measuring():
        msg: Message
        for msg in SQSMessageIterator(QUEUE_TEST, credentials, conditions, 2):
            i += 1

    print("Received - ", i)
    print("Elapsed - ", measure.elapsed.seconds)

