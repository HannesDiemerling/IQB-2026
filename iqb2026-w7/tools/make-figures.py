#!/usr/bin/env python3
"""Erzeugt die statischen Abbildungen fuer die Foliendecks.

Ausgabe: folien/assets/*.png

Warum statisch und nicht interaktiv: die Folien sollen Text ersetzen, nicht
eine zweite Anwendung sein. Die interaktiven Fassungen stehen in apps/, die
Gruppen arbeiten dort. Auf der Folie zaehlt das eine Bild.

Alle Zahlen sind identisch zu den zugehoerigen Anwendungen, damit Folie und
Anwendung dieselbe Geschichte erzaehlen.

Aufruf:  python tools/make-figures.py
"""

from __future__ import annotations

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.stats import nct, norm, t as t_dist, ttest_ind

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "folien" / "assets"
ZIEL.mkdir(parents=True, exist_ok=True)

# Markenfarben, identisch zu theme/iqb-slides.scss
NAVY, TEAL, CORAL = "#2A3F66", "#4FA8A0", "#E27C5C"
SAND, CREAM, INK = "#E8C9A4", "#F7F2EA", "#1B2436"
GRAU, HELLGRAU = "#7f8c8d", "#bdc3c7"

plt.rcParams.update({
    "font.size": 15,
    "figure.facecolor": CREAM,
    "axes.facecolor": CREAM,
    "savefig.facecolor": CREAM,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.titlecolor": INK,
})


def sichern(fig, name: str) -> None:
    pfad = ZIEL / f"{name}.png"
    fig.savefig(pfad, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {pfad.relative_to(WURZEL).as_posix()}")


def blank(ax, spines=("top", "right")):
    for s in spines:
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- Einheit 1

def e1_zwei_standorte():
    """Gleicher Zuwachs, verschiedene Streuung, verschiedene Urteile."""
    N, M_OHNE, M_MIT = 45, 10.4, 12.5

    def gruppen(seed, sd):
        rng = np.random.RandomState(seed)
        zo, zm = rng.standard_normal(N), rng.standard_normal(N)
        for z in (zo, zm):
            z -= z.mean()
            z /= z.std(ddof=1)
        return M_OHNE + sd * zo, M_MIT + sd * zm

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), layout="constrained")
    for ax, (name, seed, sd) in zip(axes, [("Standort Nord", 7, 4.96),
                                           ("Standort Süd", 21, 5.10)]):
        ohne, mit = gruppen(seed, sd)
        _, p = ttest_ind(ohne, mit)
        rng = np.random.RandomState(99)
        ax.scatter(1 + rng.uniform(-.09, .09, N), ohne, color=HELLGRAU,
                   s=55, alpha=.75, edgecolor="none")
        ax.scatter(2 + rng.uniform(-.09, .09, N), mit, color=TEAL,
                   s=55, alpha=.75, edgecolor="none")
        ax.plot([1, 2], [ohne.mean(), mit.mean()], color=NAVY, lw=2.5, ls="--")
        ax.scatter([1, 2], [ohne.mean(), mit.mean()], color=NAVY, s=130, zorder=6)

        sig = p < .05
        ax.set_title(f"{name}\np = {p:.3f}   ·   "
                     f"{'signifikant' if sig else 'nicht signifikant'}",
                     color=TEAL if sig else CORAL, fontweight="bold", fontsize=15)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["ohne", "LeseStark"])
        ax.set_xlim(.5, 2.5)
        ax.set_ylim(0, 26)
        ax.set_ylabel("Testleistung in Punkten")
        blank(ax)
        tf = ax.get_xaxis_transform()
        ax.text(1.5, .04, f"Zuwachs {mit.mean() - ohne.mean():.1f} Punkte",
                transform=tf, ha="center", fontsize=14, fontweight="bold",
                color=NAVY)
    sichern(fig, "e1-zwei-standorte")


