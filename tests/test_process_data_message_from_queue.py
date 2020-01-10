from __app__ import process_data_messages_from_queue
from unittest.mock import patch, MagicMock
import os
import json
from unittest.mock import patch, MagicMock


MSG = json.dumps({
    'url': 'my-url.com/place'
}).encode('utf-8')


@patch('__app__.process_data_messages_from_queue.requests.get')
def test_writes_to_blob(get_mock):
    # set up
    data = b'my-data'
    get_mock.return_value.ok = True
    get_mock.return_value.content = data

    in_msg = MagicMock()
    out_blob = MagicMock()
    in_msg.get_body.return_value = MSG

    # run test
    process_data_messages_from_queue.main(in_msg, out_blob)

    # verify
    assert out_blob.set.call_args[0][0].read() == data
