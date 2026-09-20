#!/usr/bin/env python3
"""Prueft jeden Shinylive-Block auf Syntax und Grundstruktur.

Hintergrund: ein Python-Fehler in einem Shinylive-Block faellt beim Rendern
NICHT auf. Quarto reicht den Code unveraendert an den Browser weiter, und erst
dort scheitert er, sichtbar nur fuer die Teilnehmenden. Ohne Browser-Test ist
das die groesste ungesicherte Fehlerquelle des Projekts.

Dieses Skript parst jeden Block mit ast.parse und prueft zusaetzlich die
Konventionen, die sich sonst still verletzen lassen.

Aufruf:  python tools/check-apps.py
Rueckgabe: 0 wenn alles sauber, 1 sonst.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
APP_ORDNER = WURZEL / "apps"

BLOCK = re.compile(
    r"^```\{shinylive-python\}\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)

# Zeilen, die mit #| beginnen, sind Quarto-Zellenoptionen und kein Python.
OPTION = re.compile(r"^#\|")


def bloecke(text: str):
    for treffer in BLOCK.finditer(text):
        roh = treffer.group(1)
        zeilen = roh.split("\n")
        optionen = [z for z in zeilen if OPTION.match(z)]
        code = "\n".join(z for z in zeilen if not OPTION.match(z))
        start = text[: treffer.start()].count("\n") + 1
        yield start, optionen, code


def pruefe_datei(pfad: pathlib.Path) -> list[str]:
    text = pfad.read_text(encoding="utf-8")
    name = pfad.relative_to(WURZEL).as_posix()
    fehler: list[str] = []
    gefunden = 0

    for start, optionen, code in bloecke(text):
        gefunden += 1
        ort = f"{name}:{start}"

        try:
            baum = ast.parse(code)
        except SyntaxError as exc:
            fehler.append(f"{ort}  Syntaxfehler Zeile {exc.lineno}: {exc.msg}")
            continue

        optionstext = "\n".join(optionen)
        if "standalone: true" not in optionstext:
            fehler.append(f"{ort}  '#| standalone: true' fehlt")
        if "viewerHeight" not in optionstext:
            fehler.append(f"{ort}  '#| viewerHeight' fehlt")

        namen = {
            ziel.id
            for knoten in ast.walk(baum)
            if isinstance(knoten, ast.Assign)
            for ziel in knoten.targets
            if isinstance(ziel, ast.Name)
        }
        if "app" not in namen:
            fehler.append(f"{ort}  keine Zuweisung an 'app' gefunden")

        funktionen = {
            k.name for k in ast.walk(baum) if isinstance(k, ast.FunctionDef)
        }
        if "server" not in funktionen:
            fehler.append(f"{ort}  keine Funktion 'server' gefunden")

        # Plot-Konvention: nie tight_layout, immer layout="constrained".
        if "tight_layout" in code:
            fehler.append(f"{ort}  tight_layout verwendet, layout='constrained' nutzen")
        if "plt.subplots(" in code and 'layout="constrained"' not in code:
            fehler.append(f"{ort}  plt.subplots ohne layout='constrained'")

    if gefunden == 0:
        fehler.append(f"{name}  kein Shinylive-Block gefunden")

    return fehler


def main() -> int:
    if not APP_ORDNER.is_dir():
        print(f"Ordner fehlt: {APP_ORDNER}")
        return 1

    dateien = sorted(APP_ORDNER.glob("a*.qmd"))
    if not dateien:
        print("Keine Anwendungen gefunden.")
        return 1

    alle: list[str] = []
    for pfad in dateien:
        alle.extend(pruefe_datei(pfad))

    print(f"{len(dateien)} Anwendungen geprueft.")
    if alle:
        print(f"\n{len(alle)} Problem(e):\n")
        for eintrag in alle:
            print("  " + eintrag)
        return 1

    print("Alle Bloecke sind syntaktisch gueltig und folgen den Konventionen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
