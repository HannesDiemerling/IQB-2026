# Jenseits des Frequentismus: Vom p-Wert zur Posterior

Workshop 7 beim **IQB 2026**, am 23. und 24. September, jeweils 14 bis 18 Uhr,
online über Zoom, für 25 Teilnehmende.

Dieses Repository enthält das komplette Material: eine Website mit
interaktiven Anwendungen und Arbeitsblättern, dazu ein Foliendeck je
Workshop-Tag. Alles wird von einem Quarto-Projekt gebaut und über GitHub
Pages veröffentlicht.

## Worum es geht

Der Workshop soll für die Probleme im Umgang mit p-Werten und Effektstärken
sensibilisieren und Alternativen anbieten. Er ist semi self-paced angelegt:
Input im Plenum, dann Gruppenarbeit an interaktiven Anwendungen im Browser,
danach kurzes Zusammentragen.

**Tag 1, die Diagnose**

1. Was der p-Wert nicht sagt
2. Die Freiheitsgrade des Forschens
3. Effektstärken und ihre Grenzen

**Tag 2, die Alternative**

4. Die Frage umdrehen
5. Prior, Likelihood, Posterior
6. Evidenz berichten

Jede Einheit hat ein Arbeitsblatt und zwei bis vier Anwendungen. Die Aufgaben
tragen aufklappbare Auffrischungen für fehlende Grundlagen und aufklappbare
Lösungen, damit keine Gruppe hängen bleibt.

## Das durchgehende Beispiel

**LeseStark**, ein fiktives Leseförderprogramm, gemessen mit einem
Lesekompetenztest (Rohwerte 0 bis 25, Mittelwert rund 12, Streuung rund 5,
Reliabilität .70). Die zentrale Studie hat 45 Lernende je Gruppe und findet
2,1 Punkte Zuwachs, also d = 0.42.

Diese Zahlen ziehen sich durch alle sechs Einheiten und ergeben am Ende den
Ergebnissatz auf der Schlussfolie. Sie stehen an genau einer Stelle:
`iqb2026-w7/_includes/szenario.qmd`.

## Was wo liegt

| Pfad | Inhalt |
|---|---|
| `iqb2026-w7/index.qmd` | Startseite für die Teilnehmenden |
| `iqb2026-w7/tag1/`, `tag2/` | sechs Arbeitsblätter |
| `iqb2026-w7/apps/` | 19 interaktive Anwendungen |
| `iqb2026-w7/folien/` | zwei Reveal.js-Decks, eines je Tag, mit Moderationsnotizen |
| `iqb2026-w7/leitung/` | **Moderationsleitfaden**, nicht in der Navigation |
| `iqb2026-w7/_includes/` | Szenario, Auffrischungen, Ladehinweis |
| `iqb2026-w7/tools/` | zwei Prüfskripte |
| `iqb2026-w7/_entwicklung.md` | Konventionen und Autorenmuster |
| `.github/workflows/` | der Build, muss hier oben liegen |

Der [Moderationsleitfaden](iqb2026-w7/leitung/index.qmd) ist die erste Adresse
vor dem Termin: Deckliste, Tastenkürzel, minutengenaue Zeitplanung, die
Vorwärm-Checkliste für die Anwendungen und ein Plan B je Block.

## Bedienung

Die Anwendungen laufen als **Shinylive** im Browser der Teilnehmenden, über
Pyodide. Es gibt keinen Server, nichts zu installieren, und die Daten bleiben
lokal.

```bash
cd iqb2026-w7

python -m venv .venv                                  # Python 3.12 nötig
./.venv/Scripts/python.exe -m pip install -r requirements.txt

./.venv/Scripts/python.exe tools/check-konventionen.py   # Sprache, Pfade, Callouts
./.venv/Scripts/python.exe tools/check-apps.py           # Syntax der Anwendungen

quarto render                                         # baut nach _site/
quarto preview                                        # lokal anschauen
```

Beide Prüfskripte laufen auch in der GitHub Action und brechen den Build ab.
`check-apps.py` ist das wichtigere: ein Python-Fehler in einer Anwendung fällt
beim Rendern **nicht** auf, er scheitert erst im Browser.

**Deploy** passiert automatisch bei jedem Push auf `main`. Voraussetzung im
Repo: Settings → Pages → Source auf **GitHub Actions**, nicht auf einen
Branch.

## Gut zu wissen

- **Python 3.12 ist Pflicht.** numpy und scipy sind auf Versionen gepinnt, die
  das verlangen.
- **Der erste Build dauert lange**, weil Shinylive seine Browser-Laufzeit
  herunterlädt (rund 45 MB). Danach greift der Cache.
- **Die Shinylive-Extension ist mitversioniert** unter `_extensions/`. Kein
  `quarto add` im Build, damit kein ungepinnter Netzabruf im kritischen Pfad
  liegt.
- **Nur ASCII und deutsche Umlaute im Code der Anwendungen.** Der
  Shinylive-CLI ist beim Einlesen encodingempfindlich; tiefgestellte Ziffern
  haben den Build schon einmal hart abgebrochen.
- **Keine wurzelabsoluten Pfade.** Unter einer Pages-Projektseite zeigt
  `href="/..."` ins Leere. Das Prüfskript fängt es ab.
- **`site-url` in `iqb2026-w7/_quarto.yml`** muss zum Repo-Namen passen.
- `workshops/` ist aus der Versionierung ausgeschlossen. Dort liegen die
  Vorgänger-Repos, aus denen das Material stammt.

## Lizenz und Herkunft

Alle Inhalte stehen unter **CC BY 4.0** und dürfen weiterverwendet, umgebaut
und in eigener Lehre eingesetzt werden.

Die Grundlagen stammen aus dem Projekt *Beyond p-values* an der HMU Health and
Medical University Erfurt, gefördert von der VolkswagenStiftung in der
Förderlinie Pioniervorhaben. Für das IQB neu geschnitten und auf die
Bildungsforschung übertragen.
