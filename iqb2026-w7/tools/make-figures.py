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
from scipy.stats import norm, t as t_dist, ttest_ind

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


def main() -> int:
    print("Abbildungen erzeugen:")
    for f in (e1_zwei_standorte, e1_p_gegen_n, e2_garten, e2_publikationsbias,
              e3_minderung, e3_benchmarks, e4_basisrate, e5_drei_kurven,
              e6_hdi_rope):
        f()
    print("Fertig.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
