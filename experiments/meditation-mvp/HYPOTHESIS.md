---
title: Meditation MVP — content-first prototyp
description: Räcker en JSON-katalog + statisk HTML-spelare för att testa ett personligt meditationsbibliotek där licens är förstklassdata?
category: ux-spike
status: in-progress
last_updated: 2026-05-07
sections: [Hypothesis, Test, Success Criteria, Time Budget, Result]
---

# Meditation MVP

## Hypothesis
En personlig meditationsapp behöver inte ett backend för att vara användbar.
En `catalog.json` med fullständig metadata (titel, lärare, längd, språk, källa,
licens, attribution, anteckningar) plus en statisk HTML-spelare räcker för att:

1. Importera egna MP3-filer.
2. Lista publika källor som måste licensgranskas innan import.
3. Spela upp, favoritmarkera och se senast spelade.

Hypotesen testar en starkare delprincip: **licens är inte fotnot, det är ett
fält som styr UI-flödet.** Spår med `license_status: pending-review` får aldrig
spelas upp — bara visas som "att granska". Spår får inte hamna i biblioteket
av misstag genom auto-import.

## Test
Bygg minsta möjliga vertikala slice:
- Datamodell i `catalog.json` med 4 spår (2 lokala, 2 pending-review externa).
- `index.html` läser katalogen, listar spår, filtrerar på licensstatus + favoriter.
- HTML5 `<audio>` spelar upp lokala filer.
- `localStorage` håller favoriter och senaste uppspelningstid.
- Inga auto-importer, inga fjärr-fetches av spår.

## Success Criteria
- Katalogen kan utökas genom att lägga till ett objekt + en MP3 — utan kodändring.
- Externa exempel visas tydligt som **EJ NEDLADDADE** och kan inte spelas.
- Favorit och "senast spelad" persisterar mellan reloads.
- En person utan teknisk bakgrund kan läsa README och förstå "hur lägger jag till
  ett spår" och "varför kan jag inte bara klicka och importera från en hemsida".

## Time Budget
60 min. Stop om vi behöver bygga build-pipeline, paketera SPA, eller införa SQLite/server.

## Result
*Att fyllas i efter första slice är testad i webbläsare.*
