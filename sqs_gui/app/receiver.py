from dataclasses import dataclass
from queue import Queue
from threading import Lock, Thread
from time import sleep
from typing import Dict, Iterator, List, Optional, Set
import boto3
import os

from pydantic import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_sqs.client import SQSClient
    from mypy_boto3_sqs.service_resource import (
        SQSServiceResource,
        Message as SQSMessage,
        Queue as SQSQueue,
    )
else:
    SQSServiceResource = object
    SQSMessage = object
    SQSQueue = object

from .util import random_string

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
    """Receive at least N messages, then stop"""

    timeout: int
    """Receive messages until timeout expiration"""


class Message(BaseModel):
    id: str
    body: str
    md5OfBody: str
    attributes: Optional[Dict[str, dict]]
    md5OfAttributes: Optional[str]
    sysAttributes: Dict[str, str]
    receiptHandle: str


@dataclass
class Credentials:
    access_key: int
    secret_key: int
    region_name: str
    endpoint_url: Optional[str]


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
        msg_ids_exclude = set(),
    ):
        if num_workers is None:
            num_workers = os.cpu_count() or 2

        if num_workers <= 0:
            raise ValueError("num_workers must be greater than 0")

        self._lock = Lock()
        self._shutdown = False
        self._worker_threads = list()
        self._unique_messages = Queue()
        self._unique_message_ids = msg_ids_exclude
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
                MessageAttributeNames=["All"],
                AttributeNames=["All"],
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
                    saved_msg = Message(
                        id=message.message_id,
                        body=message.body,
                        md5OfBody=message.md5_of_body,
                        attributes=message.message_attributes,
                        md5OfAttributes=message.md5_of_message_attributes,
                        sysAttributes=message.attributes,
                        receiptHandle=message.receipt_handle,
                    )

                    self._unique_message_ids.add(saved_msg.id)
                    self._unique_messages.put(saved_msg)

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


def receiveMessages(
    queue_name: str,
    credentials: Credentials,
    conditions: ReceiveConditions,
    num_workers: Optional[int] = None,
    msg_ids_exclude = set(),
) -> Iterator[Message]:

    return SQSMessageIterator(
        queue_name,
        credentials,
        conditions,
        num_workers,
        msg_ids_exclude,
    )


def sendMessages(queue_name: str, n: int, credentials: Credentials):

    session = boto3.Session()
    sqs: SQSServiceResource = session.resource(
        service_name="sqs",
        region_name=credentials.region_name,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
    )

    queue: SQSQueue = sqs.get_queue_by_name(QueueName=queue_name)

    for i in range(n):
        queue.send_message(MessageBody=f"message-{i}-{random_string(10)}")
