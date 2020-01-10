import os
ORIG_APIKEY_VAL = os.environ.get('APIKEY', None)


def pytest_sessionstart(session):
    os.environ['APIKEY'] = "made-up-key"


def pytest_sessionfinish(session, exitstatus):
    if ORIG_APIKEY_VAL is None:
        del os.environ['APIKEY']
    else:
        os.environ['APIKEY'] = ORIG_APIKEY_VAL
