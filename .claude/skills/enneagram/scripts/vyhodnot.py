#!/usr/bin/env python3
"""Vyhodnocení orientačního enneagram dotazníku (assets/dotaznik.json).

Použití:
  python3 vyhodnot.py --sablona > odpovedi.json     # prázdná šablona odpovědí
  python3 vyhodnot.py odpovedi.json                 # vyhodnocení (text)
  python3 vyhodnot.py vyplneny_dotaznik.md          # lze i vyplněný dotaznik.md
  python3 vyhodnot.py odpovedi.json --format json   # strojový výstup

Formát odpovědí (JSON): {"R1": "A", "R2": "C", "B01": 4, ..., "B90": 2, "C01": 5, ..., "C18": 3}
Hodnoty B/C jsou 1–5, R1/R2 jsou A/B/C. Chybějící hodnoty (null) se vynechají.
"""
import argparse, json, re, statistics, sys
from pathlib import Path

DOTAZNIK = Path(__file__).resolve().parent.parent / "assets" / "dotaznik.json"

NAZVY = {1: "Reformátor", 2: "Pomocník", 3: "Úspěšný", 4: "Individualista", 5: "Pozorovatel",
         6: "Loajální", 7: "Nadšenec", 8: "Vyzyvatel", 9: "Mírotvůrce"}
STRES = {1: 4, 4: 2, 2: 8, 8: 5, 5: 7, 7: 1, 3: 9, 9: 6, 6: 3}
RUST = {v: k for k, v in STRES.items()}
CENTRA = {"tělo": [8, 9, 1], "srdce": [2, 3, 4], "hlava": [5, 6, 7]}
INST_NAZVY = {"sp": "sebezáchovný", "so": "sociální", "sx": "sexuální / one-to-one"}
MIN_ODPOVEDI = 0.8  # podíl vyplněných výroků na typ, pod kterým varujeme


def nacti_dotaznik():
    return json.loads(DOTAZNIK.read_text(encoding="utf-8"))


def sablona(d):
    s = {q["id"]: None for q in d["cast_a"]}
    s.update({p["id"]: None for p in d["cast_b"]})
    s.update({p["id"]: None for p in d["cast_c"]})
    return s


def nacti_odpovedi(cesta):
    text = Path(cesta).read_text(encoding="utf-8") if cesta != "-" else sys.stdin.read()
    if cesta.endswith(".md"):
        odp = {}
        for m in re.finditer(r"\|\s*([BC]\d{2})\s*\|.*\|\s*\[\s*([1-5])\s*\]\s*\|", text):
            odp[m.group(1)] = int(m.group(2))
        for m in re.finditer(r"\*\*(R\d)\..*?\[\s*([ABCabc])\s*\]", text):
            odp[m.group(1)] = m.group(2).upper()
        return odp
    return json.loads(text)


def wing(top, prumery):
    l, p = (top - 2) % 9 + 1, top % 9 + 1
    sl, sp = prumery.get(l), prumery.get(p)
    if sl is None or sp is None:
        return None, "nelze určit"
    if abs(sl - sp) < 0.2:
        return None, f"vyvážená ({top}w{l} ≈ {top}w{p})"
    w = l if sl > sp else p
    return w, f"{top}w{w}"


