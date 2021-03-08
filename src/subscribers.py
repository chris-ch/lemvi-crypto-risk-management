import json
import base64
import os
from typing import Dict

from google.cloud.functions import Context
from msgstore import FieldStoreFile


def store_file(event: Dict, context: Context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """

    print("""This Function was triggered by messageId {} published at {}""".format(context.event_id, context.timestamp))

    if "data" not in event:
        return

    message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    filename = message[FieldStoreFile.FILENAME]
    content = message[FieldStoreFile.CONTENT]
    bucket_name = message[FieldStoreFile.BUCKET_NAME]


    print("Hello {}!".format(message))
