from __future__ import annotations

from typing import Any, Dict, List

import requests

SECOP_API_URL = "https://secop.g.vmailru.net/api/v0"


class SecopApiClient:

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or SECOP_API_URL).rstrip("/")
        if not self.base_url:
            raise ValueError("SECOP_API_URL не задан и base_url не передан")

    def get_all_images(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/images", timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else [data]

    def get_images_by_component(self, component: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.base_url}/images", timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list):
            data = [data]

        return [doc for doc in data if doc.get("component") == component]

    def insert_image(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = requests.post(f"{self.base_url}/images", json=payload, timeout=20)
        if resp.status_code == 409:
            return {"ok": False, "error": "duplicate_key", "message": resp.text or "duplicate"}
        resp.raise_for_status()
        return resp.json()
