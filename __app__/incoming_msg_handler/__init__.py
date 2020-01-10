import logging
import json

import azure.functions as func


def process_subscription(msg_body, msg_out):
    msg_out.set(json.dumps(msg_body))
    logging.info(f"Visit {msg_body['SubscribeURL']} to subscribe to {msg_body['TopicArn']}")


def process_data_msg(msg_body, msg_out):
    msg_out.set(json.dumps(msg_body))
    logging.info("Got data message...", msg_body)


def get_model(message):
    models = ['mo-atmospheric-ukv', 'mo-atmospheric-global', 'mo-atmospheric-mogreps-g', 'mo-atmospheric-mogreps-uk']
    for model in models:
        if message['url'].find(model) >= 0:
            return model
    else:
        raise ValueError(f"No model found in message {message}")


def make_object_key_root(meta):

    base = f"{meta['model']}/{meta['name']}"
    if meta.get('cell_methods', False):
        base += f"-{meta['cell_methods']}"
    if meta.get('height', False):
        if (len(meta['height'].strip().split(' ')) > 1):
            base += '-at_heights'
        else:
            base += '-'+meta['height'].strip()+meta['height_units'].strip()
    if meta.get('pressure', False) and (len(meta['pressure'].strip().split(' ')) > 1):
        base += '-at_pressures'

    return base


def main(req: func.HttpRequest, datamsg: func.Out[str], submsg: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    msg_type = None
    message = None
    try:
        message = req.get_json()
        msg_type = message.get('Type')
    except (ValueError, KeyError):
        pass

    if msg_type == "SubscriptionConfirmation":
        process_subscription(message, submsg)
    else:
        try:
            data_msg_in = json.loads(message['Message'])
            metadata = data_msg_in['metadata']
            metadata['model'] = get_model(data_msg_in)
            path = [make_object_key_root(metadata),
                    metadata['forecast_reference_time'],
                    metadata['forecast_period']]
            data_msg_in['file_dest'] = '/'.join(path) + '.nc'
        except (KeyError, ValueError) as e:
            logging.warning(f"{e}, exception processing message. {message}")
            return func.HttpResponse(f"Message malformed or missing.", status_code=400)

        process_data_msg(data_msg_in, datamsg)

    return func.HttpResponse(f"processed message type {msg_type}")
