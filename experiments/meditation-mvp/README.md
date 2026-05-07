# Meditation MVP

Content-first prototyp för ett personligt meditationsbibliotek. Inget backend,
ingen build-pipeline. En statisk HTML-sida läser `catalog.json` och spelar upp
lokala MP3-filer. Favoriter och senast spelade sparas i `localStorage`.

## Syfte

Testa om en katalog-i-JSON + statisk spelare räcker för att:

- samla egna meditationer på ett ställe,
- registrera **licens som förstklassdata**,
- lista publika källor som måste granskas innan de får importeras,
- spela upp, favoritmarkera, se senaste lyssning.

Detta är ett experiment — inte en app som ska distribueras. Se
`HYPOTHESIS.md` för testpremiss och stoppkriterier.

## Kör

Mappen behöver serveras över HTTP (annars blockerar webbläsaren `fetch`):

```bash
cd experiments/meditation-mvp
python3 -m http.server 8000
# Öppna http://localhost:8000/
```

## Struktur

```
experiments/meditation-mvp/
├── README.md
├── HYPOTHESIS.md
├── catalog.json          # Source of truth: alla spår + metadata + licensstatus
├── index.html            # Bibliotek + spelare (vanilj-JS, ingen build)
├── _make_silence.py      # Engångsskript som genererade placeholder-MP3:erna
└── tracks/
    ├── placeholder-breath-5min.mp3      # Tyst MP3 — byts ut mot riktig fil
    └── placeholder-bodyscan-10min.mp3   # Tyst MP3 — byts ut mot riktig fil
```

## Licensprinciper

1. **Varje spår har explicit `license_status`.** Inget spår är "default ok".
   Statusvärden:
   - `cleared` — verifierad licens, fri att spela. Personlig användning räknas.
   - `pending-review` — katalogpost finns, men källan är inte granskad. Filen
     finns inte lokalt och spår med denna status **kan inte spelas** i UI:t.
   - `blocked` — granskad och avvisad. Behålls i katalogen så vi inte
     importerar samma sak igen av misstag.
2. **Inga blinda nedladdningar.** Appen hämtar aldrig audio från externa URL:er
   automatiskt. Externa poster är *referenser* tills någon manuellt laddat ner,
   verifierat licensvillkoren och uppdaterat statusen till `cleared`.
3. **Attribution är ett fält, inte ett antagande.** Om licensen kräver
   attribution måste `attribution`-fältet fyllas i innan statusen sätts till
   `cleared`.
4. **`personal-use` är inte distribuerbart.** Spår markerade så får inte
   committas in om repot någonsin blir publikt med innehåll. Just nu commitar
   vi bara tysta platshållare.

## Importera en egen MP3

1. Lägg filen i `tracks/` (eller en undermapp).
2. Lägg till ett objekt i `catalog.json` under `tracks`. Alla fält:

   ```json
   {
     "id": "unik-slug-utan-mellanslag",
     "title": "Visningstitel",
     "teacher": "Lärare eller källa",
     "source": "Egen / Insight Timer / etc.",
     "duration_seconds": 600,
     "category": "breath | body-scan | loving-kindness | ...",
     "language": "sv | en | ...",
     "path": "tracks/min-fil.mp3",
     "source_url": null,
     "license": "personal-use | CC-BY | CC0 | ...",
     "license_status": "cleared",
     "attribution": "Text som ska visas vid uppspelning, eller null",
     "notes": "Fri text",
     "added": "ÅÅÅÅ-MM-DD"
   }
   ```

3. Ladda om sidan. Inget byggsteg.

## Granska en publik källa innan import

Lägg först till en post med `license_status: "pending-review"` och `path: null`.
Spåret blir då synligt i biblioteket som "att granska", men kan inte spelas.
Innan du flyttar det till `cleared`:

1. **Hitta den faktiska licenstexten** på källans sida (CC, public domain,
   "free for personal use", egen TOS). Skärmdumpa eller spara länken — sidor
   ändras.
2. **Tolka villkoren.** Tillåts privat lyssning? Distribution? Modifiering?
   Skriv slutsatsen i `notes`.
3. **Kontrollera attribution-krav.** CC-BY kräver namn + källa + licens.
   Fyll i `attribution`. Om kravet inte kan uppfyllas → `blocked`, inte
   `cleared`.
4. **Ladda ner manuellt** till `tracks/` och sätt `path`. Aldrig automatiskt
   från koden.
5. Sätt `license_status: "cleared"`. Behåll `source_url` så provenance finns
   kvar.

Om du är osäker — `blocked` är säkrare än `cleared`.

## Datamodell (kort)

`catalog.json` har två toppnycklar:

- `schema_version` — versionsnummer, börja på `1`. Höj vid breaking changes.
- `license_statuses` — dokumenterade värden för `license_status`.
- `tracks[]` — alla spårposter.

Fält per spår: se "Importera en egen MP3" ovan.

## Vad MVP:n medvetet inte gör

- Ingen sökning, ingen taggfiltrering bortom licens/favorit.
- Ingen progress-bar utöver `<audio controls>`.
- Inga playlists, inga sessioner, ingen påminnelse.
- Ingen mobil-app, ingen PWA, inget offlineläge utöver vad statisk HTML ger.
- Ingen auto-import från någon källa.

Lägg till sånt först när hypotesen i `HYPOTHESIS.md` är bekräftad.
