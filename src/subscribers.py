import json
import base64
import logging

from typing import Dict

from google.cloud import datastore
from msgstore import FieldStoreFile


def store_file(event: Dict, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Example event:
    {
    "data": {
            "filename": "abcd",
            "buket-name": "xyz",
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
    if "data" not in event:
        return

    message = json.loads(base64.b64decode(event["data"]).decode('utf-8'))

    filename = message[FieldStoreFile.FILENAME.value]
    content = message[FieldStoreFile.CONTENT.value]
    namespace = message[FieldStoreFile.NAMESPACE.value]
    source = message[FieldStoreFile.SOURCE.value]
    exchange = message[FieldStoreFile.EXCHANGE.value]

    client = datastore.Client(namespace=namespace)

    with client.transaction():
        entity = datastore.Entity(key=client.key(FieldStoreFile.SOURCE.value, source, FieldStoreFile.EXCHANGE.value, exchange, FieldStoreFile.FILENAME.value, filename))
        entity.update(content)
        client.put(entity)

    logging.info('saved entity using key {}={}/{}={}/{}={}'.format(FieldStoreFile.SOURCE.value, source, FieldStoreFile.EXCHANGE.value, exchange, FieldStoreFile.FILENAME.value, filename))
