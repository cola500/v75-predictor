#!/usr/bin/env python3
"""Hämta V75-lopp från ATG och ranka hästar. Zero friction, one file."""
import json, urllib.request, sys

BASE = "https://www.atg.se/services/racinginfo/v1/api"
DATE = "2026-04-19"
TRACK = 31  # Årjäng
TRACK_NAME = "Årjäng"
RACES = list(range(1, 11))  # Hela dagen, 10 lopp
NOT_BETTABLE = 9999  # ATG:s placeholder för "odds ej satt"

# Spelformer för denna dag (verifierat mot ATG:s games-endpoints).
# Tuple: (visningsnamn, beskrivning, vilka lopp som ingår)
BETTING_FORMS = [
    (
        "Grand Slam 75 (dagens V75-spel)",
        "Poolspel: välj rätt häst i varje ingående lopp. Alla rätt ger stor utdelning. "
        "Dagens GS75 omfattar 7 lopp.",
        [4, 5, 6, 7, 8, 9, 10],
    ),
    (
        "V4",
        "Poolspel: välj rätt häst i 4 på varandra följande lopp. Mindre kombinatorik än V75.",
        [7, 8, 9, 10],
    ),
    (
        "V3",
        "Poolspel: välj rätt häst i 3 på varandra följande lopp. Billigare att spela brett.",
        [8, 9, 10],
    ),
    (
        "DD — Dagens Dubbel",
        "Välj rätt häst i 2 lopp. Enklaste kombinationsspelet.",
        [9, 10],
    ),
]


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def year_win_rate(stats, year):
    """Hämta vinstprocent från statistics.years.{year}. 0 om saknas."""
    y = stats.get("years", {}).get(year, {})
    st = y.get("starts", 0) or 1
    return y.get("placement", {}).get("1", 0) / st


def post_position_bonus(pos, start_method):
    """Inre spår gynnar vid volte; mindre effekt vid autostart."""
    if not pos:
        return 0
    if start_method == "volte":
        # Spår 1 = 1.0, spår 8+ = 0. Linjär.
        return max(0, (8 - pos)) / 7
    # autostart: halv effekt, räcker längre ut
    return max(0, (12 - pos)) / 22


def score_horse(start, start_method):
    h = start["horse"]
    stats = h.get("statistics", {})
    life = stats.get("life", {})
    starts = life.get("starts", 0) or 1
    win_rate = life.get("placement", {}).get("1", 0) / starts
    recent = stats.get("years", {}).get("2026", {})
    # ATG returnerar earnings i öre. 1 kr = 100 öre. Räkna om till tkr.
    recent_earnings_tkr = (recent.get("earnings", 0) or 0) / 100 / 1000
    recent_earnings = recent_earnings_tkr / 10  # skalad för score
    recent_starts = recent.get("starts", 0)
    recent_wins = recent.get("placement", {}).get("1", 0)
    recent_form = (recent_wins / recent_starts) if recent_starts else 0

    tr_rate = year_win_rate(h.get("trainer", {}).get("statistics", {}), "2025")
    dr_rate = year_win_rate((start.get("driver") or {}).get("statistics", {}), "2025")
    pp = start.get("postPosition")
    post_factor = post_position_bonus(pp, start_method)

    score = (
        win_rate * 60
        + recent_earnings * 20
        + recent_form * 15
        + dr_rate * 10
        + tr_rate * 5
        + post_factor * 5
    )
    return score, {
        "life_win_rate": round(win_rate, 3),
        "recent_earnings_kr": int(recent_earnings_tkr * 1000),
        "recent_form": round(recent_form, 3),
        "trainer_win_rate": round(tr_rate, 3),
        "driver_win_rate": round(dr_rate, 3),
        "post_position": pp,
        "start_method": start_method,
    }


def fetch_odds(race_id):
    """Returnerar dict: startnummer -> odds (float, t.ex. 2.89). Saknade odds utelämnas."""
    try:
        game = get(f"{BASE}/games/vinnare_{race_id}")
    except Exception:
        return {}
    odds_map = {}
    race = game.get("races", [{}])[0]
    for s in race.get("starts", []):
        o = s.get("pools", {}).get("vinnare", {}).get("odds")
        if o is None or o == NOT_BETTABLE:
            continue
        odds_map[s["number"]] = o / 100
    return odds_map


