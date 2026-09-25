"""Projde všechny weby ze sites/ a na Discord pošle jen nově přibyté položky.

Použití:
    python main.py            # normální běh
    python main.py --dry-run  # vypíše zprávy místo odeslání a nic neuloží
"""

import os
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv

import seen
from notify import Discord
from sites import SITES
from sites.base import Site

BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "state"


def run_site(site: Site, discord: Discord) -> None:
    items = site.scrape()
    if not items:
        # nejspíš se změnila struktura webu
        raise RuntimeError("Scraper nevrátil žádné položky, zkontrolujte selektory.")
    items = [i for i in items if site.matches(i)]

    state_file = STATE_DIR / f"{site.name}.json"
    known = seen.load(state_file)
    if known is None:
        # první běh: jen si zapamatujeme, co už existuje, ať nepřijde záplava zpráv
        discord.text(f"✅ **{site.name}**: monitoring spuštěn, výchozí stav {len(items)} položek.")
        new = []
    else:
        new = [i for i in items if i["id"] not in known]
        if new:
            discord.new_items(site.name, new)
    print(f"{site.name}: {len(items)} položek, {len(new)} nových")

    # ukládáme až po úspěšném odeslání, při chybě se nové položky pošlou příště
    if not discord.dry_run:
        seen.save(state_file, seen.mark(known or {}, items))


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    dry_run = "--dry-run" in sys.argv
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook and not dry_run:
        print("Chybí DISCORD_WEBHOOK_URL v .env", file=sys.stderr)
        return 2
    discord = Discord(webhook, dry_run=dry_run)

    failed = 0
    for site in SITES:
        # chyba jednoho webu nesmí zastavit ostatní
        try:
            run_site(site, discord)
        except Exception as exc:
            failed += 1
            traceback.print_exc()
            try:
                discord.error(f"⚠️ **{site.name}** selhal: `{type(exc).__name__}: {exc}`")
            except Exception:
                traceback.print_exc()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
