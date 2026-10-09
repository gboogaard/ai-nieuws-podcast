# Redactie-instructie AI in 5

Deze instructie volgt de geplande taak elke ochtend. Het resultaat is één bestand: `episodes/JJJJ-MM-DD.json` (de datum van vandaag, Europe/Amsterdam). Daarna commit en push naar `main`; GitHub maakt de audio en publiceert.

## Doel

Een zakelijk nieuwsbulletin van vijf minuten over AI, voorgelezen in het Nederlands. Luisteraars zijn professionals en ondernemers. Ze willen weten wat er gebeurde, wat het voor hen betekent en waar kansen liggen.

## Onderzoek

1. Zoek nieuws van de afgelopen 24 uur (maandag: sinds vrijdagochtend). Gebruik meerdere zoekopdrachten.
2. **Nederland eerst**: overheid en toezicht (AP, RDI, ministeries), Nederlandse bedrijven en start-ups, onderwijs, zorg, publieke sector, onderzoek (TNO, universiteiten), Nederlandse nieuwsbronnen (NOS, FD, NRC, Volkskrant, Emerce, Computable, AG Connect, Tweakers, Dutch IT Channel). Ook EU-nieuws dat Nederland direct raakt (AI Act).
3. **Wereldwijd**: grote modelreleases, bedrijfsnieuws, regelgeving, onderzoek, investeringen.
4. Open de artikelen die je gebruikt. Neem alleen feiten op die in de bron staan. Geen geruchten als feit; noem een gerucht een gerucht.
5. Kies 2 tot 3 Nederlandse en 2 tot 3 internationale onderwerpen. Is er weinig Nederlands nieuws, maak dan het Nederlandse blok korter, maar sla het niet over.
6. Controleer of het nieuws niet al in de afleveringen van de afgelopen drie dagen stond (`episodes/`). Alleen herhalen als er echt iets nieuws is.

## Opbouw en lengte

Totaal **650 tot 750 woorden** (ongeveer vijf minuten).

| Onderdeel | Woorden | Inhoud |
| --- | --- | --- |
| intro | 30-45 | "Goedemorgen. Het is [weekdag] [datum]. Dit is AI in 5." Daarna in één zin de drie hoofdpunten. |
| sectie `nl` | 220-260 | Nederlands AI-nieuws. Per bericht: wat gebeurde er, waarom telt het, één praktisch voorbeeld. |
| sectie `wereld` | 220-260 | Internationaal nieuws, steeds vertaald naar de Nederlandse praktijk, met een praktisch voorbeeld. |
| sectie `kansen` | 120-160 | Twee of drie concrete marktkansen die uit het nieuws volgen: voor wie, wat je kunt doen, waarom nu. |
| outro | 20-35 | Korte afsluiting: "Dat was AI in 5. Morgen om acht uur weer." |

## Toon: zakelijk nieuwsbulletin

- Schrijf voor het oor: korte zinnen (gemiddeld 12-15 woorden), actieve vorm, één gedachte per zin.
- Rustig, zakelijk en neutraal, zoals een radionieuwslezer. Geen hype, geen uitroeptekens, geen grapjes.
- Spreek de luisteraar aan met "u".
- Overgangen tussen blokken: "Dan het nieuws uit het buitenland." en "Tot slot: de kansen."
- Bronvermelding in de gesproken tekst kort: "meldt het FD", "volgens de NOS".
- Getallen uitschrijven zoals je ze uitspreekt: "twaalf miljoen euro", "vijfenveertig procent".
- Afkortingen die je uitspreekt als woord mogen; spel lastige afkortingen niet zelf uit.
- Geen opsommingstekens, haakjes, markdown, emoji of URL's in de gesproken tekst.

## Praktische voorbeelden en kansen

- Elk nieuwsbericht krijgt één concreet voorbeeld: "Een accountantskantoor kan hiermee …", "Voor een mbo-school betekent dit …".
- Kansen zijn specifiek en uitvoerbaar, met een doelgroep. Niet: "AI biedt veel kansen." Wel: "Voor kleine webshops ligt er een kans in …, omdat …".
- Geen beleggingsadvies.

## Bestandsformaat

```json
{
  "date": "2026-10-10",
  "title": "Korte kop van max. 70 tekens over het belangrijkste nieuws",
  "summary": "Eén of twee zinnen over wat de luisteraar vandaag hoort.",
  "intro": "Goedemorgen. Het is zaterdag 10 oktober. Dit is AI in 5. …",
  "sections": [
    { "key": "nl", "title": "Nederland", "script": "Gesproken tekst. Alinea's scheiden met een lege regel (\\n\\n)." },
    { "key": "wereld", "title": "Wereldwijd", "script": "…" },
    { "key": "kansen", "title": "Kansen", "script": "…" }
  ],
  "outro": "Dat was AI in 5. Morgen om acht uur weer.",
  "items": [
    {
      "section": "nl",
      "headline": "Kop van het bericht",
      "takeaway": "Eén of twee zinnen: wat het betekent plus het praktische voorbeeld.",
      "source_name": "NOS",
      "source_url": "https://…"
    }
  ]
}
```

- `items`: één per nieuwsbericht (sectie `nl` of `wereld`) en één per kans (sectie `kansen`, `source_url` mag leeg zijn).
- Geldige JSON, UTF-8. Controleer na het schrijven met een JSON-parser en tel de woorden (intro + secties + outro).

## Publiceren

1. Schrijf `episodes/JJJJ-MM-DD.json`.
2. `git add episodes/JJJJ-MM-DD.json`, commit "Script JJJJ-MM-DD", `git pull --rebase`, `git push` naar `main`.
3. Maak verder niets aan: geen audio, geen wijzigingen aan `index.json` of de app.
4. Rapporteer in één alinea: kop van de dag, aantal woorden, en de bronnen.
