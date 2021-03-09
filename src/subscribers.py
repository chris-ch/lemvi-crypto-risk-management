import json
import base64
from google.cloud import logging

from typing import Dict

from google.cloud import datastore
from msgstore import FieldStoreFile, FieldStoreKind


def store_file(event: Dict, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Example event:
    {
    "data": {
            "Operation": "abcd",
            "Source": "abcd",
            "Exchange": "abcd",
            "namespace": "xyz",
            "content": {"data1": "dummy"}
        }
    }

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    logging_client = logging.Client()
    logger = logging_client.logger('store_file')
    if 'data' not in event:
        return

    logger.log_text('loading message')
    message = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    content = message[FieldStoreFile.CONTENT.value]
    namespace = message[FieldStoreFile.NAMESPACE.value]
    source = message[FieldStoreKind.SOURCE.value]
    exchange = message[FieldStoreKind.EXCHANGE.value]
    operation_key = message[FieldStoreKind.OPERATION.value]

    client = datastore.Client(namespace=namespace)

    with client.transaction():
        source_key = client.key(FieldStoreKind.SOURCE.value, source)
        exchange_key = client.key(FieldStoreKind.EXCHANGE.value, exchange, parent=source_key)
        entity = datastore.Entity(key=client.key(FieldStoreKind.OPERATION.value, operation_key, parent=exchange_key))
        entity.update(content)
        client.put(entity)

    logger.log_text('saved entity using key {}={}/{}={}/{}={}'.format(FieldStoreKind.SOURCE.value, source, FieldStoreKind.EXCHANGE.value, exchange, FieldStoreKind.OPERATION.value, operation_key))