def e1_p_gegen_n():
    """Ein belangloser Zuwachs wird durch Datenmasse signifikant."""
    DIFF, SD = 0.2, 3.0
    n = np.linspace(10, 5000, 600)
    p = t_dist.sf(np.abs(DIFF / (SD * np.sqrt(2 / n))), 2 * n - 2) * 2

    fig, ax = plt.subplots(figsize=(11, 5.2), layout="constrained")
    ax.plot(n, p, color=NAVY, lw=3)
    ax.axhline(.05, color=CORAL, ls="dotted", lw=2.5)

    for nn, txt in [(50, "n = 50\nnichts gefunden"),
                    (1800, "n = 1800\nhochsignifikant")]:
        pp = float(t_dist.sf(abs(DIFF / (SD * np.sqrt(2 / nn))), 2 * nn - 2) * 2)
        ax.scatter([nn], [pp], color=CORAL, s=170, zorder=5)
        ax.annotate(txt, xy=(nn, pp), xytext=(nn + 420, pp + .18),
                    fontsize=13, color=NAVY,
                    arrowprops=dict(arrowstyle="-", color=GRAU, lw=1.2))

    ax.text(4900, .075, "Signifikanzschwelle .05", ha="right", fontsize=13,
            color=CORAL)
    ax.set_xlim(0, 5000)
    ax.set_ylim(-.02, 1)
    ax.set_xlabel("Getestete Lernende pro Gruppe")
    ax.set_ylabel("p-Wert")
    ax.set_title("Der Zuwachs bleibt konstant bei 0,2 Punkten",
                 fontweight="bold", fontsize=16)
    blank(ax)
    sichern(fig, "e1-p-gegen-n")


def e1_teststaerke():
    """Wie oft findet die Studie ihren eigenen Effekt ueberhaupt?

    Rechnet mit den Szenariozahlen: d = 0.42, je 45 Lernende, alpha .05
    zweiseitig. Die Pointe steht nicht auf der Folie, sondern faellt aus der
    Rechnung: die Teststaerke liegt bei rund 50 Prozent.
    """
    D, N_STUDIE, ZIEL = 0.42, 45, 0.80

    def power(n):
        df = 2 * n - 2
        ncp = D * np.sqrt(n / 2.0)
        krit = t_dist.ppf(1 - .05 / 2, df)
        return nct.sf(krit, df, ncp) + nct.cdf(-krit, df, ncp)

    n_noetig = 2
    while power(n_noetig) < ZIEL:
        n_noetig += 1

    n = np.arange(5, 251)
    p = np.array([power(k) for k in n])
    p_studie = power(N_STUDIE)

    fig, ax = plt.subplots(figsize=(11.5, 5.0), layout="constrained")
    ax.plot(n, p * 100, color=NAVY, lw=3.5, zorder=4)
    ax.axhline(ZIEL * 100, color=TEAL, ls="dotted", lw=2.5, zorder=3)
    ax.text(248, ZIEL * 100 + 2.5, "üblicher Anspruch: 80 %", ha="right",
            fontsize=13, color=TEAL)

    ax.fill_between(n, 0, p * 100, where=(n <= N_STUDIE), color=CORAL,
                    alpha=.13, zorder=1)
    ax.scatter([N_STUDIE], [p_studie * 100], s=260, color=CORAL, zorder=6,
               edgecolor=CREAM, lw=2.5)
    ax.annotate(f"die LeseStark-Studie\nje {N_STUDIE} Lernende: "
                f"{p_studie * 100:.0f} %",
                xy=(N_STUDIE, p_studie * 100), xytext=(N_STUDIE + 26, 27),
                fontsize=13.5, color=CORAL, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=GRAU, lw=1.3))

    ax.scatter([n_noetig], [power(n_noetig) * 100], s=200, color=TEAL,
               zorder=6, edgecolor=CREAM, lw=2)
    ax.annotate(f"für 80 % bräuchte sie\nje {n_noetig} Lernende",
                xy=(n_noetig, power(n_noetig) * 100),
                xytext=(n_noetig + 30, 62), fontsize=13.5, color=TEAL,
                fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=GRAU, lw=1.3))

    ax.set_xlim(0, 250)
    ax.set_ylim(0, 103)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(["0 %", "20 %", "40 %", "60 %", "80 %", "100 %"])
    ax.set_xlabel("Getestete Lernende pro Gruppe")
    ax.set_ylabel("Teststärke")
    ax.set_title("Wie oft findet die Studie ihren eigenen Effekt?\n"
                 "Teststärke bei d = 0.42", fontweight="bold", fontsize=16)
    blank(ax)
    sichern(fig, "e1-teststaerke")