def rank_race(race_id):
    race = get(f"{BASE}/races/{race_id}")
    odds_map = fetch_odds(race_id)
    start_method = race.get("startMethod", "volte")
    rows = []
    for s in race.get("starts", []):
        if s.get("scratched"):
            continue
        score, parts = score_horse(s, start_method)
        rows.append({
            "nr": s["number"],
            "name": s["horse"]["name"],
            "driver": (s.get("driver") or {}).get("shortName", "?"),
            "trainer": s["horse"].get("trainer", {}).get("shortName", "?"),
            "score": round(score, 2),
            "parts": parts,
            "odds": odds_map.get(s["number"]),
        })
    rows.sort(key=lambda r: r["score"], reverse=True)
    # Marknadens topp-3: de tre med lägst odds
    market = sorted(
        [r for r in rows if r["odds"] is not None],
        key=lambda r: r["odds"],
    )[:3]
    return race.get("name", race_id), rows, market


def kr(n):
    """Formatera kr med tusentalsavgränsare (svenska: mellanslag)."""
    return f"{n:,.0f}".replace(",", " ") + " kr"


def motivation(parts):
    p = parts
    if p["life_win_rate"] >= 0.3:
        return f"Vinner {int(p['life_win_rate']*100)} % av sina starter i karriären."
    if p["recent_form"] >= 0.3:
        return f"Het form: {int(p['recent_form']*100)} % vinst 2026."
    if p["driver_win_rate"] >= 0.2:
        return f"Het kusk: {int(p['driver_win_rate']*100)} % vinst 2025."
    if p["recent_earnings_kr"] >= 50000:
        return f"Tjänat {kr(p['recent_earnings_kr'])} 2026 — bland de bäst betalda i fältet."
    if p["start_method"] == "volte" and (p["post_position"] or 99) <= 3:
        return f"Innerspår {p['post_position']} vid volte — kan rusa ledningen direkt."
    if p["trainer_win_rate"] >= 0.15:
        return f"Tränas av ett toppstall ({int(p['trainer_win_rate']*100)} % vinst 2025)."
    return "Toppscore i fältet på sammanvägd statistik."


