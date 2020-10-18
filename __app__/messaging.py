import os
from azure.servicebus import Message
from azure.servicebus.aio import ServiceBusClient
import json
import logging
import datetime

CONNECTION_STR = os.environ['ServiceBusConnection']
DELAY_HOURS = float(os.environ['DELAY_HOURS'])

async def send_message(msg_body, queue):
    logging.info(f'Send message: {msg_body} to {queue}')
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
    logging.info(servicebus_client)
    async with servicebus_client:
        logging.info('Create message')
        enqueue_dt = datetime.datetime.utcnow() + datetime.timedelta(hours=DELAY_HOURS)
        message = Message(json.dumps(msg_body), scheduled_enqueue_time_utc=enqueue_dt)
        logging.info('Message created')
        sender = servicebus_client.get_queue_sender(queue_name=queue)
        async with sender:
            logging.info(f'Do Send...')
            await sender.send_messages(message)
            logging.info(f'Sent!')