def e1_lortie_forgues():
    """141 Wirksamkeitsstudien: der Effekt verschwindet in seinem Intervall.

    Ersetzt eine Belegliste in Kleinschrift. Die Pointe ist ein
    Groessenverhaeltnis, und Groessenverhaeltnisse gehoeren ins Bild.
    """
    EFFEKT, BREITE = 0.06, 0.30
    lo, hi = EFFEKT - BREITE / 2, EFFEKT + BREITE / 2

    fig, ax = plt.subplots(figsize=(11.5, 4.3), layout="constrained")
    ax.axvspan(-0.16, 0, color=CORAL, alpha=.13, zorder=0)
    ax.axvspan(0.20, 0.32, color=TEAL, alpha=.20, zorder=0)

    ax.plot([lo, hi], [0, 0], color=NAVY, lw=11, solid_capstyle="butt", zorder=3)
    ax.scatter([EFFEKT], [0], s=300, color=CORAL, zorder=5,
               edgecolor=CREAM, lw=2.5)
    ax.axvline(0, color=INK, ls="dotted", lw=2)

    ax.text(EFFEKT, .30, "Durchschnitt\n0,06 SD", ha="center", fontsize=14,
            fontweight="bold", color=CORAL)
    ax.text(lo, -.30, f"{lo:.2f}".replace(".", ","), ha="center", fontsize=12,
            color=GRAU)
    ax.text(hi, -.30, f"{hi:.2f}".replace(".", ","), ha="center", fontsize=12,
            color=GRAU)
    ax.text(-.08, .78, "Schaden\nmöglich", ha="center", fontsize=12.5,
            color=CORAL, style="italic")
    ax.text(.26, .78, "großer Effekt\nnach Kraft", ha="center", fontsize=12.5,
            color=TEAL, style="italic")

    ax.text(.5, -.42, "Das Intervall ist fünfmal so breit wie der Effekt, den "
                      "es einschließen soll.\nMittlerer Bayes-Faktor 0,56: die "
                      "Daten unterscheiden nicht zwischen Wirkung und keiner "
                      "Wirkung.",
            transform=ax.transAxes, ha="center", fontsize=13, color=NAVY,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                      edgecolor=HELLGRAU, lw=1.2))

    ax.set_xlim(-.16, .32)
    ax.set_ylim(-1.15, 1.15)
    ax.set_yticks([])
    ax.set_xticks([-.1, 0, .1, .2, .3])
    ax.set_xticklabels(["-0,10", "0", "0,10", "0,20", "0,30"])
    ax.set_xlabel("Effektstärke in Standardabweichungen")
    ax.set_title("141 große Wirksamkeitsstudien, zusammen über 1,2 Millionen "
                 "Lernende", fontweight="bold", fontsize=16, pad=12)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e1-lortie-forgues")


# ---------------------------------------------------------------- Einheit 2

def e2_garten():
    """Alle 24 Analysepfade auf einen Blick, wahrer Effekt null."""
    from itertools import product
    rng = np.random.default_rng(42)
    n = 60
    d = dict(ohne=rng.normal(12, 3.0, n), mit=rng.normal(12, 3.0, n))
    for k in ("voll", "regel", "jg", "gt"):
        d[k + "_o"] = rng.random(n) > (.4 if k == "voll" else .3 if k == "regel" else .5)
        d[k + "_m"] = rng.random(n) > (.4 if k == "voll" else .3 if k == "regel" else .5)

    ps = []
    for do, cw, wo, sg in product([False, True], [False, True], [False, True],
                                  ["all", "jg", "gt"]):
        mo = np.ones(n, bool); mm = np.ones(n, bool)
        if cw: mo &= d["voll_o"]; mm &= d["voll_m"]
        if wo: mo &= d["regel_o"]; mm &= d["regel_m"]
        if sg == "jg": mo &= d["jg_o"]; mm &= d["jg_m"]
        elif sg == "gt": mo &= d["gt_o"]; mm &= d["gt_m"]
        a, b = d["ohne"][mo], d["mit"][mm]
        if do:
            if len(a) > 2: a = np.sort(a)[:-1]
            if len(b) > 2: b = np.sort(b)[:-1]
        if len(a) >= 3 and len(b) >= 3:
            ps.append(ttest_ind(a, b)[1])
    ps = np.sort(np.array(ps))

    fig, ax = plt.subplots(figsize=(11, 5.4), layout="constrained")
    farben = [CORAL if v < .05 else HELLGRAU for v in ps]
    ax.barh(np.arange(len(ps)), ps, color=farben, height=.72)
    ax.axvline(.05, color=CORAL, ls="dotted", lw=2.5)
    ax.text(.058, len(ps) - 1.5, "Schwelle .05", color=CORAL, fontsize=13)

    ax.set_yticks([])
    ax.set_xlim(0, 1)
    ax.set_ylim(-1, len(ps))
    ax.set_xlabel("p-Wert des jeweiligen Analysepfads")
    ax.set_ylabel(f"{len(ps)} Pfade")
    n_sig = int((ps < .05).sum())
    ax.set_title(f"{len(ps)} plausible Analysepfade, {n_sig} davon signifikant"
                 f"\nDer wahre Effekt ist null",
                 fontweight="bold", fontsize=16, color=NAVY)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e2-garten")


