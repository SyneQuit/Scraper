"""bluffish.cz: nadcházející eventy (Krvavá hodina odbila apod.).

Stránka je javascriptová aplikace, proto se vykresluje v headless prohlížeči (Playwright).
Nepoužívá se vestavěný filtr ?region=, protože web zná jen pár měst. Kraj se filtruje
podle vlastního seznamu v sites/regions.py.
"""

import re

from playwright.sync_api import sync_playwright

from sites.base import USER_AGENT, Site
from sites.regions import is_jihocesky

BASE_URL = "https://bluffish.cz"
EVENTS_URL = f"{BASE_URL}/events"
CARD_SELECTOR = 'a[href^="/events/"]:has(h3)'

# Z karty čteme údaje podle ikon vedle nich (lucide-*). Jsou stabilnější než generované CSS třídy.
EXTRACT_JS = """
cards => cards.map(card => {
    const byIcon = name => card.querySelector(`svg.lucide-${name}`)?.parentElement?.innerText?.trim() || null;
    const lines = card.innerText.split('\\n').map(s => s.trim());
    return {
        href: card.getAttribute('href'),
        // textContent vrací název v původní podobě, innerText by ho vrátil po CSS uppercase
        title: card.querySelector('h3')?.textContent?.trim(),
        date: byIcon('calendar'),
        clock: byIcon('clock'),
        city: byIcon('map-pin'),
        capacity: byIcon('users') || lines.find(s => /^\\d+\\/\\d+$/.test(s)) || null,
        storyteller: card.querySelector('a[href^="/storyteller/"]')?.innerText?.trim() || null,
        price: lines.find(s => /Kč$|^zdarma$/i.test(s)) || null,
    };
})
"""


class Bluffish(Site):
    name = "bluffish"

    def scrape(self) -> list[dict]:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(user_agent=USER_AGENT, locale="cs-CZ")
                page.goto(EVENTS_URL, wait_until="networkidle", timeout=60_000)
                page.wait_for_selector(CARD_SELECTOR, timeout=30_000)
                raw = page.eval_on_selector_all(CARD_SELECTOR, EXTRACT_JS)
            finally:
                browser.close()
        return [self._to_item(r) for r in raw if r.get("href") and r.get("title")]

    @staticmethod
    def _to_item(r: dict) -> dict:
        url = BASE_URL + r["href"]
        # u víkendových eventů ikona hodin ukazuje délku ("3d"), ne čas začátku
        clock = r.get("clock") or ""
        time = clock if re.fullmatch(r"\d{1,2}:\d{2}", clock) else None
        when = " ".join(filter(None, [r.get("date"), time]))
        if clock and not time:
            when += f" ({clock})"
        return {
            "id": r["href"].rsplit("/", 1)[-1],  # UUID eventu
            "title": r["title"],
            "url": url,
            "city": r.get("city"),
            "details": {
                "Kdy": when or None,
                "Kde": r.get("city"),
                "Cena": r.get("price"),
                "Obsazenost": r.get("capacity"),
                "Vypravěč": r.get("storyteller"),
            },
        }

    def matches(self, item: dict) -> bool:
        return is_jihocesky(item.get("city"))
