from enum import Enum


class FieldStoreFile(Enum):
    CONTENT = 'content'
    NAMESPACE = 'namespace'


class FieldStoreKind(Enum):
    SOURCE = 'Source'
    EXCHANGE = 'Exchange'
    OPERATION = 'Operation'

class TopicId(Enum):
    JOB_ORDER_DATA_IMPORT = 'job-order-data-import'
    JOB_WALLET_DATA_IMPORT = 'job-wallet-data-import'