def e2_publikationsbias():
    """Was von 40 Studien in der Literatur ankommt."""
    np.random.seed(42)
    N, TRUE = 40, 2.0
    se = np.random.uniform(.4, 2.0, N)
    eff = np.random.normal(TRUE, se, N)
    sig = (eff / se) > 1.96
    order = np.argsort(eff)

    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    for rang, i in enumerate(order):
        if sig[i]:
            ax.barh(rang, eff[i], color=TEAL, alpha=.9, height=.74)
        else:
            ax.barh(rang, eff[i], color=CREAM, height=.74,
                    edgecolor=HELLGRAU, lw=1.1, hatch="///")

    ax.axvline(TRUE, color=NAVY, ls="dotted", lw=2.5)
    sichtbar = float(eff[sig].mean())
    ax.axvline(sichtbar, color=CORAL, lw=3.5)

    ax.set_yticks([])
    ax.set_xlim(-3, 9)
    ax.set_ylim(-1, N)
    ax.set_xlabel("Gemessener Zuwachs in Punkten")
    ax.set_ylabel("40 Studien")
    ax.set_title(f"Wahrer Zuwachs {TRUE:.0f} Punkte, in der Literatur "
                 f"{sichtbar:.1f} Punkte", fontweight="bold", fontsize=16)
    ax.legend(handles=[
        Line2D([0], [0], color=TEAL, lw=9, label="publiziert"),
        Line2D([0], [0], color=HELLGRAU, lw=9, label="in der Schublade"),
        Line2D([0], [0], color=NAVY, lw=2.5, ls="dotted", label="wahrer Zuwachs"),
        Line2D([0], [0], color=CORAL, lw=3.5, label="Durchschnitt der Literatur"),
    ], loc="lower right", fontsize=12, framealpha=.95)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e2-publikationsbias")


