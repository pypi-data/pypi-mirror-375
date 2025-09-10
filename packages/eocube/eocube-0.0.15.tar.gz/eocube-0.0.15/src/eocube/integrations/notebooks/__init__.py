import os
import s3fs

from ..auth import ROCS_DEFAULT_STORAGE_ENDPOINT
from ..auth.client import get_eocube_sign
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
session_token = os.environ.get("AWS_SESSION_TOKEN", ROCS_DEFAULT_STORAGE_ENDPOINT)

fs = s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key, token=session_token)

def setup_notebook():
    import nest_asyncio
    nest_asyncio.apply()

def sign_in_place(entry):
    get_eocube_sign(entry)