def vyhodnot(d, odp):
    var = []
    # část B
    hodnoty = {t: [] for t in NAZVY}
    for p in d["cast_b"]:
        v = odp.get(p["id"])
        if v is None:
            continue
        v = int(v)
        if not 1 <= v <= 5:
            raise SystemExit(f"Neplatná hodnota {p['id']}={v} (povoleno 1–5)")
        hodnoty[p["typ"]].append(v)
    pocet_na_typ = len(d["cast_b"]) // 9
    prumery = {}
    for t, h in hodnoty.items():
        if len(h) < MIN_ODPOVEDI * pocet_na_typ:
            var.append(f"Typ {t}: vyplněno jen {len(h)}/{pocet_na_typ} výroků – skóre je nespolehlivé.")
        if h:
            prumery[t] = statistics.mean(h)
    if len(prumery) < 9:
        raise SystemExit("Část B není dost vyplněná – chybí celé typy.")
    poradi = sorted(prumery, key=prumery.get, reverse=True)
    top, druhy = poradi[0], poradi[1]

    vse = [v for h in hodnoty.values() for v in h]
    rozptyl = statistics.pstdev(prumery.values())
    if prumery[top] - prumery[druhy] < 0.3:
        var.append(f"Typy {top} a {druhy} jsou téměř vyrovnané – rozhodne ověřovací rozhovor.")
    if rozptyl < 0.35:
        var.append("Plochý profil (typy se málo liší). Zkus vyplnit znovu: „jak se chovám většinu života, ne jak bych chtěl/a“.")
    if statistics.mean(vse) > 4.0:
        var.append("Velmi vysoký průměr odpovědí – možná tendence souhlasit se vším.")
    if statistics.mean(vse) < 2.0:
        var.append("Velmi nízký průměr odpovědí – možná tendence se v ničem nepoznávat.")
    if druhy == STRES[top]:
        var.append(f"Druhý typ {druhy} je stresový bod typu {top} – může jít o stresové chování, ne o hlavní typ.")
    if druhy == RUST[top]:
        var.append(f"Druhý typ {druhy} je růstový bod typu {top} – ověř, který z nich je jádro.")
    if 9 in poradi[:3] and rozptyl < 0.5:
        var.append("Vysoká 9 při málo odlišeném profilu – devítky se často poznávají ve všech typech; zvaž typ 9.")

    w, w_text = wing(top, prumery)
    centra = {c: statistics.mean(prumery[t] for t in ts) for c, ts in CENTRA.items()}
    tritype = sorted((max(ts, key=prumery.get) for ts in CENTRA.values()), key=prumery.get, reverse=True)

    # část C
    inst = {k: [] for k in INST_NAZVY}
    for p in d["cast_c"]:
        v = odp.get(p["id"])
        if v is not None:
            inst[p["instinkt"]].append(int(v))
    inst_pr = {k: statistics.mean(v) for k, v in inst.items() if v}
    stack = sorted(inst_pr, key=inst_pr.get, reverse=True) if len(inst_pr) == 3 else []
    if stack and inst_pr[stack[0]] - inst_pr[stack[1]] < 0.25:
        var.append(f"Instinkty {stack[0]} a {stack[1]} jsou vyrovnané – dominantní instinkt ověř rozhovorem.")
    if len(inst_pr) < 3:
        var.append("Část C (instinkty) není vyplněná – podtyp nelze odhadnout.")

    # část A
    rychly = None
    volby = {q["id"]: {m["kod"]: set(m["typy"]) for m in q["moznosti"]} for q in d["cast_a"]}
    r1, r2 = (str(odp.get("R1") or "").upper(), str(odp.get("R2") or "").upper())
    if r1 in volby["R1"] and r2 in volby["R2"]:
        prunik = volby["R1"][r1] & volby["R2"][r2]
        rychly = prunik.pop()
        misto = poradi.index(rychly) + 1
        if misto > 3:
            var.append(f"Rychlý test ukazuje typ {rychly}, dotazník ho řadí až na {misto}. místo – probrat v rozhovoru.")
    else:
        misto = None

    return {
        "prumery": {str(t): round(prumery[t], 2) for t in poradi},
        "procenta": {str(t): round((prumery[t] - 1) / 4 * 100) for t in poradi},
        "poradi": poradi,
        "nejpravdepodobnejsi": top,
        "kandidati": poradi[:3],
        "kridlo": w, "kridlo_text": w_text,
        "stres": STRES[top], "rust": RUST[top],
        "centra": {c: round(v, 2) for c, v in centra.items()},
        "tritype_orientacne": "".join(map(str, tritype)),
        "instinkty": {k: round(v, 2) for k, v in inst_pr.items()},
        "instinkty_stack": "/".join(stack),
        "podtyp": f"{stack[0]}{top}" if stack else None,
        "rychly_test": rychly, "rychly_test_misto": misto,
        "varovani": var,
    }


def tisk(r):
    o = []
    top = r["nejpravdepodobnejsi"]
    o.append("ENNEAGRAM – výsledek orientačního dotazníku")
    o.append("=" * 46)
    o.append(f"Nejvyšší skóre: typ {top} – {NAZVY[top]}  ({r['kridlo_text']})")
    if r["instinkty_stack"]:
        o.append(f"Instinkty: {r['instinkty_stack']}  → podtyp {r['podtyp']}")
    o.append(f"Kandidáti k ověření: " + ", ".join(f"{t} {NAZVY[t]}" for t in r["kandidati"]))
    o.append(f"Šipky typu {top}: stres → {r['stres']}, růst → {r['rust']}")
    o.append(f"Orientační tritype: {r['tritype_orientacne']}")
    if r["rychly_test"]:
        o.append(f"Rychlý test (část A): typ {r['rychly_test']} – v dotazníku na {r['rychly_test_misto']}. místě")
    o.append("")
    o.append("Typy (průměr 1–5):")
    for t in r["poradi"]:
        s = float(r["prumery"][str(t)])
        o.append(f"  {t} {NAZVY[t]:<15} {s:4.2f}  {'█' * round((s - 1) * 8)}")
    o.append("")
    o.append("Centra: " + ", ".join(f"{c} {v:.2f}" for c, v in r["centra"].items()))
    if r["instinkty"]:
        o.append("Instinkty: " + ", ".join(f"{k} ({INST_NAZVY[k]}) {v:.2f}" for k, v in r["instinkty"].items()))
    if r["varovani"]:
        o.append("")
        o.append("Upozornění:")
        o += [f"  ! {v}" for v in r["varovani"]]
    o.append("")
    o.append("Výsledek je hypotéza k ověření rozhovorem (references/rozlisovani.md), ne diagnóza.")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("odpovedi", nargs="?", help="JSON s odpověďmi, vyplněný .md, nebo - pro stdin")
    ap.add_argument("--sablona", action="store_true", help="vypíše prázdnou JSON šablonu odpovědí")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    a = ap.parse_args()
    d = nacti_dotaznik()
    if a.sablona:
        print(json.dumps(sablona(d), ensure_ascii=False, indent=1))
        return
    if not a.odpovedi:
        ap.error("chybí soubor s odpověďmi (nebo použij --sablona)")
    r = vyhodnot(d, nacti_odpovedi(a.odpovedi))
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.format == "json" else tisk(r))


if __name__ == "__main__":
    main()
