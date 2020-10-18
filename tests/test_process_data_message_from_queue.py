from __app__ import process_data_messages_from_queue
from unittest.mock import patch, MagicMock
import os
import json
import pytest

URL='https://blah.com/datasets/mo-atmospheric-mogreps-uk/objects/bGV2ZWxf'
MSG = {'metadata': {'cell_methods': 'time: maximum (interval: 1 hour)',
                         'created_time': '2019-12-13T12:10:54Z',
                         'forecast_period': '172800',
                         'forecast_period_bounds': '169200 172800',
                         'forecast_period_units': 'seconds',
                         'forecast_reference_time': '2019-12-13T10:00:00Z',
                         'height': '10.0',
                         'height_units': 'm',
                         'name': 'wind_speed_of_gust',
                         'realization': '15 16 17',
                         'time': '2019-12-15T10:00:00Z',
                         "model":"ukv"
                         },
            'object_size': 4378232,
            'target_blob': "save/here/pls.nc",
            'url': URL}


@pytest.mark.asyncio
async def test_writes_to_blob_with_filename():
    in_msg = MagicMock()
    in_msg.get_body.return_value =  json.dumps(MSG).encode('utf-8')

    blob_write_mock = MagicMock()
    async def blob_write(msg, q):
        blob_write_mock(msg, q)

    # run test
    with patch('__app__.process_data_messages_from_queue.write_lotus_url_data_to_blob', blob_write):
        await process_data_messages_from_queue.main(in_msg)

    # verify
    assert blob_write_mock.call_count == 1
    assert blob_write_mock.call_args[0]  == (URL, MSG['target_blob'] )
