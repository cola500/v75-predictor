#!/usr/bin/env python3
"""Jämför vår heuristik-ranking mot ATG:s vinnarodds för 7 lopp på Årjäng 2026-04-19."""
import json, urllib.request

BASE = "https://www.atg.se/services/racinginfo/v1/api"
DATE = "2026-04-19"
TRACK = 31
RACES = [4, 5, 6, 7, 8, 9, 10]
NOT_BETTABLE = 9999  # ATG:s placeholder för "odds ej satt / ej spelbar"


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def score_horse(start):
    """Samma heuristik som predict.py — karriärvinst + intjänat + form + tränare."""
    h = start["horse"]
    stats = h.get("statistics", {})
    life = stats.get("life", {})
    starts = life.get("starts", 0) or 1
    wins = life.get("placement", {}).get("1", 0)
    win_rate = wins / starts
    recent = stats.get("years", {}).get("2026", {})
    rec_earn = (recent.get("earnings", 0) or 0) / 100 / 1000 / 10  # tkr/10
    rec_starts = recent.get("starts", 0)
    rec_wins = recent.get("placement", {}).get("1", 0)
    form = (rec_wins / rec_starts) if rec_starts else 0
    tr = h.get("trainer", {}).get("statistics", {}).get("years", {}).get("2025", {})
    tr_starts = tr.get("starts", 0) or 1
    tr_rate = tr.get("placement", {}).get("1", 0) / tr_starts
    return win_rate * 60 + rec_earn * 20 + form * 15 + tr_rate * 5


def our_top3(race_id):
    race = get(f"{BASE}/races/{race_id}")
    rows = []
    for s in race.get("starts", []):
        if s.get("scratched"):
            continue
        rows.append((s["number"], s["horse"]["name"], score_horse(s)))
    rows.sort(key=lambda r: r[2], reverse=True)
    return race.get("name"), rows[:3]


def market_top3(race_id):
    """Odds-data från vinnare-pool. Lägre odds = större favorit."""
    game = get(f"{BASE}/games/vinnare_{race_id}")
    race = game["races"][0]
    rows = []
    for s in race.get("starts", []):
        if s.get("scratched"):
            continue
        odds = s.get("pools", {}).get("vinnare", {}).get("odds")
        if odds is None or odds == NOT_BETTABLE:
            continue
        rows.append((s["number"], s["horse"]["name"], odds))
    rows.sort(key=lambda r: r[2])  # lägst odds först
    return rows[:3]


def main():
    total_overlap = 0
    total_compared = 0
    print(f"{'Lopp':<4} {'Vår topp-3':<48} {'Marknadens topp-3':<48} Överlapp")
    print("-" * 120)
    for n in RACES:
        race_id = f"{DATE}_{TRACK}_{n}"
        race_name, ours = our_top3(race_id)
        market = market_top3(race_id)
        our_nrs = {r[0] for r in ours}
        mkt_nrs = {r[0] for r in market}
        overlap = len(our_nrs & mkt_nrs)
        total_overlap += overlap
        total_compared += 3
        ours_txt = ", ".join(f"#{nr} {name[:15]}" for nr, name, _ in ours)
        mkt_txt = ", ".join(f"#{nr} ({odds/100:.2f})" for nr, name, odds in market)
        print(f"{n:<4} {ours_txt:<48} {mkt_txt:<48} {overlap}/3")

    pct = 100 * total_overlap / total_compared
    print("-" * 120)
    print(f"Totalt överlapp: {total_overlap}/{total_compared} = {pct:.0f} %")
    if pct >= 70:
        verdict = "REDUNDANT — vi håller oftast med marknaden."
    elif pct >= 40:
        verdict = "ANNAN BILD — vi avviker tillräckligt för att vara intressanta."
    else:
        verdict = "VILT AVVIKANDE — antingen geniala eller helt ute."
    print(f"Slutsats: {verdict}")

    # Detaljerade avvikelser
    print("\n=== Detaljerade avvikelser per lopp ===")
    for n in RACES:
        race_id = f"{DATE}_{TRACK}_{n}"
        _, ours = our_top3(race_id)
        market = market_top3(race_id)
        our_nrs = {r[0] for r in ours}
        mkt_nrs = {r[0] for r in market}
        only_us = [r for r in ours if r[0] not in mkt_nrs]
        only_mkt = [r for r in market if r[0] not in our_nrs]
        if not only_us and not only_mkt:
            continue
        print(f"\nLopp {n}:")
        for nr, name, score in only_us:
            print(f"  Vi säger JA, marknaden NEJ:  #{nr} {name} (score {score:.1f})")
        for nr, name, odds in only_mkt:
            print(f"  Marknaden säger JA, vi NEJ:  #{nr} {name} (odds {odds/100:.2f})")


if __name__ == "__main__":
    main()
