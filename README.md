# AI in een paar minuten

Elke ochtend om 08:00 een zakelijk AI-nieuwsbulletin van een paar minuten: eerst Nederland, dan wereldwijd, en tot slot de kansen in de markt. Je luistert in een web-app op je iPhone-beginscherm.

## Hoe het werkt

1. **08:00, Claude (geplande taak):** zoekt het AI-nieuws, schrijft het script volgens `tools/redactie.md` en zet `episodes/JJJJ-MM-DD.json` in deze repo.
2. **GitHub Action:** ziet het nieuwe script, maakt de mp3 met ElevenLabs (model `eleven_v4`) en werkt `episodes/index.json` bij.
3. **GitHub Pages:** publiceert de app met de nieuwe aflevering. Na een paar minuten staat hij op je iPhone.

## Eenmalig instellen

### 1. GitHub-account en repo

1. Maak een gratis account op [github.com](https://github.com).
2. Kies rechtsboven **+ › New repository**.
3. Naam: `ai-nieuws-podcast`, zichtbaarheid **Public**, verder niets aanvinken. Klik **Create repository**.

> Public is nodig voor gratis GitHub Pages. De afleveringen zijn daardoor openbaar op internet.

### 2. Bestanden in de repo zetten

Makkelijkst: koppel GitHub aan Claude en laat Claude de bestanden plaatsen.

Zelf doen kan ook: kies in de lege repo **uploading an existing file** en sleep de inhoud van deze map erin, inclusief de map `.github`. Controleer daarna dat `.github/workflows/podcast.yml` in de repo staat.

### 3. ElevenLabs

1. Log in op [elevenlabs.io](https://elevenlabs.io). Maak onder je profiel een **API key** aan. Geef de sleutel alleen rechten voor tekst-naar-spraak en stemmen lezen.
2. Kies een stem: open de **Voice Library**, filter op Nederlands en zoek een rustige, zakelijke nieuwsstem. Voeg die toe aan je stemmen en kopieer de **Voice ID**.
3. Reken op ongeveer 4.500 tekens per dag, dus zo'n 140.000 per maand. Controleer of je abonnement dat dekt.

### 4. Geheimen en Pages in GitHub

1. In de repo: **Settings › Secrets and variables › Actions › New repository secret**.
   - `ELEVENLABS_API_KEY`: je API key
   - `ELEVENLABS_VOICE_ID`: de Voice ID
2. **Settings › Pages › Build and deployment › Source:** kies **GitHub Actions**.
3. **Settings › Actions › General › Workflow permissions:** kies **Read and write permissions** en sla op.
4. Ga naar **Actions › Podcast maken en publiceren › Run workflow** voor een eerste publicatie.

### 5. Op je iPhone

1. Open `https://JOUW-GEBRUIKERSNAAM.github.io/ai-nieuws-podcast/` in Safari.
2. Tik op de deelknop en kies **Zet op beginscherm**.

De app opent dan schermvullend met een eigen icoon. Afspelen gaat door met het scherm vergrendeld en is te bedienen vanaf het vergrendelscherm.

## Aanpassen

- **Stem, model of instellingen:** `tools/config.json`. `stability` hoger maakt de stem vlakker en rustiger.
- **Inhoud en toon:** `tools/redactie.md`. Claude leest dit bestand elke ochtend.
- **Bewaartermijn:** `keepDays` in `tools/config.json` (standaard 60 dagen).

## Problemen oplossen

| Wat je ziet | Oplossing |
| --- | --- |
| Geen nieuwe aflevering in de app | Kijk bij **Actions** of de laatste run rood is en open de foutmelding. |
| `Model eleven_v4 niet gevonden` | Je ElevenLabs-abonnement heeft v4 niet. Zet `model` tijdelijk op `eleven_v4_turbo` of `eleven_multilingual_v2`. |
| `HTTP 401` | API key klopt niet of mist rechten. Vervang het secret. |
| `git push` faalt in de Action | Stap 4.3: workflow-rechten op Read and write. |
| Oude versie van de app | Sluit de app helemaal af en open opnieuw. |

## Bestanden

```
index.html              de app (speler, archief, animaties)
manifest.webmanifest    beginscherm-instellingen
sw.js                   offline werken
icons/                  app-iconen
episodes/               scripts per dag + index.json voor de app
audio/                  mp3's (gemaakt door de Action)
tools/make_episode.py   ElevenLabs-aanroep en index opbouwen
tools/config.json       stem en model
tools/redactie.md       redactie-instructie voor Claude
.github/workflows/      de GitHub Action
```
