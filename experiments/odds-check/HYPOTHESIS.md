---
title: V75 Odds-koll — slår vi spelmarknaden?
description: Jämför vår heuristik-ranking mot ATG:s vinnarodds. Om vi alltid håller med marknaden tillför vi inget. Om vi avviker har vi antingen hittat värde eller har fel.
category: tech-spike
status: needs-iteration
last_updated: 2026-04-18
sections: [Hypothesis, Test, Success Criteria, Time Budget, Result]
---

# V75 Odds-koll

## Hypothesis
Vår enkla heuristik (karriärvinst + intjänat + form + tränare) tillför **information utöver** vad spelmarknaden redan vet via odds. Alltså: vår topp-3 kommer ibland att skilja sig från oddsfavoriterna, och minst några av dessa avvikelser kommer att vara motiverade.

**Nollhypotes**: Våra topp-3 är nästan alltid samma hästar som oddsfavoriterna. Då är vår modell redundant — spelmarknaden har redan priskodat samma signaler.

## Test
1. Hämta vinnar-odds per häst i samma 7 lopp (Årjäng 2026-04-19).
2. Per lopp: jämför vår topp-3 med de 3 hästarna med lägst odds (= marknadens favoriter).
3. Räkna **överlapp** (hur många av våra topp-3 finns bland odds-topp-3).
4. Lista **avvikelser**: hästar vi rankar högt men marknaden inte, och tvärtom.

Bonus om tiden räcker: spara utfallet och körresultat i en fil så vi kan jämföra mot faktiska resultat efter loppen.

## Success Criteria
Observerbart före loppen:
- Överlapp **≥ 70 %** → vår modell säger samma sak som marknaden. Heuristiken är rimlig men inte värdeadderande.
- Överlapp **40–70 %** → vi har en annan bild. Intressant — kolla motiveringen i avvikelserna.
- Överlapp **< 40 %** → vi är antingen geniala eller fel. Behöver efter-loppet-data.

Efter loppen (bonus):
- Våra val vinner oftare än oddsfavoriterna → hypotes bekräftad.
- Oddsfavoriterna vinner oftare → hypotes falsifierad, vår modell är sämre.
- Jämt → vår modell är lika bra men billigare att köra.

## Time Budget
20 minuter. Stop om:
- Odds-endpointen kräver auth eller är dold
- Det blir fler än 2 filer (HYPOTHESIS.md + odds_check.py)
- Vi börjar bygga UI innan siffrorna är verifierade i terminal

## Result
- **Status**: Needs iteration (tekniskt bevis klart, värdet är oklart tills vi har utfallsdata)
- **Utfall före loppen**: **6/21 överlapp = 29 %**. Kategori: "vilt avvikande".
- **Odds-endpoint**: `/services/racinginfo/v1/api/games/vinnare_{raceId}` → `races[0].starts[i].pools.vinnare.odds` i hundradelar (289 = 2,89). `9999` = ej satta / ej spelbar, filtreras bort.
- **Mönster i avvikelser**:
  - Vi matchar marknadens favorit ungefär varje lopp (6 av 7 gånger), men missar plats 2–3 systematiskt.
  - I Lopp 9 har marknaden en storfavorit (Eskils Balder, odds 1,39) som vår modell inte ens har i topp-3 — tydligt tecken på att vi saknar en bärande signal (troligen senaste-start-form, kusk-kvalitet, eller specifikt banpass).
  - I Lopp 8 är vi noll överens med marknaden.
- **Vad vi lärde oss**:
  - Heuristiken är inte redundant — den producerar en annan bild än spelmarknaden.
  - Men vi vet inte om "annorlunda" betyder "bättre" eller "sämre" utan att mäta mot faktiska resultat.
  - Enkla historiska mått (karriärvinst, årsintjäning, tränare) verkar fånga "vem som brukar vara bra" men missar "vem som är vass just idag".
- **Decision**: Iterate.
  - **Steg 1**: Efter loppen 2026-04-19 — hämta resultat (`/races/{id}` har `result` när status = results), räkna hur många av våra topp-3 och oddens topp-3 som faktiskt vann eller hamnade på prispallen. Då vet vi om avvikelsen var värdefull eller värdelös.
  - **Steg 2**: Lägg till signaler som marknaden verkar använda men vi saknar — senaste 5 startens placeringssumma, kusk-vinstprocent, och möjligen odds själva som en faktor i vår score (marknaden har info vi inte ser).
