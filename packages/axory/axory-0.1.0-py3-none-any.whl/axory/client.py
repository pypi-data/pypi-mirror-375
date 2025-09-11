import requests
from typing import Optional
from .exceptions import APIError, AuthenticationError, ConfigurationError
import mimetypes
base_url = "https://axory.tech"
class AxoryClient:
    def __init__(self, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.user_id = None
        self.credits_remaining = None

        # Automatically verify API key on client creation
        self._verify_key()

    def _verify_key(self):
        """Verify API key and store user_id and credits"""
        url = f"{self.base_url}/verify"
        resp = requests.post(url, params={"token": self.api_key})
        
        if resp.status_code == 401:
            raise AuthenticationError(resp.json().get("detail", "Unauthorized"))
        if resp.status_code == 402:
            raise ConfigurationError(resp.json().get("detail", "No credits"))
        if not resp.ok:
            raise APIError(resp.text)

        data = resp.json()
        self.user_id = data["user_id"]
        self.credits_remaining = data["credits_remaining"]
    def analyze_file(
        self,
        file_path: str,
        content_hash: Optional[str] = None,
        has_text: bool = False
    ):
        """Upload video/image and get analysis results"""
        if not self.user_id:
            raise AuthenticationError("Client not verified")

        url = f"{self.base_url}/analyze"
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # fallback

        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, mime_type)}
            data = {
                "user_id": self.user_id,
                "content_hash": content_hash,
                "has_text": str(has_text)
        }


            resp = requests.post(url, files=files, data=data)

        if resp.status_code == 401:
            raise AuthenticationError(resp.json().get("detail", "Unauthorized"))
        if resp.status_code == 402:
            raise ConfigurationError(resp.json().get("detail", "No credits"))
        if not resp.ok:
            raise APIError(resp.text)

        return resp.json()
