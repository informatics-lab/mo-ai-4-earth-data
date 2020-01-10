from __app__ import incoming_msg_handler
import azure.functions as func
from enum import Enum
import json
from unittest.mock import MagicMock
from typing import Any
import copy


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


class MsgType(Enum):
    NOTIFICATION = "Notification",
    SUB_CONFIRMATION = "SubscriptionConfirmation"


def make_message(msg_type: MsgType = MsgType.NOTIFICATION, message: Any = None) -> bytes:
    msg = {'Type': msg_type.value, 'TopicArn': "arn:made:up"}
    message = message if message else {'hello': 'world'}

    if msg_type == MsgType.SUB_CONFIRMATION:
        msg['SubscribeURL'] = "https://subscribe-here"

    msg['Message'] = json.dumps(message)
    return json.dumps(msg).encode('utf-8')


def test_subscribe_message_adds_to_sub_queue():
    message = make_message(MsgType.SUB_CONFIRMATION)
    req = func.HttpRequest("GET", "https://dummy.url", body=message)

    datamsg = MagicMock()
    submsg = MagicMock()

    incoming_msg_handler.main(req, datamsg, submsg)

    assert submsg.set.call_args[0][0] == message.decode('utf-8')
    assert not datamsg.set.called


def test_notification_message_adds_to_data_queue():
    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    req = func.HttpRequest("GET", "https://dummy.url", body=message)

    datamsg = MagicMock()
    submsg = MagicMock()

    incoming_msg_handler.main(req, datamsg, submsg)

    assert datamsg.set.called
    assert not submsg.set.called
    pass


def test_file_dest_set_on_data_message():

    message = make_message(MsgType.NOTIFICATION, TEST_MSG)
    req = func.HttpRequest("GET", "https://dummy.url", body=message)

    datamsg = MagicMock()
    submsg = MagicMock()

    incoming_msg_handler.main(req, datamsg, submsg)

    out_message = json.loads(datamsg.set.call_args[0][0])
    assert out_message['file_dest'] == 'mo-atmospheric-mogreps-uk/wind_speed_of_gust-time: maximum (interval: 1 hour)-10.0m/2019-12-13T10:00:00Z/172800.nc'
    assert not submsg.set.called
    pass
