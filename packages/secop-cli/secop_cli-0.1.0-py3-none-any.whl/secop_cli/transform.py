from __future__ import annotations

from typing import Any, Dict, Iterable, List

from secop_cli.models.cli_models import ImageCLI


def extract_cloud_rows(doc: Dict[str, Any]) -> list[ImageCLI]:
    rows: List[ImageCLI] = []
    component = doc["component"]
    cloud = (doc or {}).get("cloud", {})
    if isinstance(cloud, dict):
        for cloud_component_name, payload in cloud.items():
            if not isinstance(payload, dict):
                continue
            rows.append(
                ImageCLI(
                    component=component,
                    cloud_component_name=cloud_component_name,
                    image_name=str(payload.get("name")) if payload.get("name") else "",
                    image_version=str(payload.get("version")) if payload.get("version") else "",
                    registry=str(payload.get("registry")) if payload.get("registry") else "",
                )
            )
    return rows


def flatten_docs(docs: Iterable[Dict[str, Any]]) -> list[ImageCLI]:
    out: List[ImageCLI] = []
    for d in docs:
        out.extend(extract_cloud_rows(d))
    return out
