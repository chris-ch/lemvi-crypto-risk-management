from enum import Enum


class FieldStoreFile(Enum):
    FILENAME = 'filename'
    CONTENT = 'content'
    BUCKET_NAME = 'bucket-name'


class TopicId(Enum):
    JOB_ORDER_DATA_IMPORT = 'job-order-data-import'
    JOB_WALLET_DATA_IMPORT = 'job-wallet-data-import'
