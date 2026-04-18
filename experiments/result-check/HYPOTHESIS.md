---
title: V75 Resultatkoll — var avvikelsen värd något?
description: Efter loppen på Årjäng 2026-04-19 — jämför vår topp-3 och marknadens topp-3 mot de faktiska placeringarna. Avgör om vår avvikelse är värdefull eller brus.
category: tech-spike
status: pending
last_updated: 2026-04-18
sections: [Hypothesis, Test, Success Criteria, Time Budget, Result]
depends_on: v75-prediction, v75-odds-check
---

# V75 Resultatkoll

## Hypothesis
Efter att loppen är körda kan vi säga säkert om vår heuristik tillför värde eller bara brus. Specifikt:

- **H1**: Vår topp-3 får fler träffar (pallplats eller vinst) än slumpen (~3/14 × 3 ≈ 64 % per lopp att någon av våra tre hamnar bland de tre första).
- **H2**: Vår topp-3 är **lika bra eller bättre** än marknadens topp-3 på pallträffar.
- **H3**: I lopp där vi starkt avvek från marknaden (< 33 % överlapp) — hur gick det?

## Test
Efter loppen 2026-04-19 (sista lopp ca 19:00):

1. Hämta `/races/{id}` för varje lopp — när `status` = `"results"` finns `result`-fältet med placeringarna.
2. För varje lopp:
   - Notera vilka av **våra** topp-3 som kom 1, 2, 3 (och vilken av dem som vann).
   - Notera vilka av **marknadens** topp-3 som kom 1, 2, 3.
3. Sammanställ totalsiffror:
   - Antal pallträffar (av 3 × 7 = 21 möjliga) för oss vs. marknaden.
   - Antal vinsttreff.
   - Genomsnittlig "pris-för-spelad-krona" om man spelat vinnare på topp-3 per lopp (indikativ, inte strikt).

## Success Criteria
Observerbart efter loppen:

| Utfall | Tolkning |
|---|---|
| Våra pallträffar > marknadens | **Hypotes bekräftad** — heuristiken är värdefull trots sin enkelhet. Iterera vidare med fler signaler. |
| Jämnt | Vi är lika bra, billigare modell. Kan ha nisch-värde (t.ex. outsider-tips). |
| Marknadens pallträffar >> våra | **Hypotes falsifierad** — marknaden vet mer. Vårt värde begränsas till utbildning/transparens, inte vinstoptimering. |

Konkret nivå för "bättre": minst 2 fler pallträffar av 21 (≈ 10 pp). Mindre = brus i ett enda loppdagsprov.

## Time Budget
15 minuter. En fil (`result_check.py`), återanvänder samma endpoints som de två tidigare sliceverna.

## Notes / constraints
- Ett enda loppdagsprov (7 lopp, 21 topp-3-slots) är **för litet statistiskt underlag**. Detta är en första sanitykoll, inte en vetenskaplig slutsats.
- För robust svar krävs ett historiskt dataset — kör samma jämförelse på 20–50 dagars V75-historik.
- Skippar avkastningsberäkning i minimalsliceven (komplexitet: insats per häst, kombinationer, etc).

## Result
_Fylls i efter 2026-04-19 ca 19:00._
