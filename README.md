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
TRACK = 31           # Årjäng — andra banor: se /api/calendar/day/{YYYY-MM-DD}
RACES = [4, 5, 6, 7, 8, 9, 10]
```

## Score-formel

Varje häst får en poäng byggd på fyra publika statistikfält:

```
score = karriärvinst%         × 60
      + intjänat 2026 (tkr/10) × 20
      + form 2026              × 15
      + tränarvinst% 2025      × 5
```

Topp-3 per lopp rankas efter score. Inforutan i sidans fot förklarar motiveringarna.

## Vad den INTE tar hänsyn till

- Startspår
- Banans längd och karaktär
- Kuskens form
- Skobyten och sulky-ändringar
- Väderlek
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

- `https://www.atg.se/services/racinginfo/v1/api/calendar/day/{YYYY-MM-DD}` — lista banor och lopp per dag
- `https://www.atg.se/services/racinginfo/v1/api/races/{raceId}` — komplett startfält + häststatistik
- `https://www.atg.se/services/racinginfo/v1/api/games/vinnare_{raceId}` — aktuella vinnar-odds

`raceId`-formatet: `{YYYY-MM-DD}_{trackId}_{raceNumber}`.

## Status

Experimentellt. Inget spelråd — sidan är byggd för att testa om publik statistik räcker som grund, inte för att slå spelmarknaden. Se `experiments/odds-check/HYPOTHESIS.md` för hur modellen står sig mot oddsen (spoiler: ~29 % överlapp, behöver fler signaler).
