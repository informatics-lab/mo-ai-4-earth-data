import azure.functions as func
from enum import Enum
import json
from unittest.mock import MagicMock, patch
from typing import Any
import copy
import pytest
import __app__
import os

TEST_MSG = {'metadata': {'cell_methods': 'time: maximum (interval: 1 hour)',
                         'created_time': '2019-12-13T12:10:54Z',
                         'forecast_period': '172800',
                         'forecast_period_bounds': '169200 172800',
                         'forecast_period_units': 'seconds',
                         'forecast_reference_time': '2019-12-13T10:00:00Z',
                         'height': '10.0',
                         'height_units': 'm',
                         'name': 'wind_speed_of_gust',
                         'realization': '15 16 17',
                         'time': '2019-12-15T10:00:00Z'},
            'object_size': 4378232,
            'url': 'https://blah.com/datasets/mo-atmospheric-mogreps-uk/objects/bGV2ZWxf'}
TARGET_MODEL = 'mo-atmospheric-mogreps-uk'
TARGET_DEST = f'{TARGET_MODEL}/20191213T1000Z/20191215T1000Z-PT0048H00M-wind_gust_at_10m-PT01H.nc'


class MsgType(Enum):
    NOTIFICATION = "Notification",
    SUB_CONFIRMATION = "SubscriptionConfirmation"


def make_message(msg_type: MsgType = MsgType.NOTIFICATION, message: Any = None) -> bytes:
    msg = {'Type': msg_type.value, 'TopicArn': "arn:made:up"}
    message = message if message else {'hello': 'world'}

    if msg_type == MsgType.SUB_CONFIRMATION:
        msg['SubscribeURL'] = "https://subscribe-here"

    msg['Message'] = json.dumps(message)
    return json.dumps(msg, sort_keys=True).encode('utf-8')


async def run_with_message(message, required_diagnostic=True):
    req = func.HttpRequest("GET", "https://dummy.url", body=message)

    msg_mock = MagicMock()
    async def send_message(msg, q):
        msg_mock(msg, q)

    with patch("__app__.incoming_msg_handler.send_message", send_message) as mock:
        with patch('__app__.incoming_msg_handler.required_diagnostic') as filter_func:
            filter_func.return_value = required_diagnostic
            await __app__.incoming_msg_handler.main(req)

    return msg_mock

@pytest.mark.asyncio
async def test_subscribe_message_adds_to_sub_queue():
    
    message = make_message(MsgType.SUB_CONFIRMATION)
    msg_queue_mock = await run_with_message(message)

    assert json.dumps(msg_queue_mock.call_args[0][0]).encode('utf-8') == message
    assert msg_queue_mock.call_args[0][1] == os.environ['SUBSCRIBE_QUEUE_NAME']
    assert msg_queue_mock.call_count == 1



@pytest.mark.asyncio
async def test_notification_message_adds_to_data_queue():
    
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    

    msg_queue_mock = await run_with_message(message)
    
    assert msg_queue_mock.call_count == 1
    assert msg_queue_mock.call_args[0][1] == os.environ['DATA_QUEUE_NAME']



@pytest.mark.asyncio
async def test_retains_metadata_and_url():
    
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    
    msg_queue_mock = await run_with_message(message)
    sent_msg = msg_queue_mock.call_args[0][0]

    for k, v in TEST_MSG['metadata'].items():
        assert sent_msg['metadata'][k] == v

    assert sent_msg['url'] == TEST_MSG['url']

@pytest.mark.asyncio
async def test_adds_model():
    
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    
    msg_queue_mock = await run_with_message(message)
    sent_msg = msg_queue_mock.call_args[0][0]

    assert sent_msg['metadata']['model'] == TARGET_MODEL


@pytest.mark.asyncio
async def test_adds_filename():
    
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    msg_queue_mock = await run_with_message(message)
    
    target = json.loads(json.loads(message)['Message'])['metadata']
    target['model'] = 'mo-atmospheric-mogreps-uk'

    sent_msg =  msg_queue_mock.call_args[0][0]
    assert sent_msg['target_blob'] == TARGET_DEST 


@pytest.mark.asyncio
async def test_filters():
    
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)

    msg_queue_mock = await run_with_message(message, False)

    assert msg_queue_mock.call_count == 0


    msg_queue_mock = await run_with_message(message, True)

    assert msg_queue_mock.call_count == 1