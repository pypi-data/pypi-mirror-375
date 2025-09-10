import os
import s3fs

from ..auth import ROCS_DEFAULT_STORAGE_ENDPOINT
from ..auth.client import get_eocube_sign

access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
session_token = os.environ.get("AWS_SESSION_TOKEN")
endpoint = os.environ.get("AWS_S3_ENDPOINT", ROCS_DEFAULT_STORAGE_ENDPOINT)

fs = s3fs.S3FileSystem(
    anon=False,
    key=access_key,
    secret=secret_key,
    token=session_token,
    endpoint_url=endpoint,
    asynchronous=False,
)

_sign = get_eocube_sign(fs)


def setup_notebook():
    import nest_asyncio

    nest_asyncio.apply()


def sign_in_place(entry):
    _sign(entry)
