import base64
import json
from fastapi.responses import JSONResponse
from fastapi import Request

from .validate_license import validate_license


def sample_middleware(key: str):
    license_header = base64.b64decode(key).decode()
    license_json = json.loads(license_header)
    res = validate_license(license_json=license_json)
    return res