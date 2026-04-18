---
title: V75 Duglighetspredikator
description: Kan vi hämta data och ranka hästar för V75-lopp så användaren får spelbara tips?
category: tech-spike
status: confirmed
last_updated: 2026-04-18
sections: [Hypothesis, Test, Success Criteria, Time Budget, Result]
---

# V75 Duglighetspredikator

## Hypothesis
ATG har en öppen JSON-endpoint som ger oss tillräckligt med data (startfält, statistik, tränare) för att räkna ut en enkel duglighetsranking per V75-lopp.

## Test
Skriv ett script som hämtar ett riktigt kommande V75-lopp (GS75 på Årjäng 2026-04-19), räknar en enkel score per häst baserat på publik statistik, och skriver ut topp 3 per lopp.

## Success Criteria
- Vi kan hämta strukturerad data för ett kommande lopp utan auth/scraping.
- Varje häst får en siffra.
- Topp 3 per lopp ser rimliga ut (inte random ordning).

## Time Budget
15 min. Stop om vi behöver ett fjärde skript eller börjar bygga UI.

## Result
- **Status**: Confirmed
- **What we learned**:
  - ATG har öppet API: `https://www.atg.se/services/racinginfo/v1/api/races/{date}_{trackId}_{raceNo}` ger komplett startfält med häststatistik (karriär + årsvis), tränare och tränarstatistik, kusk, skor, sulky, distans, startmetod.
  - Kalender-endpoint (`/calendar/day/{date}`) listar alla banor + race-ids för dagen. Enkelt att iterera.
  - En enkel heuristik (karriärvinstprocent + senaste årets intjäning + form + tränarvinstprocent) ger klar ranking — favoritern rankas överst i varje lopp, inte slump.
  - Spel-endpoints (`/games/V75_...`, `/products/V75/upcoming`) är tomma — men vi behöver inte dem, races räcker.
  - Testlopp: Årjäng 2026-04-19 (GS75). Lopp 7: Remjahn topprankad med 83 % karriärvinst.
- **Decision**: Keep — tekniken är bevisad. Nästa experiment: UX-slice där en användare ser tipsen och säger om de är spelbara. När UX:n är validerad: bygg riktig prediktor (fler faktorer, backtesta på historisk data, kolla om ranking slår favoritodds).
