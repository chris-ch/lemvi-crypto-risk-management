from enum import Enum


class FieldStoreFile(Enum):
    FILENAME = 'filename'
    CONTENT = 'content'
    NAMESPACE = 'namespace'
    SOURCE = 'source'
    EXCHANGE = 'exchange'


class TopicId(Enum):
    JOB_ORDER_DATA_IMPORT = 'job-order-data-import'
    JOB_WALLET_DATA_IMPORT = 'job-wallet-data-import'
