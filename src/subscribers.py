import io
import json
import base64
import logging

from typing import Dict

from google.cloud import storage
from google.cloud.functions import Context
from msgstore import FieldStoreFile


def store_file(event: Dict, context: Context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Example data:
    {
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

    message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    filepath = message[FieldStoreFile.FILENAME]
    path_items = filepath.split('/')
    filename = path_items[-1]
    file_prefix = '/'.join(path_items[:-1])
    content = message[FieldStoreFile.CONTENT]
    bucket_name = message[FieldStoreFile.BUCKET_NAME]

    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name, prefix=file_prefix, delimiter='/')
    if len([blob for blob in blobs if blob.name == filename]) > 0:
        logging.error('file "{}" already found in bucket'.format(filepath))
        return

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filepath)
    blob.upload_from_file(io.StringIO(content))
