import logging
import json
import os
import traceback

import azure.functions as func
from azure.servicebus import Message

from __app__.messaging import send_message
from __app__.util import determine_blob_name
from __app__.vendor.data_filter import required_diagnostic

def get_model(message):
    models = ['mo-atmospheric-ukv', 'mo-atmospheric-global', 'mo-atmospheric-mogreps-g', 'mo-atmospheric-mogreps-uk']
    for model in models:
        if message['url'].find(model) >= 0:
            return model
    else:
        raise ValueError(f"No model found in message {message}")

async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')
        

        msg_type = None
        message = None
        try:
            message = req.get_json()
            logging.info(f'Incoming message: {message}')
            msg_type = message.get('Type')
            logging.info(f'Of type {msg_type}')
        except (ValueError, KeyError):
            pass

        
        if msg_type == "SubscriptionConfirmation":
            logging.info(f'Send message subscribe')
            await send_message(message, os.environ["SUBSCRIBE_QUEUE_NAME"])
            logging.info(f'Sent message subscribe')
        else:
            try:
                data_msg_in = json.loads(message['Message'])
                metadata = data_msg_in['metadata']
                metadata['model'] = get_model(data_msg_in)
                blob_dest =  determine_blob_name(metadata)
                data_msg_in['target_blob'] = blob_dest
                required = required_diagnostic(blob_dest)
                logging.info(f"Message interoperated; Required = {required}, blob_dest={blob_dest}")
            except (KeyError, ValueError) as e:
                logging.warning(f"{e}, exception processing message. {message}")
                return func.HttpResponse(f"Message malformed or missing.", status_code=400)

            if required:
                data_queue = os.environ["DATA_QUEUE_NAME"]
                await send_message(data_msg_in, data_queue)
                logging.info(f"Message {data_msg_in} sent to {data_queue}")
            else: 
                logging.info(f"Skip {blob_dest} as diagnostic no required")


        logging.info(f'Precessing complete.')
    except:
        logging.error("Uncaught exception occurred. Stack trace to follow")
        logging.error(traceback.format_exc())
        raise

    return func.HttpResponse(f"Processed message type {msg_type}.")
