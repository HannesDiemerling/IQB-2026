#!/usr/bin/env python3
"""Prueft die Sprach- und Struktur-Konventionen des Repos.

Laeuft ohne Abhaengigkeiten und ohne Render. Wird lokal und in der
GitHub Action identisch aufgerufen.

Geprueft wird:
  1. Keine Gedankenstriche (em dash), keine :innen-Formen. Gilt auch fuer
     Speaker-Notes.
  2. Jedes {{< include >}} beginnt mit einem Slash. Relative Includes loesen
     gegen das Top-Level-Dokument auf, nicht gegen die Partialdatei, und das
     bricht, sobald eine Datei verschoben wird.
  3. Keine aufklappbaren Auffrischungen in Foliendecks. Der Revealjs-Callout-
     Renderer liest 'collapse' nicht, der Kasten stuende dauerhaft offen.
  4. Jeder aufklappbare Callout hat einen expliziten Titel. Ohne Titel wird
     'collapse' stillschweigend ignoriert.
  5. Keine Reste von Platzhaltertexten.
  6. Im gerenderten _site keine wurzelabsoluten Pfade. Die wuerden unter einer
     GitHub-Pages-Projektseite ins Leere zeigen. Nur wenn _site existiert.

Aufruf:  python tools/check-konventionen.py
Rueckgabe: 0 wenn sauber, 1 sonst.
"""

from __future__ import annotations

import pathlib
import re
import sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
AUSGENOMMEN = {".venv", "_site", ".quarto", ".git", "_extensions", "tools"}

EM_DASH = "—"
GENDER = re.compile(r":innen|\*innen|_innen|:in\b")
INCLUDE = re.compile(r"\{\{<\s*include\s+([^\s>]+)")
CALLOUT_AUF = re.compile(r"^:::+\s*\{[^}]*collapse\s*=\s*[\"']true[\"'][^}]*\}")
PLATZHALTER = re.compile(r"GERÜST|TODO|FIXME|XXX")


def quelldateien():
    for p in sorted(WURZEL.rglob("*.qmd")):
        if any(teil in AUSGENOMMEN for teil in p.relative_to(WURZEL).parts):
            continue
        yield p


def pruefe_text() -> list[str]:
    fehler: list[str] = []
    for p in quelldateien():
        rel = p.relative_to(WURZEL).as_posix()
        zeilen = p.read_text(encoding="utf-8").split("\n")

        for i, z in enumerate(zeilen, 1):
            if EM_DASH in z:
                fehler.append(f"{rel}:{i}  Gedankenstrich gefunden")
            if GENDER.search(z):
                fehler.append(f"{rel}:{i}  Gendersonderzeichen gefunden")
            if PLATZHALTER.search(z):
                fehler.append(f"{rel}:{i}  Platzhalter gefunden")

            for ziel in INCLUDE.findall(z):
                if not ziel.startswith("/"):
                    fehler.append(
                        f"{rel}:{i}  Include ohne fuehrenden Slash: {ziel}"
                    )
                if rel.startswith("folien/") and "auffrischen/" in ziel:
                    fehler.append(
                        f"{rel}:{i}  Auffrischung in einem Deck: "
                        f"collapse wirkt in revealjs nicht"
                    )

            # Aufklappbarer Callout braucht einen Titel in der naechsten
            # nicht leeren Zeile.
            if CALLOUT_AUF.match(z):
                folge = next(
                    (t for t in zeilen[i : i + 4] if t.strip()), ""
                )
                if not folge.lstrip().startswith("#"):
                    fehler.append(
                        f"{rel}:{i}  collapse ohne expliziten Titel, "
                        f"wird stillschweigend ignoriert"
                    )
    return fehler


def pruefe_markdown() -> list[str]:
    """Keine .md-Datei darf als Website-Seite gerendert werden.

    Quarto rendert in einem Website-Projekt auch .md. Entwicklerdoku gehoert
    aber nicht auf die Seite der Teilnehmenden. Der Schutz ist die
    Unterstrich-Regel: Quarto ignoriert alles, was mit _ beginnt, Datei wie
    Verzeichnis.
    """
    fehler = []
    for p in sorted(WURZEL.rglob("*.md")):
        teile = p.relative_to(WURZEL).parts
        if any(t in AUSGENOMMEN for t in teile):
            continue
        if any(t.startswith("_") for t in teile):
            continue
        fehler.append(
            f"{p.relative_to(WURZEL).as_posix()}  wuerde als Website-Seite "
            f"gerendert, Unterstrich voranstellen"
        )
    return fehler


def pruefe_site() -> list[str]:
    site = WURZEL / "_site"
    if not site.is_dir():
        return []
    muster = re.compile(r'(?:src|href)="/(?!/)')
    fehler = []
    for p in site.rglob("*.html"):
        for i, z in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            if muster.search(z):
                fehler.append(
                    f"{p.relative_to(WURZEL).as_posix()}:{i}  "
                    f"wurzelabsoluter Pfad, bricht unter /REPO/"
                )
                break
    return fehler


def main() -> int:
    fehler = pruefe_text() + pruefe_markdown() + pruefe_site()
    anzahl = sum(1 for _ in quelldateien())
    print(f"{anzahl} Quelldateien geprueft.")
    if fehler:
        print(f"\n{len(fehler)} Problem(e):\n")
        for e in fehler:
            print("  " + e)
        return 1
    print("Alle Konventionen eingehalten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