def e2_replikation():
    """Drei Befunde zur Replizierbarkeit, je ein Panel.

    Die drei Arbeiten messen Verschiedenes und bekommen deshalb verschiedene
    Darstellungen. Gemeinsam ist nur die Richtung.
    """
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), layout="constrained",
                             gridspec_kw=dict(width_ratios=[1, 1, 1.3]))

    # Panel 1: Original gegen Replikation
    ax = axes[0]
    ax.bar([0, 1], [97, 36], color=[NAVY, CORAL], width=.62)
    for x, v in [(0, 97), (1, 36)]:
        ax.text(x, v + 3, f"{v} %", ha="center", fontsize=15,
                fontweight="bold", color=NAVY if x == 0 else CORAL)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Original", "Replikation"])
    ax.set_ylim(0, 118)
    ax.set_yticks([])
    ax.set_title("Anteil signifikanter Befunde\nOpen Science Collaboration 2015",
                 fontsize=13.5, fontweight="bold", color=NAVY)
    blank(ax, ("top", "right", "left"))

    # Panel 2: ohne gegen mit Praeregistrierung
    ax = axes[1]
    ax.bar([0, 1], [.36, .16], color=[NAVY, CORAL], width=.62)
    for x, v in [(0, .36), (1, .16)]:
        ax.text(x, v + .012, f"{v:.2f}".replace(".", ","), ha="center",
                fontsize=15, fontweight="bold", color=NAVY if x == 0 else CORAL)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["ohne\nPräregistrierung", "präregistriert"])
    ax.set_ylim(0, .44)
    ax.set_yticks([])
    ax.set_title("Median der Effekte, r\nSchäfer & Schwarz 2019",
                 fontsize=13.5, fontweight="bold", color=NAVY)
    blank(ax, ("top", "right", "left"))

    # Panel 3: wie selten Replikationen ueberhaupt sind
    ax = axes[2]
    SP, ZE = 40, 25
    TREFFER = (SP * ZE) // 2      # genau ein Punkt, mittig, damit er auffaellt
    for i in range(SP * ZE):
        if i == TREFFER:
            continue
        ax.scatter(i % SP, -(i // SP), s=11, color="#d8dde3",
                   edgecolor="none", zorder=1)
    tx, ty = TREFFER % SP, -(TREFFER // SP)
    ax.scatter([tx], [ty], s=150, color=CORAL, edgecolor="none", zorder=4)
    ax.scatter([tx], [ty], s=620, facecolors="none", edgecolor=CORAL, lw=2,
               zorder=4)
    ax.set_xlim(-1.5, SP + .5)
    ax.set_ylim(-ZE - 1.5, 1.5)
    ax.axis("off")
    ax.set_title("Von 1000 Artikeln ist einer eine Replikation\n"
                 "Makel & Plucker 2014", fontsize=13.5, fontweight="bold",
                 color=NAVY)
    ax.text(SP / 2, -ZE - .6, "0,13 %", ha="center", fontsize=15,
            fontweight="bold", color=CORAL)

    sichern(fig, "e2-replikation")


# ---------------------------------------------------------------- Einheit 3

def e3_minderung():
    """Die Minderungskurve, mit den fuenf Gruppenwerten."""
    D_WAHR = 0.50
    rel = np.linspace(.5, 1.0, 200)

    fig, ax = plt.subplots(figsize=(11, 5.4), layout="constrained")
    ax.plot(rel, D_WAHR * np.sqrt(rel), color=NAVY, lw=3.5,
            label="beobachtbares d")
    ax.axhline(D_WAHR, color=TEAL, ls="dotted", lw=2.5,
               label=f"wahres d = {D_WAHR:.2f}")
    ax.fill_between(rel, D_WAHR * np.sqrt(rel), D_WAHR, color=CORAL, alpha=.15)

    for r in [.95, .85, .75, .65, .55]:
        ax.scatter([r], [D_WAHR * np.sqrt(r)], color=CORAL, s=140, zorder=5)
    ax.annotate("verlorener Anteil", xy=(.72, .455), xytext=(.72, .53),
                ha="center", fontsize=14, color=CORAL, style="italic",
                arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.4))

    ax.set_xlim(.5, 1.0)
    ax.set_ylim(.3, .58)
    ax.set_xlabel("Reliabilität des Messinstruments")
    ax.set_ylabel("Effektstärke d")
    ax.set_title("Bei Reliabilität .70 bleibt von d = 0.50 nur d = 0.42",
                 fontweight="bold", fontsize=16)
    ax.legend(loc="lower right", fontsize=13)
    blank(ax)
    sichern(fig, "e3-minderung")


def e3_benchmarks():
    """Cohens Faustregeln gegen bildungsspezifische Groessenordnungen.

    Cohen nennt Punktkonventionen (0.2 / 0.5 / 0.8). Kraft schlaegt fuer
    Bildungsinterventionen Baender vor. Die beiden Schemata sind also
    verschieden gebaut und werden deshalb auch verschieden gezeichnet.
    """
    fig, ax = plt.subplots(figsize=(11.5, 4.6), layout="constrained")

    # Oben: Kraft, als Baender
    baender = [(0.0, 0.05, "klein", "#cfe3e1"),
               (0.05, 0.20, "mittel", TEAL),
               (0.20, 1.0, "groß", NAVY)]
    for lo, hi, name, farbe in baender:
        ax.barh(1, hi - lo, left=lo, height=.30, color=farbe, zorder=3)
        ax.text((lo + hi) / 2, 1.28, name, ha="center", fontsize=13,
                color=NAVY, fontweight="bold")
    ax.text(0.025, 0.72, "< .05", ha="center", fontsize=11, color=GRAU)
    ax.text(0.125, 0.72, ".05 bis .20", ha="center", fontsize=11, color=GRAU)
    ax.text(0.60, 0.72, "ab .20", ha="center", fontsize=11, color=GRAU)

    # Unten: Cohen, als Punktkonventionen
    ax.plot([0, 1.0], [0, 0], color=HELLGRAU, lw=1.4, zorder=1)
    for wert, name in [(0.2, "klein"), (0.5, "mittel"), (0.8, "groß")]:
        ax.scatter([wert], [0], s=260, color=SAND, zorder=3,
                   edgecolor=NAVY, lw=1.2)
        ax.text(wert, 0.20, f"{name}\n{wert:.1f}", ha="center", fontsize=12,
                color=NAVY)

    # Der Befund aus dem Workshop
    ax.axvline(0.42, color=CORAL, ls="dashed", lw=2, zorder=2)
    ax.text(0.42, -0.62, "LeseStark\nd = 0.42", ha="center", fontsize=12.5,
            color=CORAL, fontweight="bold")

    ax.text(-0.015, 1, "Bildungsforschung\nKraft 2020", ha="right",
            va="center", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(-0.015, 0, "Cohen 1988\nallgemein", ha="right", va="center",
            fontsize=13, fontweight="bold", color=NAVY)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.85, 1.6)
    ax.set_yticks([])
    ax.set_xticks([0, .2, .4, .6, .8, 1.0])
    ax.set_xlabel("Cohens d")
    ax.set_title("Dieselbe Zahl, zwei völlig verschiedene Einordnungen",
                 fontweight="bold", fontsize=16, pad=14)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e3-benchmarks")


def e3_design_effekte():
    """Cheung und Slavin: dasselbe Programm, doppelte Effektstaerke.

    Bewusst relativ skaliert. Die Quelle traegt die Aussage "rund doppelt so
    gross", nicht ein Paar absoluter Werte je Merkmal. Wer hier absolute
    Zahlen hinschreibt, erfindet sie.
    """
    paare = [
        ("kleine Stichprobe", "große Stichprobe"),
        ("selbst entwickelter Test", "normiertes Instrument"),
        ("publiziert", "unpubliziert"),
    ]

    fig, ax = plt.subplots(figsize=(11.5, 4.8), layout="constrained")
    for i, (hoch, referenz) in enumerate(paare):
        y = len(paare) - 1 - i
        ax.barh(y + .19, 2.0, height=.34, color=CORAL, zorder=3)
        ax.barh(y - .19, 1.0, height=.34, color=HELLGRAU, zorder=3)
        ax.text(2.06, y + .19, hoch, va="center", fontsize=13.5,
                fontweight="bold", color=CORAL)
        ax.text(1.06, y - .19, referenz, va="center", fontsize=13.5,
                color=GRAU)
        ax.text(1.94, y + .19, "doppelt", va="center", ha="right",
                fontsize=12.5, color="white", fontweight="bold")

    ax.set_xlim(0, 3.7)
    ax.set_ylim(-.7, len(paare) - .2)
    ax.set_yticks([])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["0", "Referenz"])
    ax.set_xlabel("Effektstärke relativ zur jeweiligen Vergleichsgruppe")
    ax.set_title("Dasselbe Programm, doppelte Effektstärke.\n"
                 "Cheung & Slavin 2016, 645 Studien aus 12 Übersichtsarbeiten",
                 fontweight="bold", fontsize=15.5, pad=12)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e3-design-effekte")


