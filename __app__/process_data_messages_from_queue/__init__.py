import os
import io
import requests
import json
import logging

import azure.functions as func

from __app__.blob import write_lotus_url_data_to_blob
import traceback




async def main(msg: func.ServiceBusMessage):
    try:
        msg_as_txt = msg.get_body().decode('utf-8')
        logging.info('Python ServiceBus queue trigger processed message:\n%s', msg_as_txt)
        try:
            message = json.loads(msg_as_txt)
            url = message['url']
            name = message['target_blob']

        except (ValueError, KeyError) as e:
            logging.warning(f'Message mal formed: {e} {message}')
            raise


        logging.info('Object at: %s', url)

        await write_lotus_url_data_to_blob(url, name)

        logging.info(f"Wrote to blob: {name}")

    except:
        logging.error(traceback.format_exc())
        traceback.print_exc()
        raise
