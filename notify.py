"""Odesílání zpráv na Discord přes webhook."""

import time

import requests

EMBEDS_PER_MESSAGE = 10  # limit Discordu
COLOR_NEW = 0x2ECC71
COLOR_ERROR = 0xE74C3C


class Discord:
    def __init__(self, webhook_url: str, dry_run: bool = False) -> None:
        self.webhook_url = webhook_url
        self.dry_run = dry_run

    def _post(self, payload: dict) -> None:
        if self.dry_run:
            print(payload)
            return
        for _ in range(5):
            resp = requests.post(self.webhook_url, json=payload, timeout=15)
            if resp.status_code == 429:  # rate limit, Discord řekne, jak dlouho čekat
                time.sleep(float(resp.json().get("retry_after", 1)))
                continue
            resp.raise_for_status()
            return
        raise RuntimeError("Discord opakovaně vrací 429 (rate limit)")

    def new_items(self, site_name: str, items: list[dict]) -> None:
        embeds = [
            {
                "title": f"🆕 {item['title']}"[:256],
                "url": item.get("url"),
                "description": "\n".join(
                    f"**{label}:** {value}" for label, value in item.get("details", {}).items() if value
                )[:4096],
                "color": COLOR_NEW,
            }
            for item in items
        ]
        for start in range(0, len(embeds), EMBEDS_PER_MESSAGE):
            payload = {"embeds": embeds[start:start + EMBEDS_PER_MESSAGE]}
            if start == 0:
                payload["content"] = f"**{site_name}**: {len(items)} nových"
            self._post(payload)

    def text(self, text: str) -> None:
        self._post({"content": text[:2000]})

    def error(self, text: str) -> None:
        self._post({"embeds": [{"description": text[:4096], "color": COLOR_ERROR}]})
