import os
import io
import requests
import json
import logging

import azure.functions as func

HEADERS = {
    "x-api-key": os.environ['APIKEY']
}


def main(msg: func.ServiceBusMessage, outputblob: func.Out[func.InputStream]):
    msg_as_txt = msg.get_body().decode('utf-8')
    logging.info('Python ServiceBus queue trigger processed message: %s', msg_as_txt)
    try:
        message = json.loads(msg_as_txt)
        url = message['url']

    except (ValueError, KeyError) as e:
        logging.warning(f'Message mal formed: {e} {message}')
        raise

    logging.info('object at: %s', url)

    raw_bytes = requests.get(url, headers=HEADERS).content
    logging.info(f"Write to blob")
    outputblob.set(io.BytesIO(raw_bytes))
