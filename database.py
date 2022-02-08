
from PyQt5.QtSql import QSqlDatabase
con = QSqlDatabase.addDatabase("QSQLITE")
con.setDatabaseName("C:\\a.db") # Temporary database
con.close()


class MQDump:

    def save(self, filepath):
        pass

    def load(self, filepath):
        pass

    def add(self, msg):
        pass

    def list(self):
        pass

    def filter(self, conditions):
        raise NotImplementedError()

# Database = queue name

# Messages
# message_id: - globally unique
# md5_of_body: str
# body: str
# md5_of_message_attributes: str
# receipt_handle: VARCHAR(1024)

# MessageAttributes
# message_id: str
# name
# type

# MessageStringAttributes
# message_id: str
# name: VARCHAR(255)
# value: TEXT

# MessageBinaryAttributes
# message_id: str       -\
# name: VARCHAR(255)    - unique
# value: BLOB

# MessageStringListAttributes
# message_id: str
# order: int
# name: VARCHAR(255)
# value: TEXT

# MessageBinaryListAttributes
# message_id: str
# order: int
# name: VARCHAR(255)
# value: BLOB

# MessageSystemAttributes
# "AWSTraceHeader", str
# "ApproximateFirstReceiveTimestamp", str
# "ApproximateReceiveCount", str
# "MessageDeduplicationId", str
# "MessageGroupId", str
# "SenderId", str
# "SentTimestamp", str
# "SequenceNumber", str