# ---------------------------------------------------------------- Einheit 4

def e4_basisrate():
    """Faktenbox: 1000 Lernende, wer wird richtig und wer falsch erkannt."""
    SPALTEN, ZEILEN = 50, 20
    gesamt = SPALTEN * ZEILEN
    echt_erkannt, fehlalarm = 28, 78

    kat = np.zeros(gesamt, dtype=int)
    kat[:echt_erkannt] = 1
    kat[echt_erkannt:echt_erkannt + 2] = 2
    kat[echt_erkannt + 2:echt_erkannt + 2 + fehlalarm] = 3

    farbe = {0: "#dfe3e8", 1: TEAL, 2: NAVY, 3: CORAL}
    fig, ax = plt.subplots(figsize=(12, 5.6), layout="constrained")
    for i, k in enumerate(kat):
        ax.scatter(i % SPALTEN, -(i // SPALTEN), s=42, color=farbe[k],
                   edgecolor="none")

    ax.set_xlim(-1, SPALTEN)
    ax.set_ylim(-ZEILEN, 1.2)
    ax.axis("off")
    ax.set_title("1000 gescreente Lernende", fontweight="bold", fontsize=17,
                 color=NAVY, pad=12)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", lw=0, markersize=11, color=TEAL,
               label=f"{echt_erkannt} echter Bedarf, erkannt"),
        Line2D([0], [0], marker="o", lw=0, markersize=11, color=NAVY,
               label="2 echter Bedarf, übersehen"),
        Line2D([0], [0], marker="o", lw=0, markersize=11, color=CORAL,
               label=f"{fehlalarm} Fehlalarme"),
        Line2D([0], [0], marker="o", lw=0, markersize=11, color="#dfe3e8",
               label="kein Bedarf, kein Alarm"),
    ], loc="lower center", ncol=2, fontsize=13, framealpha=.95,
        bbox_to_anchor=(.5, -.22))
    fig.text(.5, .5, f"Von {echt_erkannt + fehlalarm} Alarmen sind "
                     f"{echt_erkannt} berechtigt: 27 %",
             ha="center", fontsize=16, fontweight="bold", color=CORAL,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                       edgecolor=CORAL, lw=1.5))
    sichern(fig, "e4-basisrate")


# ---------------------------------------------------------------- Einheit 5

