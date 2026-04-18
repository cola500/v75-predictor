# V75 Predictor

Enkel prediktor för svenska travlopp (V75/GS75). Hämtar öppen data från ATG, räknar en duglighetsscore per häst och genererar en HTML-tipssida med topp-3 per lopp plus marknadens vinnar-odds som jämförelse.

**Live:** [cola500.github.io/v75-predictor](https://cola500.github.io/v75-predictor/)

## Kör själv

Krav: Python 3.8+. Inga externa paket.

```bash
python3 predict.py
open index.html      # macOS — annars öppna i valfri browser
```

Scriptet hämtar data från ATG:s publika API och skriver `index.html` i samma mapp.

## Byt lopp

Ändra överst i `predict.py`:

```python
DATE = "2026-04-19"
TRACK = 31                     # Årjäng — andra banor: se /api/calendar/day/{YYYY-MM-DD}
TRACK_NAME = "Årjäng"
RACES = list(range(1, 11))     # Hela dagen
```

Om du vill ranka andra banor/dagar behöver du också uppdatera `BETTING_FORMS`-listan (hårdkodad per dag — spelformsstrukturen skiljer sig mellan banor och dagar).

## Score-formel

Varje häst får en poäng byggd på sex publika statistikfält:

```
score = karriärvinst%            × 60
      + intjänat 2026 (tkr/10)   × 20
      + form 2026                × 15
      + kuskvinst% 2025          × 10
      + tränarvinst% 2025        × 5
      + startspår-bonus          × 5
```

Startspår-bonusen ger innerspår full effekt vid voltestart och halv effekt vid autostart. Topp-3 per lopp rankas efter score. Inforutan i sidans fot förklarar motiveringarna.

## Sidans struktur

Genererad `index.html` innehåller tre delar:

1. **Dagens program** — översikt av spelformerna (GS75, V4, V3, DD) och vilka lopp som ingår i varje.
2. **Topp-3 per lopp** — rankad lista med motivering, odds och marknadsfavorit-tagg.
3. **Så räknas tipsen fram** — expanderbar inforuta med formel och motiveringslogik.

## Vad den INTE tar hänsyn till

- Banans längd och karaktär
- Skobyten och sulky-ändringar
- Väderlek
- Senaste 3–5 starternas trend (vi använder hela 2026 samlat)
- Motståndarnas relativa styrka (ingen normalisering mot fältet)
- Spelmarknadens signaler (odds visas bara som jämförelse, påverkar inte rankingen)

## Struktur

```
v75-predictor/
├── README.md
├── HYPOTHESIS.md                 # huvudhypotes: kan enkel heuristik ranka hästar?
├── predict.py                    # hämtar data, rankar, skriver index.html
├── index.html                    # genererad tipssida
└── experiments/
    ├── odds-check/               # jämför vår ranking mot oddsfavoriterna
    │   ├── HYPOTHESIS.md
    │   └── odds_check.py
    └── result-check/             # post-lopp-utvärdering (körs efter avgjorda lopp)
        └── HYPOTHESIS.md
```

## ATG API

Endpoints som används (inga auth-krav):

- `.../calendar/day/{YYYY-MM-DD}` — lista banor och lopp per dag
- `.../races/{raceId}` — komplett startfält + häststatistik
- `.../games/vinnare_{raceId}` — aktuella vinnar-odds
- `.../games/{TYPE}_{raceId}` — poolspel: `GS75`, `V4`, `V3` (versaler) eller `dd` (gemener). `raceId` är första loppet i spelet, och responsen listar alla ingående lopp.

`raceId`-formatet: `{YYYY-MM-DD}_{trackId}_{raceNumber}`.

## Status

Experimentellt. Inget spelråd — sidan är byggd för att testa om publik statistik räcker som grund, inte för att slå spelmarknaden. Se `experiments/odds-check/HYPOTHESIS.md` för hur modellen står sig mot oddsen (spoiler: ~29 % överlapp, behöver fler signaler).