def render_html(races):
    cards = []
    for n, name, rows, market in races:
        mkt_nrs = {m["nr"] for m in market}
        items = []
        for i, r in enumerate(rows[:3], 1):
            odds_html = (
                f"<span class='odds'>Odds {r['odds']:.2f}</span>"
                if r["odds"] is not None else
                "<span class='odds odds-na'>Odds saknas</span>"
            )
            match = ""
            if r["nr"] in mkt_nrs:
                match = "<span class='match'>Marknadsfavorit</span>"
            else:
                match = "<span class='contra'>Avviker från marknaden</span>"
            items.append(f"""
            <li class="pick pick-{i}">
              <div class="rank">{i}</div>
              <div class="who">
                <div class="nr">Nr {r['nr']} · Spår {r['parts']['post_position']} ({r['parts']['start_method']})</div>
                <div class="name">{r['name']}</div>
                <div class="meta">Kusk: {r['driver']} · Tränare: {r['trainer']}</div>
              </div>
              <div class="why">{motivation(r['parts'])}</div>
              <div class="tags">{odds_html} {match}</div>
            </li>""")

        mkt_html = (
            "<div class='market'>Marknadens topp-3: "
            + ", ".join(
                f"<b>#{m['nr']} {m['name']}</b> ({m['odds']:.2f})"
                for m in market
            )
            + "</div>"
        ) if market else ""

        cards.append(f"""
        <section class="race">
          <header>
            <span class="lopp">Lopp {n}</span>
            <h2>{name}</h2>
          </header>
          <ol class="picks">{''.join(items)}</ol>
          {mkt_html}
        </section>""")

    return f"""<!doctype html>
<html lang="sv"><head>
<meta charset="utf-8"><title>V75-tips · Årjäng {DATE}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 16px/1.5 -apple-system, system-ui, sans-serif; margin: 0; padding: 24px; max-width: 780px; margin-inline: auto; background: #faf7f2; color: #222; }}
  h1 {{ margin: 0 0 4px; font-size: 28px; }}
  .sub {{ color: #777; margin-bottom: 24px; }}
  .race {{ background: white; border-radius: 14px; padding: 20px; margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .race header {{ border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 12px; }}
  .lopp {{ font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: #c2185b; font-weight: 700; }}
  .race h2 {{ margin: 2px 0 0; font-size: 18px; font-weight: 600; }}
  ol.picks {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }}
  .pick {{ display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto auto; column-gap: 12px; padding: 10px 12px; border-radius: 10px; background: #f5f1ea; }}
  .pick-1 {{ background: #fff4da; }}
  .rank {{ font-weight: 800; font-size: 22px; color: #c2185b; grid-row: 1 / span 3; align-self: center; text-align: center; }}
  .who .nr {{ font-size: 12px; color: #999; }}
  .who .name {{ font-weight: 700; font-size: 17px; }}
  .who .meta {{ font-size: 12px; color: #666; }}
  .why {{ grid-column: 2; font-size: 14px; color: #333; margin-top: 4px; }}
  .tags {{ grid-column: 2; margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap; }}
  .tags span {{ font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600; }}
  .odds {{ background: #e8f0ff; color: #1e3a8a; }}
  .odds-na {{ background: #eee; color: #888; }}
  .match {{ background: #dcfce7; color: #166534; }}
  .contra {{ background: #fde2e2; color: #991b1b; }}
  .market {{ margin-top: 10px; padding-top: 10px; border-top: 1px dashed #eee; font-size: 12px; color: #666; }}
  .market b {{ color: #333; }}
  .info {{ background: white; border-radius: 14px; padding: 16px 20px; margin-top: 24px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .info summary {{ cursor: pointer; font-weight: 700; font-size: 15px; color: #c2185b; }}
  .info p {{ margin: 12px 0; font-size: 14px; }}
  .info table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 8px 0 4px; }}
  .info th, .info td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #eee; }}
  .info th {{ color: #888; font-weight: 600; }}
  .info td:last-child {{ font-family: ui-monospace, monospace; color: #c2185b; }}
  .info ol {{ padding-left: 20px; font-size: 13px; }}
  .info .caveat {{ color: #888; font-size: 12px; margin-top: 12px; }}
  .match-demo, .contra-demo {{ font-size: 11px; padding: 1px 8px; border-radius: 999px; font-weight: 600; }}
  .match-demo {{ background: #dcfce7; color: #166534; }}
  .contra-demo {{ background: #fde2e2; color: #991b1b; }}
  .day-overview {{ background: white; border-radius: 14px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .day-overview h2 {{ margin: 0 0 10px; font-size: 18px; }}
  .day-overview p {{ font-size: 14px; color: #333; margin: 8px 0; }}
  .day-overview table.forms {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 12px 0; }}
  .day-overview table.forms th, .day-overview table.forms td {{ text-align: left; padding: 8px; border-bottom: 1px solid #eee; vertical-align: top; }}
  .day-overview table.forms th {{ color: #888; font-weight: 600; }}
  .day-overview table.forms td:first-child {{ white-space: nowrap; }}
  .day-overview .disclaimer {{ color: #777; font-size: 12px; font-style: italic; }}
  footer {{ color: #999; font-size: 12px; margin-top: 32px; text-align: center; }}
</style></head>
<body>
  <h1>V75-tips · {TRACK_NAME}</h1>
  <div class="sub">{DATE} · auto-rankade toppval per lopp baserat på publik statistik</div>

  <section class="day-overview">
    <h2>Dagens program på {TRACK_NAME}</h2>
    <p>
      Sammanlagt 10 lopp körs. <b>Lopp 1–3</b> är "singelspel" — du satsar på vinnare, plats eller enklare
      kombinationer (komb, tvilling, trio) inom varje enskilt lopp. Det som vi brukar kalla "V75" är det
      stora poolspelet som på den här banan heter <b>Grand Slam 75 (GS75)</b>, och som körs över 7 lopp:
    </p>
    <table class="forms">
      <tr><th>Spelform</th><th>Lopp</th><th>Vad det innebär</th></tr>
      {''.join(
          f'<tr><td><b>{name}</b></td><td>{", ".join(str(x) for x in lopp)}</td><td>{desc}</td></tr>'
          for name, desc, lopp in BETTING_FORMS
      )}
    </table>
    <p class="disclaimer">
      Vår modell rankar varje av de 10 loppen oavsett spelform — men styrkan (läs: varians i score mellan
      hästarna) är störst i lopp där fältet är tunt eller toppningen glasklar. Använd rankingen som
      underlag, inte som recept.
    </p>
  </section>

  {''.join(cards)}

  <details class="info" open>
    <summary>Så räknas tipsen fram</summary>
    <p>Varje häst får en <b>score</b> byggd på fyra publika statistikfält från ATG. Högst score per lopp blir topp-3.</p>
    <table>
      <tr><th>Faktor</th><th>Vad det är</th><th>Vikt</th></tr>
      <tr><td>Karriärvinst%</td><td>Antal segrar genom antal starter i hästens karriär</td><td>× 60</td></tr>
      <tr><td>Intjänat 2026</td><td>Prispengar i år (i tusenlappar, delat med 10)</td><td>× 20</td></tr>
      <tr><td>Form 2026</td><td>Segrar ÷ starter i år</td><td>× 15</td></tr>
      <tr><td>Kuskvinst% 2025</td><td>Kuskens vinstprocent föregående helår</td><td>× 10</td></tr>
      <tr><td>Tränarvinst% 2025</td><td>Tränarens vinstprocent föregående helår</td><td>× 5</td></tr>
      <tr><td>Startspår</td><td>Inre spår gynnar vid volte (full effekt), halv effekt vid autostart</td><td>× 5</td></tr>
    </table>
    <p><b>Motiveringen</b> väljs efter vilken faktor som sticker ut mest för hästen, i prioritetsordning:</p>
    <ol>
      <li>Karriärvinst ≥ 30 % → "Vinner X % av sina starter"</li>
      <li>Form ≥ 30 % → "Het form: X % vinst 2026"</li>
      <li>Kuskvinst ≥ 20 % → "Het kusk: X % vinst 2025"</li>
      <li>Intjänat ≥ 50 000 kr → "Tjänat X kr 2026"</li>
      <li>Innerspår (1–3) vid volte → "Kan rusa ledningen direkt"</li>
      <li>Tränaren ≥ 15 % vinst → "Topptränare"</li>
      <li>Annars → "Toppscore på sammanvägd statistik"</li>
    </ol>
    <p><b>Marknadens topp-3</b> är de tre hästar som har lägst vinnar-odds just nu — dvs. de som spelarna tror mest på. När vår topp-3 matchar marknadens får hästen taggen <span class="match-demo">Marknadsfavorit</span>. När vi tycker annorlunda får hästen <span class="contra-demo">Avviker från marknaden</span> — spännande men mer risk.</p>
    <p class="caveat">Enkel heuristik — tittar inte på banans karaktär, väderlek, motståndarnas relativa styrka, skobyten eller senaste 3-5 starternas trend. Fungerar som ett <i>dugligt</i> grundval, inte som garanti.</p>
  </details>

  <footer>Experiment — ej spelråd. Data: ATG.</footer>
</body></html>"""


def main():
    races = []
    for n in RACES:
        race_id = f"{DATE}_{TRACK}_{n}"
        name, rows, market = rank_race(race_id)
        races.append((n, name, rows, market))
        print(f"\n=== Lopp {n}: {name} ===")
        for r in rows[:3]:
            p = r["parts"]
            odds_txt = f"odds={r['odds']:.2f}" if r["odds"] is not None else "odds=?"
            print(
                f"  #{r['nr']:<2} spår{p['post_position']:<2} {r['name']:<22} "
                f"score={r['score']:<6} {odds_txt:<12} "
                f"kusk%={p['driver_win_rate']} "
                f"vinst%={p['life_win_rate']}"
            )
        if market:
            mkt = ", ".join(f"#{m['nr']} {m['name']} ({m['odds']:.2f})" for m in market)
            print(f"  marknad: {mkt}")

    html = render_html(races)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\nSkrev index.html")


if __name__ == "__main__":
    main()