def e5_likelihood():
    """Die Likelihood ueber den fuenf festen Pilotklassen.

    Ersetzt eine Tabelle aus Hypothese und Bewertung. Die Tabelle konnte nicht
    zeigen, was den Begriff schwer macht: die Daten stehen still, die
    Hypothese wandert.
    """
    DATEN = np.array([3, 7, 5, 9, 6])
    m = DATEN.mean()
    se = DATEN.std(ddof=1) / np.sqrt(len(DATEN))

    theta = np.linspace(0, 12, 500)
    like = norm.pdf(theta, m, se)
    like /= like.max()

    fig, ax = plt.subplots(figsize=(11.5, 4.8), layout="constrained")
    ax.plot(theta, like, color=CORAL, lw=3.5, zorder=4)
    ax.fill_between(theta, 0, like, color=CORAL, alpha=.15, zorder=2)

    # Die fuenf Messwerte als Teppich, innerhalb der Achsen, damit sie nicht
    # in die Tick-Beschriftung laufen.
    ax.scatter(DATEN, np.full(len(DATEN), .05), s=320, color=NAVY,
               marker="|", linewidths=3, zorder=6)
    ax.text(.02, .88, "Die fünf Pilotklassen stehen fest:  3 · 7 · 5 · 9 · 6",
            transform=ax.transAxes, ha="left", fontsize=13, color=NAVY,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=HELLGRAU, lw=1.1))

    for t, label, ha in [(m, "Maximum", "center"), (3.0, "gering", "center"),
                         (9.0, "gering", "center"),
                         (0.0, "praktisch null", "left"),
                         (12.0, "praktisch null", "right")]:
        y = float(norm.pdf(t, m, se) / norm.pdf(m, m, se))
        ax.scatter([t], [y], s=120, color=NAVY, zorder=7)
        ax.text(t, y + .11, label, ha=ha, fontsize=12.5, color=NAVY,
                fontweight="bold")

    ax.set_xlim(-.5, 12.5)
    ax.set_ylim(0, 1.3)
    ax.set_yticks([])
    ax.set_xticks([0, 3, 6, 9, 12])
    ax.set_xlabel("Hypothese θ: wahrer Zuwachs in Punkten")
    ax.set_ylabel("Likelihood")
    ax.set_title("Die Daten stehen fest. Die Hypothese wandert.",
                 fontweight="bold", fontsize=16, pad=10)
    blank(ax)
    sichern(fig, "e5-likelihood")


def e5_drei_kurven():
    """Prior, Likelihood, Posterior in einem Bild."""
    p_mean, p_sd = 8.0, 5.0
    d_mean, d_se = 6.0, 2.5 / np.sqrt(5)
    pv, dv = p_sd**2, d_se**2
    post_var = 1 / (1 / pv + 1 / dv)
    post_mean = post_var * (p_mean / pv + d_mean / dv)
    post_sd = np.sqrt(post_var)

    x = np.linspace(-5, 25, 500)
    fig, ax = plt.subplots(figsize=(11, 5.2), layout="constrained")
    ax.plot(x, norm.pdf(x, p_mean, p_sd), color=GRAU, lw=2.5, ls="dotted",
            label=f"Prior: {p_mean:.0f} Punkte")
    ax.plot(x, norm.pdf(x, d_mean, d_se), color=CORAL, lw=2.5, ls="dashed",
            label=f"Daten: {d_mean:.0f} Punkte")
    ax.plot(x, norm.pdf(x, post_mean, post_sd), color="#8e44ad", lw=4,
            label=f"Posterior: {post_mean:.1f} Punkte")

    lo, hi = norm.interval(.95, loc=post_mean, scale=post_sd)
    xf = np.linspace(lo, hi, 200)
    ax.fill_between(xf, 0, norm.pdf(xf, post_mean, post_sd), color="#8e44ad",
                    alpha=.22)

    ax.set_xlim(-5, 25)
    ax.set_ylim(0, None)
    ax.set_yticks([])
    ax.set_xlabel("Kompetenzzuwachs in Punkten")
    ax.set_ylabel("Dichte")
    ax.set_title(f"Der Posterior landet dazwischen, "
                 f"95 % HDI [{lo:.1f}; {hi:.1f}]",
                 fontweight="bold", fontsize=16)
    ax.legend(loc="upper right", fontsize=13)
    blank(ax)
    sichern(fig, "e5-drei-kurven")


# ---------------------------------------------------------------- Einheit 6

