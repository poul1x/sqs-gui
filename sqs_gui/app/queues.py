from dataclasses import dataclass
from enum import Enum
import queue
import stat
from typing import Dict, List, Optional
from datetime import datetime
from winsound import MessageBeep
from .receiver import Credentials
import boto3


@dataclass
class QueueAttributes:
    numMessages: Optional[str]
    numMessagesDelayed: Optional[str]
    numMessagesNotVisible: Optional[str]
    contentBasedDeduplication: Optional[str]
    createdTimestamp: Optional[str]
    deduplicationScope: Optional[str]
    delaySeconds: Optional[str]
    fifoQueue: Optional[str]
    fifoThroughputLimit: Optional[str]
    kmsDataKeyReusePeriodSeconds: Optional[str]
    kmsMasterKeyId: Optional[str]
    lastModifiedTimestamp: Optional[str]
    maximumMessageSize: Optional[str]
    messageRetentionPeriod: Optional[str]
    policy: Optional[str]
    queueArn: Optional[str]
    receiveMessageWaitTimeSeconds: Optional[str]
    redriveAllowPolicy: Optional[str]
    redrivePolicy: Optional[str]
    sqsManagedSseEnabled: Optional[str]
    visibilityTimeout: Optional[str]


@dataclass
class QueueInfo:
    url: str
    name: str
    numMessages: str
    dumpDate: datetime
    tags: Dict[str, str]
    attributes: Dict[str, str]


class QueueType(str, Enum):
    STANDARD = "Standard queue"
    DLQ = "Dead Letter Queue"
    FIFO = "FIFO Queue"
    FIFO_DLQ = "FIFO Queue"


from mypy_boto3_sqs.client import SQSClient
from mypy_boto3_sqs.service_resource import (
    SQSServiceResource,
    Queue as SQSQueue,
    Message,
)


class MessageQueue:

    _queue: SQSQueue
    _queue_name: str
    _service_name = "sqs"
    _sqs: SQSServiceResource

    def __init__(self, queue: SQSQueue):
        self._queue_name = self._get_queue_name(queue)
        self._queue = queue

    @property
    def name(self) -> str:
        return self._queue_name

    @staticmethod
    def _get_queue_name(queue: SQSQueue):
        return queue.attributes["QueueArn"].split(":")[-1]

    def _get_queue_tags(self) -> Dict[str, str]:
        client: SQSClient = self._queue.meta.client
        resp: dict = client.list_queue_tags(QueueUrl=self._queue.url)
        return resp.get("Tags", dict())

    # def _get_queue_type(self, sourceQueues: list) -> str:

    #     hasSourceQueues = len(sourceQueues) != 0
    #     isFifoQueue = self._queue_name.endswith(".fifo")

    #     if isFifoQueue:
    #         part1 = "FIFO"
    #     else:
    #         part1 = "Standard"

    #     if hasSourceQueues:
    #         part2 = "DLQ"
    #     else:
    #         part2 = "queue"

    #     return f"{part1} {part2}"

    def _get_queue_attributes(self):

        url = self._queue.url
        client: SQSClient = self._queue.meta.client
        resp = client.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])
        attrs = resp["Attributes"]

        return {
            "ApproximateNumberOfMessages":attrs.get("ApproximateNumberOfMessages", "<Unknown>"),
            "ApproximateNumberOfMessagesDelayed":attrs.get("ApproximateNumberOfMessagesDelayed", "<Unknown>"),
            "ApproximateNumberOfMessagesNotVisible":attrs.get("ApproximateNumberOfMessagesNotVisible", "<Unknown>"),
            "ContentBasedDeduplication":attrs.get("ContentBasedDeduplication", "<Unknown>"),
            "CreatedTimestamp":attrs.get("CreatedTimestamp", "<Unknown>"),
            "DeduplicationScope":attrs.get("DeduplicationScope", "<Unknown>"),
            "DelaySeconds":attrs.get("DelaySeconds", "<Unknown>"),
            "FifoQueue":attrs.get("FifoQueue", "<Unknown>"),
            "FifoThroughputLimit":attrs.get("FifoThroughputLimit", "<Unknown>"),
            "KmsDataKeyReusePeriodSeconds":attrs.get("KmsDataKeyReusePeriodSeconds", "<Unknown>"),
            "KmsMasterKeyId":attrs.get("KmsMasterKeyId", "<Unknown>"),
            "LastModifiedTimestamp":attrs.get("LastModifiedTimestamp", "<Unknown>"),
            "MaximumMessageSize":attrs.get("MaximumMessageSize", "<Unknown>"),
            "MessageRetentionPeriod":attrs.get("MessageRetentionPeriod", "<Unknown>"),
            "Policy":attrs.get("Policy", "<Unknown>"),
            "QueueArn":attrs.get("QueueArn", "<Unknown>"),
            "ReceiveMessageWaitTimeSeconds":attrs.get("ReceiveMessageWaitTimeSeconds", "<Unknown>"),
            "RedriveAllowPolicy":attrs.get("RedriveAllowPolicy", "<Unknown>"),
            "RedrivePolicy":attrs.get("RedrivePolicy", "<Unknown>"),
            "SqsManagedSseEnabled":attrs.get("SqsManagedSseEnabled", "<Unknown>"),
            "VisibilityTimeout":attrs.get("VisibilityTimeout", "<Unknown>"),
        }

    @staticmethod
    def _get_queue_name(queue: SQSQueue):
        return queue.attributes.get("QueueArn", ":<Unknown>").split(":")[-1]

    @staticmethod
    def _current_date():
        return datetime.now().replace(microsecond=0, second=0).isoformat()

    def info(self):

        attributes = self._get_queue_attributes()
        numMessages = attributes["ApproximateNumberOfMessages"]

        return QueueInfo(
            url=self._queue.url,
            name=self._queue_name,
            numMessages=numMessages,
            attributes=attributes,
            dumpDate=self._current_date(),
            tags=self._get_queue_tags(),
        )


SERVICE_NAME = "sqs"


def list_message_queues(credentials: Credentials):

    session = boto3.Session()
    sqs: SQSServiceResource = session.resource(
        service_name=SERVICE_NAME,
        region_name=credentials.region_name,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
    )

    return [MessageQueue(queue) for queue in sqs.queues.all()]
