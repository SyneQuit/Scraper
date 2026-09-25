"""Společný základ pro všechny weby.

Každý web vrací položky ve tvaru:
    {
        "id": "unikátní a stabilní identifikátor (typicky URL detailu)",
        "title": "Název eventu",
        "url": "https://...",
        "details": {"Datum": "...", "Místo": "..."},  # libovolné popisky -> hodnoty
    }
"""

import time

import requests

USER_AGENT = "Webscraper/1.0 (osobni monitoring eventu)"


class Site:
    name: str = ""  # krátký název bez mezer, použije se pro soubor se stavem
    delay_seconds: float = 1.0

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._last_request = 0.0

    def fetch(self, url: str, **kwargs) -> requests.Response:
        """GET s pauzou mezi požadavky. Při chybě vyhodí výjimku."""
        wait = self._last_request + self.delay_seconds - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(url, timeout=15, **kwargs)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        return resp

    def scrape(self) -> list[dict]:
        raise NotImplementedError

    def matches(self, item: dict) -> bool:
        """Filtr položek (např. jen Jihočeský kraj). Výchozí je propustit vše."""
        return True
