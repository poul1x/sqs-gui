from base64 import b64encode, b85decode, b85encode
import os
from pyexpat.errors import messages
from queue import Queue
from threading import Thread
from typing import List, Optional

from black import sys

from .receiver import Message

try:
    import ujson as json  # type: ignore
except ModuleNotFoundError:
    import json


class MessageDiskStorage:

    """Saves received messages on disk"""

    _queue: Queue
    _workdir: str
    _thread: Thread
    _shutdown: bool

    def __init__(self, queueName: str) -> None:
        self._thread = Thread(target=self._storageThread, daemon=True)
        self._workdir = self.getDataDir(queueName)
        os.makedirs(self._workdir, exist_ok=True)
        self._shutdown = False
        self._queue = Queue()

    def getDataDir(self, queueName: str):

        appName = "SqsGui"
        home = os.path.expanduser("~")

        if sys.platform == "win32":
            appDataPath = os.path.join(home, "AppData", "Roaming")
        elif sys.platform == "linux":
            appDataPath = os.path.join(home, ".local", "share")
        elif sys.platform == "darwin":
            appDataPath = os.path.join(home, "Library", "Application Support")
        else:
            raise ValueError("Unsupported platform")

        return os.path.join(appDataPath, appName, queueName)

    def saveMessage(self, message: Message):
        self._queue.put(message)

    def startReceivingJobs(self):
        self._thread.start()

    def stopReceivingJobs(self):
        self._queue.put(None)

    def abortPendingJobs(self):
        self._shutdown = True
        self.waitPendingJobsDone()

    def waitPendingJobsDone(self):
        self.stopReceivingJobs()
        self._thread.join()

    def hasUnfinishedJobs(self):
        return self._thread.is_alive() and not self._queue.empty()

    @staticmethod
    def serialize(message: Message) -> str:

        if message.attributes is not None:
            for data in message.attributes.values():
                if data["DataType"] == "Binary":
                    data["BinaryValue"] = b85encode(data["BinaryValue"]).decode()

        return json.dumps(message.dict())

    @staticmethod
    def deserialize(data: str) -> Message:

        message = Message.parse_obj(json.loads(data))

        if message.attributes is not None:
            for data in message.attributes.values():
                if data["DataType"] == "Binary":
                    data["BinaryValue"] = b85decode(data["BinaryValue"]).decode()

        return message

    def _storageThread(self):

        while not self._shutdown:

            message: Optional[Message] = self._queue.get()
            if message is None or self._shutdown:
                break

            filepath = os.path.join(self._workdir, message.id)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.serialize(message))

    def loadMessages(self) -> List[Message]:

        messages = []

        def loadMessage(data: str):
            try:
                messages.append(self.deserialize(data))
            except Exception as e:
                print(f"Error - {e}")

        for filename in os.listdir(self._workdir):
            filepath = os.path.join(self._workdir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                loadMessage(f.read())

        return messages
