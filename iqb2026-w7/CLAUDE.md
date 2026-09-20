# Workshop 7: Jenseits des Frequentismus

IQB 2026, 23. und 24. September, jeweils 14 bis 18 Uhr. 25 Teilnehmende,
online über Zoom. Ein Quarto-Website-Projekt, veröffentlicht über GitHub
Pages.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `folien/` | 10 Reveal.js-Decks, Format kommt aus `folien/_metadata.yml` |
| `apps/` | 19 Shinylive-Anwendungen, eine Datei je Anwendung |
| `tag1/`, `tag2/` | 6 Arbeitsblätter für die Gruppenphasen |
| `_includes/` | Bausteine, werden nicht gerendert (Unterstrich-Regel) |
| `_includes/auffrischen/` | 12 Auffrischungen, **nur HTML**, nie in Decks |
| `leitung/` | Moderationsleitfaden, bewusst nicht in der Navigation |
| `tools/` | zwei Prüfskripte, laufen lokal und in der Action identisch |
| `_extensions/` | Shinylive-Extension, **versioniert**, kein `quarto add` im Build |

## Die vier Regeln, die wirklich beißen

**1. `filters`, `theme`, `css`, `toc` und `embed-resources` bleiben unter
`format.html`.** Auf oberster Ebene lecken sie in jedes Format, auch in die
Decks.

**2. Jedes `{{< include >}}` beginnt mit einem Slash.** Relative Includes
lösen gegen das **Top-Level-Dokument** auf, nicht gegen die Partialdatei. Im
Vorgängerprojekt hat genau das zugeschlagen. Der Prüfer erzwingt es.

**3. `collapse="true"` funktioniert in Reveal.js nicht.** Der
Revealjs-Callout-Renderer liest das Attribut nie. Aufklappbare Kästen gehören
ausschließlich auf HTML-Seiten. In einem Deck stünden sie stumm dauerhaft
offen. Außerdem braucht jeder aufklappbare Callout einen **expliziten Titel**,
sonst wird `collapse` stillschweigend ignoriert.

**4. `embed-resources: false` muss gesetzt bleiben.** Sonst verweigert der
Shinylive-Filter die Umwandlung, und der Python-Code landet als roher Text auf
der Seite.

## Pfade

- **Markdown-Links** zeigen auf `.qmd`, Quarto schreibt sie um:
  `[Text](../apps/a01-schwelle.qmd)`
- **In Folienattributen** expandiert Quarto nichts. Dort stünden von Hand
  geschriebene `.html`-Pfade. Aktuell gibt es keine, weil die Demo-Folien
  keine iframes einbetten.
- **Nie wurzelabsolut.** `href="/apps/..."` funktioniert in der Vorschau und
  bricht unter der Pages-Projektseite unter `/REPO/`. Der Prüfer fängt das im
  gerenderten Output ab.

## Sprache

Deutsch, **Du-Form**, geschlechtsneutral **ohne Sonderzeichen** (keine
`:innen`), **keine Gedankenstriche**. Gilt auch für Speaker-Notes.

Ersatzschema für den Gedankenstrich: Komma bei Apposition, Doppelpunkt bei
Erklärung, Punkt und neuer Satz beim Bruch, Mittelpunkt `·` als Trenner in
Aufzählungen.

Statt "self-paced" heißt es "im eigenen Tempo".

## Das Szenario

Eine einzige Quelle: `_includes/szenario.qmd`. Wer eine Zahl ändert, ändert
sie dort.

**LeseStark**, Leseförderprogramm. Lesekompetenztest, Rohwerte 0 bis 25,
Mittelwert rund 12, Streuung rund 5, Reliabilität .70. Zentrale Studie:
45 Lernende je Gruppe, Zuwachs 2,1 Punkte, d = 0.42, Relevanzschwelle
3 Punkte.

Das Material stammt aus dem Vorgängerprojekt "Beyond p-values", wo das
durchgehende Beispiel "SmartRail / ICE-Verspätungen" war. Beim Port wurden
**nur Beschriftungen** getauscht, keine Zahlen, mit zwei dokumentierten
Ausnahmen:

- **`a01` und `a02`** sind auf die Folien kalibriert: n = 45 statt 30,
  Streuung Nord 4,96 und Süd 5,10, plus eine Normierung der Stichproben-SD.
  Nur so liefert die Anwendung die p-Werte .048 und .054, die auf der Folie
  stehen.
- **`a08`** rechnete in Sekunden und teilte durch 60 und 3600. In Punkten gibt
  es diese Faktoren nicht. Der Regler arbeitet jetzt in Hundertstelpunkten,
  der Rechner liefert Kosten je Kompetenzpunkt.

## Anwendungen schreiben

Muster, aus dem Bestand übernommen:

```python
app_ui = ui.page_fluid(ui.card(
    ui.card_header("LeseStark: ..."),
    ui.layout_columns(
        ui.div(ui.h5("..."), ui.input_slider(...), ui.hr(), ui.output_ui("info_panel")),
        ui.output_plot("main_plot"),
        col_widths=(4, 8))))
```

Dazu `#| standalone: true`, `#| viewerHeight: N`, ein `@render.plot` und
optional ein `@render.ui`-Urteilspanel mit `background:#f8f9fa`.

**Plot-Regeln** (aus `claudeplot.md` des Vorgängerprojekts):

- immer `layout="constrained"`, nie `tight_layout`
- x-Grenzen fest verdrahten, damit die Skala beim Reglerziehen nicht springt
- Dichteachsen: `set_yticks([])` und `set_ylim(0, y.max() * 1.2)`
- bedeutungstragende Achsen: feste Ticks plus Kopffreiheit für Wertelabels
- Annotationen über `ax.get_xaxis_transform()`, nicht über Datenkoordinaten
- Spines oben und rechts aus

**Nur ASCII im App-Code jenseits deutscher Umlaute.** Der Shinylive-CLI ist
beim Lesen des Blocks encodingempfindlich. Tiefgestellte Ziffern wie `₁₀`
haben den Build hart abgebrochen. `BF10` statt `BF₁₀`.

**Ladehinweis** über `{{< include /_includes/banner-laden.qmd >}}`. Er ist
klassenbasiert, nicht id-basiert. Die Bestandsfassung nutzte eine id, was bei
zwei Anwendungen auf einer Seite gebrochen wäre.

## Prüfen

```bash
python tools/check-konventionen.py   # Sprache, Includes, Callouts, Pfade
python tools/check-apps.py           # Syntax und Konventionen der App-Bloecke
```

`check-apps.py` ist wichtig: ein Python-Fehler in einem Shinylive-Block fällt
beim Rendern **nicht** auf. Quarto reicht den Code unverändert weiter, und
erst der Browser der Teilnehmenden scheitert daran. Ohne Browsertest ist das
die größte ungesicherte Fehlerquelle.

Beide Skripte laufen auch in der Action und brechen den Build ab.

## Lokal bauen

Python ist auf der Entwicklungsmaschine nicht global installiert. Eine
projektlokale Umgebung liegt unter `.venv` und ist gitignored:

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
quarto render
```

Der erste Render lädt die Shinylive-Laufzeit herunter und dauert mehrere
Minuten. Üblicherweise wird über den Deploy validiert, nicht lokal.

## Offene Punkte

- Der Remote ist noch nicht angelegt. `site-url` in `_quarto.yml` steht auf
  `iqb2026-w7` und muss zum tatsächlichen Repo-Namen passen.
- Die Anwendungen sind noch nie in einem echten Browser gestartet worden. Das
  ist die verbleibende Sichtprüfung vor dem Termin.
