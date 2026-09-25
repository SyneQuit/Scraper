"""Rozpoznání kraje podle názvu města nebo obce."""

import unicodedata

# Města a větší obce Jihočeského kraje. Chybí-li nějaké, stačí ho sem doplnit (s diakritikou nebo bez).
JIHOCESKY = {
    # okresní města
    "České Budějovice", "Český Krumlov", "Jindřichův Hradec", "Písek", "Prachatice", "Strakonice", "Tábor",
    # okres České Budějovice
    "Hluboká nad Vltavou", "Lišov", "Rudolfov", "Trhové Sviny", "Týn nad Vltavou", "Zliv", "Borovany",
    "Nové Hrady", "Ledenice", "Ševětín", "Dříteň", "Hosín", "Litvínovice",
    "Srubec", "Dobrá Voda u Českých Budějovic", "Včelná", "Boršov nad Vltavou",
    "Zlatá Koruna", "Hrdějovice", "Mydlovary", "Olešník", "Temelín",
    # okres Český Krumlov
    "Kaplice", "Velešín", "Vyšší Brod", "Horní Planá", "Chvalšiny", "Frymburk", "Lipno nad Vltavou",
    "Hořice na Šumavě", "Kájov", "Křemže", "Černá v Pošumaví", "Rožmberk nad Vltavou", "Dolní Dvořiště",
    "Benešov nad Černou", "Horní Stropnice", "Loučovice", "Přídolí", "Holubov", "Brloh",
    # okres Jindřichův Hradec
    "Dačice", "Třeboň", "Suchdol nad Lužnicí", "Slavonice", "Nová Bystřice", "Kardašova Řečice",
    "Kamenice nad Lipou", "Počátky", "Nová Včelnice", "Strmilov", "Stráž nad Nežárkou", "České Velenice",
    "Chlum u Třeboně", "Deštná", "Lomnice nad Lužnicí", "Kunžak", "Jarošov nad Nežárkou",
    # okres Písek
    "Milevsko", "Mirotice", "Mirovice", "Protivín", "Čimelice", "Orlík nad Vltavou", "Zvíkovské Podhradí",
    "Kovářov", "Albrechtice nad Vltavou", "Putim", "Ražice", "Bernartice", "Chyšky",
    # okres Prachatice
    "Vimperk", "Netolice", "Volary", "Husinec", "Lhenice", "Vlachovo Březí", "Čkyně",
    "Kvilda", "Stachy", "Zdíkov", "Strunkovice nad Blanicí", "Nová Pec", "Horní Vltavice", "Borová Lada",
    # okres Strakonice
    "Blatná", "Vodňany", "Volyně", "Bělčice", "Sedlice", "Radomyšl", "Katovice", "Štěkeň", "Cehnice",
    "Čestice", "Horní Poříčí", "Bavorov",
    # okres Tábor
    "Sezimovo Ústí", "Soběslav", "Planá nad Lužnicí", "Veselí nad Lužnicí", "Bechyně", "Chýnov",
    "Mladá Vožice", "Jistebnice", "Malšice", "Opařany", "Chotoviny", "Ratibořské Hory", "Choustník",
    "Dírná", "Tučapy", "Zhoř u Tábora", "Borotín", "Stádlec",
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(text.lower().replace("-", " ").split())


_JIHOCESKY_NORM = {_normalize(c) for c in JIHOCESKY}


def is_jihocesky(city: str | None) -> bool:
    """Porovnává bez diakritiky a velikosti písmen. Zvládne i "České Budějovice 2" nebo "Tábor - Klokoty"."""
    if not city:
        return False
    norm = _normalize(city)
    return any(norm == c or norm.startswith(c + " ") for c in _JIHOCESKY_NORM)
