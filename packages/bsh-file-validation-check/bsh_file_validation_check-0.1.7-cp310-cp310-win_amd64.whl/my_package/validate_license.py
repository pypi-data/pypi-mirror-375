import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os


def validate_license(license_json: dict) -> bool:
    """
    Validate license JSON passed from API against public.pem
    """
    try:
        license_data = json.dumps(license_json["data"]).encode()
        signature = bytes.fromhex(license_json["signature"])

        pem_path = os.path.join(os.path.dirname(__file__), "public.pem")

        with open(pem_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        public_key.verify(
            signature,
            license_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        expiry = datetime.strptime(license_json["data"]["expiry"], "%Y-%m-%d")
        if datetime.now() > expiry:
            return False
        return True

    except Exception:
        return False