def e6_hdi_rope():
    """Die drei moeglichen Ausgaenge einer ROPE-Entscheidung."""
    ROPE = 3.0
    faelle = [
        (2.1, 1.05, "Noch nicht entschieden", CORAL),
        (0.0, 0.50, "Praktisch äquivalent", NAVY),
        (4.0, 0.50, "Relevanter Effekt", TEAL),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), layout="constrained")
    x = np.linspace(-7, 11, 500)
    for ax, (mu, sd, titel, farbe) in zip(axes, faelle):
        lo, hi = mu - 1.96 * sd, mu + 1.96 * sd
        ax.axvspan(-ROPE, ROPE, color=HELLGRAU, alpha=.35)
        y = norm.pdf(x, mu, sd)
        ax.plot(x, y, color="#8e44ad", lw=2.5)
        m = (x >= lo) & (x <= hi)
        ax.fill_between(x[m], 0, y[m], color="#8e44ad", alpha=.25)
        ax.plot([lo, hi], [0, 0], color=farbe, lw=7, solid_capstyle="round")
        ax.axvline(0, color=NAVY, ls="dotted", lw=1.5)
        ax.set_xlim(-7, 11)
        ax.set_ylim(0, y.max() * 1.25)
        ax.set_yticks([])
        ax.set_title(titel, color=farbe, fontweight="bold", fontsize=14)
        ax.set_xlabel("Zuwachs in Punkten")
        blank(ax, ("top", "right", "left"))
        tf = ax.get_xaxis_transform()
        ax.text(0, .9, "ROPE", transform=tf, ha="center", fontsize=12,
                color="#5d6d7e", fontweight="bold")
    sichern(fig, "e6-hdi-rope")


def e6_bayesfaktor():
    """Die Evidenzleiter, symmetrisch in beide Richtungen.

    Ersetzt eine fuenfzeilige Tabelle, die nur die rechte Haelfte zeigte. Die
    Symmetrie ist der eigentliche Inhalt der Folie, und eine Tabelle kann sie
    nicht zeigen.
    """
    kanten = [0, np.log10(3), 1, np.log10(30), 2, 2.4]
    namen = ["anekdotisch", "moderat", "stark", "sehr stark", "extrem"]
    coral_t = ["#f7ded5", "#f1c3b0", "#eaa78b", "#e2845c", "#c65f34"]
    teal_t = ["#d8e9e7", "#b4d7d3", "#8fc5bf", "#69b1aa", "#3e8b84"]

    fig, ax = plt.subplots(figsize=(12.5, 4.5), layout="constrained")
    for i, name in enumerate(namen):
        lo, hi = kanten[i], kanten[i + 1]
        for vz, tabelle in ((1, coral_t), (-1, teal_t)):
            ax.barh(0, vz * (hi - lo), left=vz * lo, height=.9,
                    color=tabelle[i], zorder=3, align="center")
            ax.text(vz * (lo + hi) / 2, .62, name, ha="center", fontsize=11.5,
                    color=NAVY, rotation=0 if hi - lo > .45 else 90,
                    va="bottom")

    # Nur ueber die Leiter, nicht ueber die ganze Achse. Sonst schneidet die
    # Linie durch die Beschriftung darunter.
    ax.plot([0, 0], [-.45, .45], color=INK, lw=2.5, zorder=5)
    ax.text(0, -.95, "Die Daten entscheiden nicht", ha="center", fontsize=12,
            color=GRAU, style="italic")

    ax.text(-1.2, 1.28, "BF₀₁  ·  Evidenz für kein Effekt", ha="center",
            fontsize=14.5, fontweight="bold", color="#3e8b84")
    ax.text(1.2, 1.28, "BF₁₀  ·  Evidenz für einen Effekt", ha="center",
            fontsize=14.5, fontweight="bold", color=CORAL)

    ticks = [-2, -np.log10(30), -1, -np.log10(3), 0,
             np.log10(3), 1, np.log10(30), 2]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["100", "30", "10", "3", "1", "3", "10", "30", "100"])
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-1.35, 1.75)
    ax.set_yticks([])
    ax.set_xlabel("Bayes-Faktor")
    ax.set_title("Dieselben Stufen gelten in beide Richtungen.\n"
                 "Genau das kann ein Signifikanztest nicht.",
                 fontweight="bold", fontsize=15.5, pad=10)
    blank(ax, ("top", "right", "left"))
    sichern(fig, "e6-bayesfaktor")


def main() -> int:
    print("Abbildungen erzeugen:")
    for f in (e1_zwei_standorte, e1_p_gegen_n, e1_teststaerke,
              e1_lortie_forgues,
              e2_garten, e2_publikationsbias, e2_replikation,
              e3_minderung, e3_benchmarks, e3_design_effekte,
              e4_basisrate, e5_likelihood, e5_drei_kurven,
              e6_hdi_rope, e6_bayesfaktor):
        f()
    print("Fertig.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
