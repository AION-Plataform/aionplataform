from typing import Dict, Any
from urllib import request
from urllib.error import URLError, HTTPError
import json
from .base import BaseNode


class HttpToolNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        method = self.config.get("method", "GET").upper()
        url = self.config.get("url")
        payload = self.config.get("payload") or inputs.get("payload")

        if not url:
            return {"response": None, "error": "No URL provided."}

        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(url, data=data, method=method, headers=headers)
        try:
            with request.urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8")
                return {
                    "response": {
                        "status": response.status,
                        "body": body,
                        "headers": dict(response.headers),
                    }
                }
        except HTTPError as exc:
            return {"response": None, "error": f"HTTP error {exc.code}: {exc.reason}"}
        except URLError as exc:
            return {"response": None, "error": f"Request error: {exc.reason}"}
