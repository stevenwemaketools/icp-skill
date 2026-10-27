#!/usr/bin/env python3
"""icp.json -> branded PDF, with the Python standard library only.

The lead's ICP (written by the /icp skill as icp.json) becomes an A4 document on True Black pages
with lime headings: the North Star on the cover, the profile, the evidence, the anti-ICP, where to
find them and how they buy, the 30-day plan, and a closing page with the two allowed calls to action.
No third-party package, no network, no fonts to install: the PDF standard fonts (Helvetica, Courier)
are used with WinAnsi encoding so Spanish accents render everywhere.

Usage:
  python3 make_pdf.py --input icp.json --out-dir ./out [--basename icp] [--md] [--html] [--compress]
  python3 make_pdf.py --input icp.json --validate-only

Exit codes: 0 written, 2 the icp.json failed validation (the errors are listed).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

PAGE_W, PAGE_H = 595.28, 841.89
M_L, M_R, M_T, M_B = 56.0, 56.0, 68.0, 52.0
CONTENT_W = PAGE_W - M_L - M_R
COURIER_W = 600
FONT_RES = {"Helvetica": "F1", "Helvetica-Bold": "F2", "Courier": "F3", "Courier-Bold": "F4"}
BODY, BOLD, MONO, MONOB = "Helvetica", "Helvetica-Bold", "Courier", "Courier-Bold"

# WinAnsi (cp1252) glyph widths, codes 32..255, in 1/1000 em. Source: Adobe Core 14 AFM files
# (Helvetica.afm, Helvetica-Bold.afm) as shipped in Apache PDFBox. Courier faces are fixed at 600.
WIDTHS = {
    "Helvetica": (
        278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
        556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
        1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
        667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
        333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
        556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584, 278,
        556, 278, 222, 556, 333, 1000, 556, 556, 333, 1000, 667, 333, 1000, 278, 611, 278,
        278, 222, 222, 333, 333, 350, 556, 1000, 333, 1000, 500, 333, 944, 278, 500, 667,
        278, 333, 556, 556, 556, 556, 260, 556, 333, 737, 370, 556, 584, 333, 737, 333,
        400, 584, 333, 333, 333, 556, 537, 278, 333, 333, 365, 556, 834, 834, 834, 611,
        667, 667, 667, 667, 667, 667, 1000, 722, 667, 667, 667, 667, 278, 278, 278, 278,
        722, 722, 778, 778, 778, 778, 778, 584, 778, 722, 722, 722, 722, 667, 667, 611,
        556, 556, 556, 556, 556, 556, 889, 500, 556, 556, 556, 556, 278, 278, 278, 278,
        556, 556, 556, 556, 556, 556, 556, 584, 611, 556, 556, 556, 556, 500, 556, 500,
    ),
    "Helvetica-Bold": (
        278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278,
        556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611,
        975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
        667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556,
        333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
        611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584, 278,
        556, 278, 278, 556, 500, 1000, 556, 556, 333, 1000, 667, 333, 1000, 278, 611, 278,
        278, 278, 278, 500, 500, 350, 556, 1000, 333, 1000, 556, 333, 944, 278, 500, 667,
        278, 333, 556, 556, 556, 556, 280, 556, 333, 737, 370, 556, 584, 333, 737, 333,
        400, 584, 333, 333, 333, 611, 556, 278, 333, 333, 365, 556, 834, 834, 834, 611,
        722, 722, 722, 722, 722, 722, 1000, 722, 667, 667, 667, 667, 278, 278, 278, 278,
        722, 722, 778, 778, 778, 778, 778, 584, 778, 722, 722, 722, 722, 667, 667, 611,
        556, 556, 556, 556, 556, 556, 889, 556, 556, 556, 556, 556, 278, 278, 278, 278,
        611, 611, 611, 611, 611, 611, 611, 584, 611, 611, 611, 611, 611, 556, 611, 556,
    ),
}

# ----------------------------------------------------------------------------- fixed strings
STRINGS = {
    "es": {
        "cover_eyebrow": "TU CLIENTE IDEAL", "north_star": "NORTH STAR", "date": "FECHA",
        "generated": "Generado con el skill /icp de We Make Tools.",
        "footer": "Tu cliente ideal · North Star",
        "s_profile": "El perfil", "s_evidence": "Por qué este cliente", "s_anti": "Quién NO es tu cliente",
        "s_where": "Dónde encontrarlo y cómo compra", "s_plan": "Plan de 30 días y métricas", "s_close": "Siguiente paso",
        "requirements": "REQUISITOS", "requirement": "REQUISITO", "demographics": "PERFIL", "before": "ANTES", "after": "DESPUÉS",
        "aspirations": "ASPIRACIONES", "pain_language": "EN SUS PALABRAS", "basis": "BASE DE LA DECISIÓN",
        "top_customers": "TUS MEJORES CLIENTES", "separation": "PRUEBA DE SEPARACIÓN", "separation_pass": "Pasó",
        "separation_fail": "No pasó", "scores": "INDICADORES DE MERCADO", "total": "Total",
        "score_pain": "Dolor", "score_purchasing_power": "Capacidad de pago", "score_easy_to_target": "Fácil de encontrar",
        "score_growing": "En crecimiento", "band_32": "Mercado fuerte", "band_24": "Mercado atractivo",
        "band_16": "Mercado difícil", "band_0": "Mercado débil",
        "rwa": "LISTO · DISPUESTO · CAPAZ", "ready": "Listo", "willing": "Dispuesto", "able": "Capaz",
        "checks": "SEÑALES", "talk": "Hablan entre ellos", "list100": "100 nombres en una semana", "yes": "Sí", "no": "No",
        "ladder": "ESCALERA DE NICHO", "segments": "SEGMENTOS EVALUADOS", "picked": "ELEGIDO",
        "anti": "NO ES PARA", "anti_callout": "Decir que no es parte del perfil. Cada cliente fuera del perfil cuesta margen, tiempo y energía.",
        "watering": "DÓNDE ESTÁN", "buying": "CÓMO COMPRAN", "dream100": "DREAM 100 · PRIMEROS NOMBRES",
        "week": "Semana", "metrics": "MÉTRICAS", "metric": "Métrica", "target": "Meta",
        "next10": "TUS PRÓXIMOS 10 CLIENTES", "open": "POR CONFIRMAR",
        "closing_p": "Este perfil es una hipótesis con evidencia. Se confirma con tus próximos 10 clientes: si encajan en los requisitos y compran más rápido, el North Star es correcto. Si no, ajusta un calificador y vuelve a probar.",
        "demo_industry": "Industria", "demo_size": "Tamaño", "demo_role": "Quién compra", "demo_location": "Ubicación",
        "demo_stage": "Etapa", "demo_ticket": "Ticket", "lang_code": "es-419",
        "metric_defaults": [["LTGP : CAC", "3 a 1 o mejor"], ["Tasa de cierre", "30% o mejor"], ["Retención a 90 días", "Igual o mejor que tus mejores clientes"]],
        "hypothesis": "hipótesis",
    },
    "en": {
        "cover_eyebrow": "YOUR IDEAL CUSTOMER", "north_star": "NORTH STAR", "date": "DATE",
        "generated": "Generated with the /icp skill by We Make Tools.",
        "footer": "Your ideal customer · North Star",
        "s_profile": "The profile", "s_evidence": "Why this customer", "s_anti": "Who is NOT your customer",
        "s_where": "Where to find them and how they buy", "s_plan": "30-day plan and metrics", "s_close": "Next step",
        "requirements": "REQUIREMENTS", "requirement": "REQUIREMENT", "demographics": "PROFILE", "before": "BEFORE", "after": "AFTER",
        "aspirations": "ASPIRATIONS", "pain_language": "IN THEIR WORDS", "basis": "BASIS OF THE DECISION",
        "top_customers": "YOUR BEST CUSTOMERS", "separation": "SEPARATION TEST", "separation_pass": "Passed",
        "separation_fail": "Did not pass", "scores": "MARKET INDICATORS", "total": "Total",
        "score_pain": "Pain", "score_purchasing_power": "Purchasing power", "score_easy_to_target": "Easy to target",
        "score_growing": "Growing", "band_32": "Strong market", "band_24": "Attractive market",
        "band_16": "Difficult market", "band_0": "Weak market",
        "rwa": "READY · WILLING · ABLE", "ready": "Ready", "willing": "Willing", "able": "Able",
        "checks": "SIGNALS", "talk": "They talk to each other", "list100": "100 names in a week", "yes": "Yes", "no": "No",
        "ladder": "NICHE LADDER", "segments": "SEGMENTS CONSIDERED", "picked": "PICKED",
        "anti": "NOT FOR", "anti_callout": "Saying no is part of the profile. Every customer outside it costs margin, time and energy.",
        "watering": "WHERE THEY ARE", "buying": "HOW THEY BUY", "dream100": "DREAM 100 · FIRST NAMES",
        "week": "Week", "metrics": "METRICS", "metric": "Metric", "target": "Target",
        "next10": "YOUR NEXT 10 CUSTOMERS", "open": "TO CONFIRM",
        "closing_p": "This profile is a hypothesis with evidence. Your next 10 customers confirm it: if they fit the requirements and buy faster, the North Star is right. If not, adjust one qualifier and test again.",
        "demo_industry": "Industry", "demo_size": "Size", "demo_role": "Who buys", "demo_location": "Location",
        "demo_stage": "Stage", "demo_ticket": "Ticket", "lang_code": "en",
        "metric_defaults": [["LTGP : CAC", "3 to 1 or better"], ["Close rate", "30% or better"], ["90-day retention", "Equal or better than your best customers"]],
        "hypothesis": "hypothesis",
    },
}

FALLBACK = {
    "\u2014": ", ", "―": ", ", "‒": "-", "→": "->", "←": "<-", "➔": "->", "⇒": "=>",
    "✓": "ok", "✔": "ok", "✗": "x", "✘": "x", " ": " ", " ": " ", " ": " ",
    "•": "•", "■": "•", "▪": "•", "★": "*", "☆": "*", "×": "x",
    "≤": "<=", "≥": ">=", "≈": "~", "‚": "'", "′": "'", "″": '"',
}
WARNINGS: list[str] = []


# ----------------------------------------------------------------------------- text
def normalize_text(s) -> str:
    """Make a string safe for the PDF and for the brand's copy rules.

    Dashes used as punctuation are not allowed in client-facing copy, so an em dash becomes a comma
    and a spaced en dash or spaced hyphen becomes a comma too. Characters outside cp1252 are mapped
    to a close equivalent, stripped of their accents, or dropped with a warning."""
    if s is None:
        return ""
    s = str(s)
    s = s.replace(" \u2013 ", ", ").replace(" - ", ", ").replace("\u2013", "-")
    for k, v in FALLBACK.items():
        s = s.replace(k, v)
    out = []
    for ch in s:
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            base = unicodedata.normalize("NFKD", ch)
            base = "".join(c for c in base if not unicodedata.combining(c))
            try:
                base.encode("cp1252")
                out.append(base)
            except UnicodeEncodeError:
                WARNINGS.append(f"dropped unsupported character U+{ord(ch):04X}")
    s = "".join(out)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"\s+,", ",", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def pdf_escape(s: str) -> bytes:
    raw = s.encode("cp1252", "replace")
    out = bytearray()
    for b in raw:
        if b in (0x28, 0x29, 0x5C):
            out += b"\\" + bytes([b])
        elif b < 32 or b > 126:
            out += ("\\%03o" % b).encode("ascii")
        else:
            out.append(b)
    return bytes(out)


def text_width(s: str, font: str, size: float, tc: float = 0.0) -> float:
    if font.startswith("Courier"):
        w = COURIER_W * len(s)
    else:
        table = WIDTHS[font]
        w = 0
        for ch in s:
            code = ch.encode("cp1252", "replace")[0]
            w += table[code - 32] if 32 <= code <= 255 else 278
    return w / 1000.0 * size + max(len(s) - 1, 0) * tc


def wrap(s: str, font: str, size: float, max_w: float, tc: float = 0.0) -> list[str]:
    lines: list[str] = []
    for para in s.split("\n"):
        words = para.split(" ")
        line = ""
        for word in words:
            while text_width(word, font, size, tc) > max_w:  # hard-split a word longer than the line
                cut = max(1, int(len(word) * max_w / max(text_width(word, font, size, tc), 1)) - 1)
                if line:
                    lines.append(line)
                    line = ""
                lines.append(word[:cut])
                word = word[cut:]
            candidate = word if not line else line + " " + word
            if text_width(candidate, font, size, tc) <= max_w:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    return lines


def fit_lines(s: str, font: str, sizes: list[float], max_w: float, max_lines: int) -> tuple[float, list[str]]:
    for size in sizes:
        lines = wrap(s, font, size, max_w)
        if len(lines) <= max_lines:
            return size, lines
    return sizes[-1], wrap(s, font, sizes[-1], max_w)


def rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return f"{r:.3f} {g:.3f} {b:.3f}"


def fmt(n: float) -> str:
    return f"{n:.2f}".rstrip("0").rstrip(".") if isinstance(n, float) else str(n)


# ----------------------------------------------------------------------------- document model
def band_key(total: int) -> str:
    return "band_32" if total >= 32 else "band_24" if total >= 24 else "band_16" if total >= 16 else "band_0"


def load_brand(path: Path | None = None) -> dict:
    p = path or (ASSETS / "brand.json")
    if not p.exists():
        raise SystemExit(f"brand file not found: {p} (the skill folder is incomplete)")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_icp(d: dict) -> list[str]:
    e: list[str] = []
    def need(path: str, cond: bool, msg: str) -> None:
        if not cond:
            e.append(f"{path}: {msg}")
    lang = d.get("lang")
    need("lang", lang in ("es", "en"), "must be 'es' or 'en'")
    need("path", d.get("path") in ("A", "B"), "must be 'A' (has customers) or 'B' (no customers yet)")
    need("generated_at", bool(d.get("generated_at")), "missing (ISO date)")
    biz = d.get("business") or {}
    need("business.name", bool(biz.get("name")), "missing")
    need("business.offer", bool(biz.get("offer")), "missing")
    ns = normalize_text(d.get("north_star", ""))
    need("north_star", bool(ns), "missing")
    need("north_star", len(ns) <= 220, f"too long ({len(ns)} chars, max 220); one sentence")
    need("north_star", ". " not in ns.rstrip(".") and "? " not in ns, "must be ONE sentence")
    prof = d.get("profile") or {}
    need("profile.label", bool(prof.get("label")), "missing (the avatar in a few words)")
    reqs = prof.get("requirements") or []
    need("profile.requirements", 3 <= len(reqs) <= 5, f"needs 3 to 5 items, has {len(reqs)}")
    for i, r in enumerate(reqs):
        need(f"profile.requirements[{i}]", isinstance(r, dict) and bool(r.get("name")), "needs {name, why}")
    ev = d.get("evidence") or {}
    need("evidence.basis", bool(ev.get("basis")), "missing (e.g. 'top 20% de 40 clientes' or 'hipótesis')")
    ms = ev.get("market_scores") or {}
    for k in ("pain", "purchasing_power", "easy_to_target", "growing"):
        v = ms.get(k)
        need(f"evidence.market_scores.{k}", isinstance(v, int) and 1 <= v <= 10, "integer 1 to 10")
    if d.get("path") == "A":
        st = ev.get("separation_test") or {}
        need("evidence.separation_test.passed", isinstance(st.get("passed"), bool), "boolean required on path A")
        need("evidence.separation_test.note", bool(st.get("note")), "one line explaining the test")
    else:
        segs = ev.get("segments_considered") or []
        need("evidence.segments_considered", len(segs) >= 3, f"path B needs 3 or more segments, has {len(segs)}")
        need("evidence.segments_considered", sum(1 for s in segs if s.get("picked")) == 1, "exactly one segment must have picked: true")
        n10 = d.get("next_10_customers") or []
        need("next_10_customers", len(n10) >= 5, f"path B needs 5 or more entries, has {len(n10)}")
    anti = d.get("anti_icp") or []
    need("anti_icp", 3 <= len(anti) <= 6, f"needs 3 to 6 items, has {len(anti)}")
    for i, a in enumerate(anti):
        need(f"anti_icp[{i}]", isinstance(a, dict) and bool(a.get("who")), "needs {who, why}")
    wh = d.get("where") or {}
    need("where.watering_holes", len(wh.get("watering_holes") or []) >= 3, "needs 3 or more {place, type}")
    need("where.buying_path", len(wh.get("buying_path") or []) >= 3, "needs 3 or more {step}")
    plan = d.get("plan_30_days") or []
    need("plan_30_days", len(plan) == 4, f"needs exactly 4 weeks, has {len(plan)}")
    for i, w in enumerate(plan):
        need(f"plan_30_days[{i}]", isinstance(w, dict) and bool(w.get("actions")), "needs {week, actions[]}")
    raw = json.dumps(d, ensure_ascii=False)
    dashes = raw.count("\u2014") + raw.count("\u2013")
    if dashes:
        WARNINGS.append(f"{dashes} dash(es) found in icp.json and rewritten as commas; client-facing copy uses no dash punctuation")
    return e


def build_model(d: dict, brand: dict) -> list[dict]:
    """Turn icp.json into a list of pages made of simple blocks (shared by the PDF, MD and HTML renderers)."""
    lang = d["lang"]
    S = STRINGS[lang]
    T = normalize_text
    biz, prof, ev, wh = d["business"], d["profile"], d["evidence"], d["where"]
    pages: list[dict] = []

    # cover
    pages.append({"kind": "cover", "eyebrow": S["cover_eyebrow"], "business": T(biz["name"]), "north_star": T(d["north_star"]),
                  "date": T(d.get("generated_at", "")), "generated": S["generated"], "privacy": T(brand["privacy"][lang])})

    # 01 profile
    blocks: list[dict] = [{"type": "subheading", "text": T(prof["label"])}, {"type": "label", "text": S["requirements"]}]
    blocks.append({"type": "cards", "items": [{"label": f"{S['requirement']} {i:02d}", "title": T(r.get("name")), "body": T(r.get("why"))}
                                               for i, r in enumerate(prof["requirements"], 1)]})
    demo = prof.get("demographics") or {}
    kv = [(S[f"demo_{k}"], T(demo[k])) for k in ("industry", "size", "role", "location", "stage", "ticket") if demo.get(k)]
    if kv:
        blocks += [{"type": "label", "text": S["demographics"]}, {"type": "kv", "items": kv}]
    if prof.get("situation_before") or prof.get("situation_after"):
        blocks.append({"type": "pair", "items": [{"label": S["before"], "body": T(prof.get("situation_before"))},
                                                 {"label": S["after"], "body": T(prof.get("situation_after"))}]})
    if prof.get("aspirations"):
        blocks += [{"type": "label", "text": S["aspirations"]}, {"type": "bullets", "items": [T(x) for x in prof["aspirations"]]}]
    if prof.get("pain_language"):
        blocks.append({"type": "label", "text": S["pain_language"]})
        blocks += [{"type": "quote", "text": T(q)} for q in prof["pain_language"]]
    pages.append({"kind": "section", "num": "01", "title": S["s_profile"], "blocks": blocks})

    # 02 evidence
    blocks = [{"type": "label", "text": S["basis"]}, {"type": "paragraph", "text": T(ev["basis"])}]
    if ev.get("top_customers"):
        blocks += [{"type": "label", "text": S["top_customers"]},
                   {"type": "bullets", "items": [T(f"{c.get('alias', '')}: {c.get('why', '')}").strip(": ") for c in ev["top_customers"]]}]
    if d["path"] == "A":
        st = ev.get("separation_test") or {}
        verdict = S["separation_pass"] if st.get("passed") else S["separation_fail"]
        blocks.append({"type": "callout", "label": S["separation"], "text": T(f"{verdict}. {st.get('note', '')}")})
    ms = ev["market_scores"]
    total = sum(int(ms[k]) for k in ("pain", "purchasing_power", "easy_to_target", "growing"))
    blocks.append({"type": "label", "text": S["scores"]})
    blocks.append({"type": "scores", "items": [{"name": S[f"score_{k}"], "score": int(ms[k])} for k in ("pain", "purchasing_power", "easy_to_target", "growing")],
                   "total": total, "band": S[band_key(total)]})
    rwa = ev.get("rwa") or {}
    badges = []
    if rwa:
        badges += [{"name": S[k], "value": bool(rwa.get(k))} for k in ("ready", "willing", "able")]
    if "talk_to_each_other" in ev:
        badges.append({"name": S["talk"], "value": bool(ev.get("talk_to_each_other"))})
    if "list_100_in_a_week" in ev:
        badges.append({"name": S["list100"], "value": bool(ev.get("list_100_in_a_week"))})
    if badges:
        blocks += [{"type": "label", "text": S["checks"]}, {"type": "badges", "items": badges, "yes": S["yes"], "no": S["no"]}]
    if ev.get("niche_ladder"):
        blocks += [{"type": "label", "text": S["ladder"]},
                   {"type": "steps", "items": [{"title": T(x.get("level")), "body": T(x.get("note"))} for x in ev["niche_ladder"]]}]
    if ev.get("segments_considered"):
        rows = []
        for s in ev["segments_considered"]:
            sc = s.get("scores") or {}
            tot = s.get("total") or sum(int(sc.get(k, 0)) for k in ("pain", "purchasing_power", "easy_to_target", "growing"))
            rows.append({"name": T(s.get("name")), "total": int(tot), "picked": bool(s.get("picked")), "note": T(s.get("note", ""))})
        blocks += [{"type": "label", "text": S["segments"]}, {"type": "segments", "items": rows, "picked_label": S["picked"]}]
    pages.append({"kind": "section", "num": "02", "title": S["s_evidence"], "blocks": blocks})

    # 03 anti
    blocks = [{"type": "label", "text": S["anti"]},
              {"type": "cards", "items": [{"label": f"{i:02d}", "title": T(a.get("who")), "body": T(a.get("why"))} for i, a in enumerate(d["anti_icp"], 1)], "bar": True},
              {"type": "callout", "label": "", "text": S["anti_callout"]}]
    pages.append({"kind": "section", "num": "03", "title": S["s_anti"], "blocks": blocks})

    # 04 where / how
    blocks = [{"type": "label", "text": S["watering"]}]
    groups: dict[str, list[str]] = {}
    for w in wh["watering_holes"]:
        groups.setdefault(T(w.get("type") or ""), []).append(T(w.get("place")))
    for typ, places in groups.items():
        blocks.append({"type": "bullets", "items": places, "head": typ})
    blocks += [{"type": "label", "text": S["buying"]},
               {"type": "steps", "items": [{"title": T(s.get("step")), "body": T(s.get("note", ""))} for s in wh["buying_path"]]}]
    if wh.get("dream_100_seed"):
        blocks += [{"type": "label", "text": S["dream100"]}, {"type": "twocol", "items": [T(x) for x in wh["dream_100_seed"]]}]
    pages.append({"kind": "section", "num": "04", "title": S["s_where"], "blocks": blocks})

    # 05 plan
    blocks = [{"type": "weeks", "items": [{"title": f"{S['week']} {w.get('week', i)}", "items": [T(a) for a in w.get("actions", [])]}
                                          for i, w in enumerate(d["plan_30_days"], 1)]}]
    metrics = d.get("metrics") or []
    rows = [(T(m.get("name")), T(m.get("target"))) for m in metrics if isinstance(m, dict)] or [tuple(x) for x in S["metric_defaults"]]
    blocks += [{"type": "label", "text": S["metrics"]}, {"type": "table", "head": (S["metric"], S["target"]), "rows": rows}]
    if d.get("next_10_customers"):
        blocks += [{"type": "label", "text": S["next10"]}, {"type": "bullets", "items": [T(x) for x in d["next_10_customers"]]}]
    if d.get("open_questions"):
        blocks += [{"type": "label", "text": S["open"]}, {"type": "bullets", "items": [T(x) for x in d["open_questions"]]}]
    pages.append({"kind": "section", "num": "05", "title": S["s_plan"], "blocks": blocks})

    # closing
    cta = brand["cta"]
    override = (d.get("cta") or {}).get("override")
    lines = [{"label": T(cta["audit"]["label"][lang]), "line": T(cta["audit"]["line"][lang]), "url": cta["audit"]["url"]},
             {"label": T(cta["build"]["label"][lang]), "line": T(cta["build"]["line"][lang]), "url": cta["build"]["url"]}]
    headline = T(cta["headline"][lang])
    if isinstance(override, dict):
        headline = T(override.get("headline") or headline)
        if override.get("lines"):
            lines = [{"label": T(x.get("label")), "line": T(x.get("line", "")), "url": x.get("url", "")} for x in override["lines"]]
    pages.append({"kind": "closing", "title": S["s_close"], "paragraph": S["closing_p"], "headline": headline, "lines": lines,
                  "privacy": T(brand["privacy"][lang]), "tagline": T(brand["wordmark"]["tagline"])})
    return pages


# ----------------------------------------------------------------------------- PDF renderer
K = 0.5523


class Pdf:
    def __init__(self, brand: dict, lang: str, business: str):
        self.c = brand["colors"]
        self.S = STRINGS[lang]
        self.lang = lang
        self.business = business
        self.wordmark_text = brand["wordmark"]["text"]
        self.pages: list[list[bytes]] = []
        self.ops: list[bytes] = []
        self.y = PAGE_H - M_T
        self.section_name = ""

    # --- low level
    def op(self, s: str) -> None:
        self.ops.append(s.encode("latin-1"))

    def rect(self, x, y, w, h, fill: str) -> None:
        self.op(f"q {rgb(fill)} rg {fmt(x)} {fmt(y)} {fmt(w)} {fmt(h)} re f Q")

    def rounded_rect(self, x, y, w, h, r, fill: str | None, stroke: str | None = None, lw: float = 0.75) -> None:
        k = K * r
        path = (f"{fmt(x + r)} {fmt(y)} m {fmt(x + w - r)} {fmt(y)} l "
                f"{fmt(x + w - r + k)} {fmt(y)} {fmt(x + w)} {fmt(y + r - k)} {fmt(x + w)} {fmt(y + r)} c "
                f"{fmt(x + w)} {fmt(y + h - r)} l {fmt(x + w)} {fmt(y + h - r + k)} {fmt(x + w - r + k)} {fmt(y + h)} {fmt(x + w - r)} {fmt(y + h)} c "
                f"{fmt(x + r)} {fmt(y + h)} l {fmt(x + r - k)} {fmt(y + h)} {fmt(x)} {fmt(y + h - r + k)} {fmt(x)} {fmt(y + h - r)} c "
                f"{fmt(x)} {fmt(y + r)} l {fmt(x)} {fmt(y + r - k)} {fmt(x + r - k)} {fmt(y)} {fmt(x + r)} {fmt(y)} c h")
        paint = "B" if (fill and stroke) else "f" if fill else "S"
        pre = (f"{rgb(fill)} rg " if fill else "") + (f"{rgb(stroke)} RG {fmt(lw)} w " if stroke else "")
        self.op(f"q {pre}{path} {paint} Q")

    def line(self, x1, y1, x2, y2, w: float, color: str) -> None:
        self.op(f"q {rgb(color)} RG {fmt(w)} w {fmt(x1)} {fmt(y1)} m {fmt(x2)} {fmt(y2)} l S Q")

    def text(self, x, y, s: str, font: str, size: float, color: str, tc: float = 0.0) -> None:
        if not s:
            return
        esc = pdf_escape(s).decode("latin-1")
        self.op(f"BT /{FONT_RES[font]} {fmt(size)} Tf {fmt(tc)} Tc {rgb(color)} rg {fmt(x)} {fmt(y)} Td ({esc}) Tj ET")

    # --- pages
    def new_page(self, running: bool = True) -> None:
        self.ops = []
        self.pages.append(self.ops)
        self.rect(0, 0, PAGE_W, PAGE_H, self.c["black"])
        self.y = PAGE_H - M_T
        if running:
            self.text(M_L, PAGE_H - 36, self.S["cover_eyebrow"], MONOB, 7, self.c["gray_600"], 1.2)
            right = self.business.upper()
            w = text_width(right, MONO, 7, 1.0)
            self.text(PAGE_W - M_R - w, PAGE_H - 36, right, MONO, 7, self.c["gray_600"], 1.0)
            self.line(M_L, PAGE_H - 44, PAGE_W - M_R, PAGE_H - 44, 0.5, self.c["charcoal"])

    def ensure(self, h: float) -> None:
        if self.y - h < M_B:
            self.new_page()

    # --- flow primitives
    def label(self, s: str, color: str | None = None, square: bool = True, gap: float = 10) -> None:
        self.ensure(60)
        self.y -= 8
        x = M_L
        if square:
            self.rect(M_L, self.y - 0.5, 5, 5, self.c["lime"])
            x = M_L + 10
        self.text(x, self.y, s.upper(), MONOB, 7.5, color or self.c["gray_600"], 1.2)
        self.y -= gap + 6

    def heading(self, num: str, s: str) -> None:
        self.ensure(60)
        indent = 30 if num else 0
        if num:
            self.text(M_L, self.y - 8, num, MONOB, 9, self.c["lime"], 1.5)
        size, lines = fit_lines(s, BOLD, [22, 20, 18], CONTENT_W - indent - 6, 2)
        y = self.y - 8
        for ln in lines:
            self.text(M_L + indent, y, ln, BOLD, size, self.c["white"])
            y -= size * 1.15
        self.y = y + size * 0.3
        self.rect(M_L, self.y - 6, 56, 4, self.c["lime"])
        self.y -= 22

    def subheading(self, s: str) -> None:
        size, lines = fit_lines(s, BOLD, [14, 13, 12], CONTENT_W, 3)
        self.ensure(len(lines) * size * 1.25 + 6)
        for ln in lines:
            self.text(M_L, self.y - size, ln, BOLD, size, self.c["white"])
            self.y -= size * 1.25
        self.y -= 4

    def paragraph(self, s: str, size: float = 10.5, color: str | None = None, leading: float = 15, x: float | None = None, max_w: float | None = None, font: str = BODY) -> float:
        x = M_L if x is None else x
        lines = wrap(s, font, size, max_w or (CONTENT_W - (x - M_L)))
        start = self.y
        for i, ln in enumerate(lines):
            self.ensure(leading)
            self.text(x, self.y - size, ln, font, size, color or self.c["gray_400"])
            self.y -= leading
        self.y -= 8
        return start - self.y

    def bullets(self, items: list[str], head: str | None = None) -> None:
        if head:
            self.ensure(18)
            self.text(M_L, self.y - 10, head, BOLD, 10.5, self.c["white"])
            self.y -= 18
        for it in items:
            lines = wrap(it, BODY, 10.5, CONTENT_W - 16)
            self.ensure(15)
            self.rect(M_L + 1, self.y - 9.5, 5, 5, self.c["lime"])
            for ln in lines:
                self.ensure(15)
                self.text(M_L + 16, self.y - 10.5, ln, BODY, 10.5, self.c["gray_400"])
                self.y -= 15
        self.y -= 6

    def card(self, label: str, title: str, body: str, bar: bool = False, x: float = M_L, w: float = CONTENT_W) -> None:
        pad = 12
        inner = w - 2 * pad - (6 if bar else 0)
        t_lines = wrap(title, BOLD, 12, inner) if title else []
        b_lines = wrap(body, BODY, 10, inner) if body else []
        h = pad + (11 if label else 0) + len(t_lines) * 14 + (3 if t_lines else 0) + len(b_lines) * 13 + pad - 4
        self.ensure(h + 6)
        top = self.y
        self.rounded_rect(x, top - h, w, h, 6, self.c["off_black"], self.c["charcoal"])
        if bar:
            self.rect(x, top - h + 8, 3, h - 16, self.c["lime"])
        tx = x + pad + (6 if bar else 0)
        y = top - pad
        if label:
            self.text(tx, y - 6, label.upper(), MONOB, 7, self.c["gray_600"], 1.2)
            y -= 13
        for ln in t_lines:
            self.text(tx, y - 11, ln, BOLD, 12, self.c["white"])
            y -= 14
        y -= 1
        for ln in b_lines:
            self.text(tx, y - 9.5, ln, BODY, 10, self.c["gray_400"])
            y -= 13
        self.y = top - h - 6

    def callout(self, label: str, body: str) -> None:
        lines = wrap(body, BODY, 10.5, CONTENT_W - 22)
        h = len(lines) * 15 + (16 if label else 4) + 8
        self.ensure(h + 6)
        top = self.y
        self.rect(M_L, top - h, 3, h, self.c["lime"])
        y = top - 6
        if label:
            self.text(M_L + 16, y - 7, label.upper(), MONOB, 7.5, self.c["gray_600"], 1.2)
            y -= 16
        for ln in lines:
            self.text(M_L + 16, y - 10.5, ln, BODY, 10.5, self.c["white"])
            y -= 15
        self.y = top - h - 10

    def scores(self, items: list[dict], total: int, band: str) -> None:
        self.ensure(len(items) * 20 + 30)
        track_x, track_w = M_L + 160, CONTENT_W - 160 - 40
        for it in items:
            self.text(M_L, self.y - 10, it["name"], BODY, 10.5, self.c["white"])
            self.rect(track_x, self.y - 9, track_w, 6, self.c["gray_800"])
            self.rect(track_x, self.y - 9, track_w * max(0, min(10, it["score"])) / 10.0, 6, self.c["lime"])
            num = f"{it['score']:>2}/10"
            self.text(PAGE_W - M_R - text_width(num, MONO, 9), self.y - 10, num, MONO, 9, self.c["lime"])
            self.y -= 20
        self.y -= 2
        self.line(M_L, self.y, PAGE_W - M_R, self.y, 0.5, self.c["charcoal"])
        self.y -= 14
        self.text(M_L, self.y - 2, f"{self.S['total']} {total}/40", BOLD, 11, self.c["white"])
        bw = text_width(band.upper(), MONOB, 8, 1.2)
        self.text(PAGE_W - M_R - bw, self.y - 2, band.upper(), MONOB, 8, self.c["lime"], 1.2)
        self.y -= 18

    def badges(self, items: list[dict], yes: str, no: str) -> None:
        x = M_L
        self.ensure(26)
        for it in items:
            txt = f"{it['name']}: {yes if it['value'] else no}"
            w = text_width(txt, MONO, 8, 0.5) + 16
            if x + w > PAGE_W - M_R:
                x = M_L
                self.y -= 24
                self.ensure(26)
            color = self.c["lime"] if it["value"] else self.c["gray_600"]
            self.rounded_rect(x, self.y - 17, w, 18, 4, None, color, 0.75)
            self.text(x + 8, self.y - 12, txt, MONO, 8, color, 0.5)
            x += w + 8
        self.y -= 30

    def steps(self, items: list[dict]) -> None:
        for i, it in enumerate(items, 1):
            t_lines = wrap(it.get("title") or "", BOLD, 11, CONTENT_W - 34)
            b_lines = wrap(it.get("body") or "", BODY, 10, CONTENT_W - 34) if it.get("body") else []
            h = max(1, len(t_lines)) * 14 + len(b_lines) * 14 + 8
            self.ensure(h)
            self.text(M_L, self.y - 14, f"{i:02d}", BOLD, 15, self.c["lime"])
            y = self.y
            for ln in t_lines:
                self.text(M_L + 34, y - 11, ln, BOLD, 11, self.c["white"])
                y -= 14
            for ln in b_lines:
                self.text(M_L + 34, y - 10, ln, BODY, 10, self.c["gray_400"])
                y -= 14
            self.y = y - 8

    def kv(self, items: list[tuple[str, str]]) -> None:
        col_w = CONTENT_W / 2
        for i in range(0, len(items), 2):
            pair = items[i:i + 2]
            heights = []
            for j, (k, v) in enumerate(pair):
                heights.append(len(wrap(v, BODY, 10.5, col_w - 16)) * 14 + 14)
            h = max(heights)
            self.ensure(h + 6)
            for j, (k, v) in enumerate(pair):
                x = M_L + j * col_w
                self.text(x, self.y - 8, k.upper(), MONOB, 7, self.c["gray_600"], 1.2)
                y = self.y - 14
                for ln in wrap(v, BODY, 10.5, col_w - 16):
                    self.text(x, y - 10, ln, BODY, 10.5, self.c["white"])
                    y -= 14
            self.y -= h + 6

    def pair(self, items: list[dict]) -> None:
        gap = 12
        w = (CONTENT_W - gap) / 2
        heights = [len(wrap(it.get("body") or "", BODY, 10, w - 28)) * 13 + 36 for it in items]
        h = max(heights)
        self.ensure(h + 8)
        top = self.y
        for j, it in enumerate(items[:2]):
            x = M_L + j * (w + gap)
            self.rounded_rect(x, top - h, w, h, 6, self.c["off_black"], self.c["charcoal"])
            self.text(x + 14, top - 18, it["label"].upper(), MONOB, 7, self.c["gray_600"], 1.2)
            y = top - 26
            for ln in wrap(it.get("body") or "", BODY, 10, w - 28):
                self.text(x + 14, y - 10, ln, BODY, 10, self.c["gray_400"])
                y -= 13
        self.y = top - h - 8

    def twocol(self, items: list[str]) -> None:
        col_w = CONTENT_W / 2
        half = (len(items) + 1) // 2
        cols = [items[:half], items[half:]]
        rows = max(len(c) for c in cols)
        for r in range(rows):
            self.ensure(15)
            for j, col in enumerate(cols):
                if r < len(col):
                    x = M_L + j * col_w
                    self.rect(x + 1, self.y - 9.5, 5, 5, self.c["lime"])
                    txt = wrap(col[r], BODY, 10.5, col_w - 20)[0]
                    self.text(x + 14, self.y - 10.5, txt, BODY, 10.5, self.c["gray_400"])
            self.y -= 15
        self.y -= 6

    def weeks(self, items: list[dict]) -> None:
        for it in items:
            lines_per = [wrap(a, BODY, 10, CONTENT_W - 44) for a in it["items"]]
            h = 30 + sum(len(l) for l in lines_per) * 14 + 6
            self.ensure(h + 8)
            top = self.y
            self.rounded_rect(M_L, top - h, CONTENT_W, h, 6, self.c["off_black"], self.c["charcoal"])
            self.text(M_L + 14, top - 19, it["title"].upper(), MONOB, 8, self.c["lime"], 1.5)
            y = top - 32
            for lines in lines_per:
                self.rect(M_L + 15, y - 8.5, 5, 5, self.c["lime"])
                for ln in lines:
                    self.text(M_L + 30, y - 9.5, ln, BODY, 10, self.c["gray_400"])
                    y -= 14
            self.y = top - h - 8

    def table(self, head: tuple[str, str], rows: list[tuple[str, str]]) -> None:
        col1 = CONTENT_W * 0.42
        self.ensure(20)
        self.text(M_L, self.y - 8, head[0].upper(), MONOB, 7, self.c["gray_600"], 1.2)
        self.text(M_L + col1, self.y - 8, head[1].upper(), MONOB, 7, self.c["gray_600"], 1.2)
        self.y -= 14
        self.line(M_L, self.y, PAGE_W - M_R, self.y, 0.5, self.c["charcoal"])
        for a, b in rows:
            la, lb = wrap(a, BOLD, 10.5, col1 - 10), wrap(b, BODY, 10.5, CONTENT_W - col1)
            h = max(len(la), len(lb)) * 14 + 8
            self.ensure(h)
            y = self.y - 4
            for ln in la:
                self.text(M_L, y - 10, ln, BOLD, 10.5, self.c["white"])
                y -= 14
            y = self.y - 4
            for ln in lb:
                self.text(M_L + col1, y - 10, ln, BODY, 10.5, self.c["gray_400"])
                y -= 14
            self.y -= h
            self.line(M_L, self.y, PAGE_W - M_R, self.y, 0.5, self.c["charcoal"])
        self.y -= 10

    def segments(self, items: list[dict], picked_label: str) -> None:
        for it in items:
            n_lines = wrap(it["name"], BOLD, 11, CONTENT_W - 120)
            note = wrap(it.get("note") or "", BODY, 9.5, CONTENT_W - 120) if it.get("note") else []
            h = len(n_lines) * 14 + len(note) * 13 + 18
            self.ensure(h + 6)
            top = self.y
            fill = self.c["off_black"]
            stroke = self.c["lime"] if it["picked"] else self.c["charcoal"]
            self.rounded_rect(M_L, top - h, CONTENT_W, h, 6, fill, stroke, 1.0 if it["picked"] else 0.75)
            y = top - 9
            for ln in n_lines:
                self.text(M_L + 14, y - 11, ln, BOLD, 11, self.c["white"])
                y -= 14
            for ln in note:
                self.text(M_L + 14, y - 9, ln, BODY, 9.5, self.c["gray_400"])
                y -= 13
            score = f"{it['total']}/40"
            self.text(PAGE_W - M_R - 14 - text_width(score, MONOB, 10), top - 20, score, MONOB, 10, self.c["lime"] if it["picked"] else self.c["gray_400"])
            if it["picked"]:
                self.text(PAGE_W - M_R - 14 - text_width(picked_label, MONOB, 7, 1.2), top - 32, picked_label, MONOB, 7, self.c["lime"], 1.2)
            self.y = top - h - 8

    def quote(self, s: str) -> None:
        lines = wrap(s, BODY, 11, CONTENT_W - 22)
        h = len(lines) * 14 + 4
        self.ensure(h + 6)
        top = self.y
        self.rect(M_L, top - h + 2, 3, h - 4, self.c["lime"])
        y = top
        for ln in lines:
            self.text(M_L + 16, y - 11, ln, BODY, 11, self.c["white"])
            y -= 14
        self.y = top - h - 6

    def logo(self, x: float, y: float, s: float = 1.0) -> None:
        for i, color in enumerate((self.c["white"], self.c["white"], self.c["lime"])):
            self.rounded_rect(x + i * 10 * s, y + 11 * s, 8 * s, 8 * s, 2.2 * s, color)
        self.rounded_rect(x, y, 28 * s, 8 * s, 2.2 * s, self.c["white"])

    def wordmark(self, x: float, y: float, size: float, color: str | None = None) -> float:
        a, dot, b = self.wordmark_text.partition(".")
        self.text(x, y, a, BOLD, size, color or self.c["white"])
        x2 = x + text_width(a, BOLD, size)
        self.text(x2, y, dot, BOLD, size, self.c["lime"])
        x3 = x2 + text_width(dot, BOLD, size)
        self.text(x3, y, b, BOLD, size, color or self.c["white"])
        return x3 + text_width(b, BOLD, size)

    def cta_block(self, headline: str, lines: list[dict]) -> None:
        h_lines = wrap(headline, BOLD, 16, CONTENT_W - 40)
        rows = []
        for ln in lines:
            rows.append((wrap(ln["label"], BOLD, 11, CONTENT_W - 40), wrap(ln.get("line", ""), BODY, 10, CONTENT_W - 40), ln.get("url", "")))
        h = 28 + len(h_lines) * 20 + 10 + sum(len(a) * 14 + len(b) * 13 + 14 + 10 for a, b, _ in rows) + 10
        self.ensure(h + 10)
        top = self.y
        self.rounded_rect(M_L, top - h, CONTENT_W, h, 8, self.c["lime"])
        y = top - 24
        for ln in h_lines:
            self.text(M_L + 20, y - 14, ln, BOLD, 16, self.c["black"])
            y -= 20
        y -= 8
        for a, b, url in rows:
            for ln in a:
                self.text(M_L + 20, y - 10, ln, BOLD, 11, self.c["black"])
                y -= 14
            for ln in b:
                self.text(M_L + 20, y - 9, ln, BODY, 10, self.c["black"])
                y -= 13
            if url:
                self.text(M_L + 20, y - 9, url, MONOB, 8.5, self.c["black"], 0.3)
                y -= 14
            y -= 10
        self.y = top - h - 14

    # --- page builders
    def cover(self, p: dict) -> None:
        self.new_page(running=False)
        self.logo(M_L, PAGE_H - 70, 1.0)
        self.wordmark(M_L + 40, PAGE_H - 66, 12)
        d = p["date"]
        if d:
            dw = text_width(f"{self.S['date']}  {d}", MONO, 7.5, 1.0)
            self.text(PAGE_W - M_R - dw, PAGE_H - 66, f"{self.S['date']}  {d}", MONO, 7.5, self.c["gray_600"], 1.0)
        y = PAGE_H - 170
        self.rect(M_L, y - 1, 5, 5, self.c["lime"])
        self.text(M_L + 10, y, p["eyebrow"], MONOB, 8, self.c["lime"], 1.6)
        y -= 34
        size, lines = fit_lines(p["business"], BOLD, [20, 17, 15], CONTENT_W, 2)
        for ln in lines:
            self.text(M_L, y - size, ln, BOLD, size, self.c["white"])
            y -= size * 1.2
        y -= 48
        self.text(M_L, y, p["north_star_label"] if p.get("north_star_label") else self.S["north_star"], MONOB, 8, self.c["gray_600"], 1.6)
        self.rect(M_L, y - 12, 56, 4, self.c["lime"])
        y -= 44
        size, lines = fit_lines(p["north_star"], BOLD, [30, 27, 24, 22, 20, 18], CONTENT_W, 7)
        for i, ln in enumerate(lines):
            last = i == len(lines) - 1
            if last and ln.endswith("."):
                body = ln[:-1]
                self.text(M_L, y - size, body, BOLD, size, self.c["white"])
                self.text(M_L + text_width(body, BOLD, size), y - size, ".", BOLD, size, self.c["lime"])
            else:
                self.text(M_L, y - size, ln, BOLD, size, self.c["white"])
            y -= size * 1.18
        self.text(M_L, 112, p["generated"], BODY, 9, self.c["gray_400"])
        self.text(M_L, 98, p["privacy"], BODY, 8, self.c["gray_600"])
        self.line(M_L, 84, PAGE_W - M_R, 84, 0.5, self.c["charcoal"])
        self.wordmark(M_L, 66, 10)
        tag = self.S["footer"]
        self.text(PAGE_W - M_R - text_width(tag, MONO, 7, 1.0), 66, tag, MONO, 7, self.c["gray_600"], 1.0)

    def section(self, p: dict) -> None:
        self.new_page()
        self.heading(p["num"], p["title"])
        for b in p["blocks"]:
            t = b["type"]
            if t == "label":
                self.label(b["text"])
            elif t == "subheading":
                self.subheading(b["text"])
            elif t == "paragraph":
                self.paragraph(b["text"])
            elif t == "bullets":
                self.bullets(b["items"], b.get("head"))
            elif t == "cards":
                for it in b["items"]:
                    self.card(it.get("label", ""), it.get("title", ""), it.get("body", ""), bar=b.get("bar", False))
            elif t == "callout":
                self.callout(b.get("label", ""), b["text"])
            elif t == "quote":
                self.quote(b["text"])
            elif t == "scores":
                self.scores(b["items"], b["total"], b["band"])
            elif t == "badges":
                self.badges(b["items"], b["yes"], b["no"])
            elif t == "steps":
                self.steps(b["items"])
            elif t == "kv":
                self.kv(b["items"])
            elif t == "pair":
                self.pair(b["items"])
            elif t == "twocol":
                self.twocol(b["items"])
            elif t == "weeks":
                self.weeks(b["items"])
            elif t == "table":
                self.table(b["head"], b["rows"])
            elif t == "segments":
                self.segments(b["items"], b["picked_label"])

    def closing(self, p: dict) -> None:
        self.new_page()
        self.heading("", p["title"])
        self.paragraph(p["paragraph"], size=11, leading=16, color=self.c["white"])
        self.y -= 10
        self.cta_block(p["headline"], p["lines"])
        self.paragraph(p["privacy"], size=9, leading=13, color=self.c["gray_600"])
        self.ensure(90)
        y0 = self.y - 56
        self.logo(M_L, y0, 1.4)
        self.wordmark(M_L + 52, y0 + 6, 18)
        self.text(M_L, y0 - 18, p["tagline"], MONO, 7.5, self.c["gray_600"], 1.4)
        self.y = y0 - 30

    def footer(self, ops: list[bytes], n: int, total: int) -> None:
        saved = self.ops
        self.ops = ops
        self.wordmark(M_L, 30, 8)
        tag = self.S["footer"]
        self.text((PAGE_W - text_width(tag, MONO, 7, 1.0)) / 2, 30, tag, MONO, 7, self.c["gray_600"], 1.0)
        num = f"{n:02d} / {total:02d}"
        self.text(PAGE_W - M_R - text_width(num, MONO, 7, 1.0), 30, num, MONO, 7, self.c["gray_600"], 1.0)
        self.ops = saved


def render_pdf(model: list[dict], brand: dict, lang: str, business: str, compress: bool = False, only_page: int = 0) -> bytes:
    pdf = Pdf(brand, lang, business)
    for p in model:
        if p["kind"] == "cover":
            pdf.cover(p)
        elif p["kind"] == "closing":
            pdf.closing(p)
        else:
            pdf.section(p)
    total = len(pdf.pages)
    for i, ops in enumerate(pdf.pages[1:], 2):
        pdf.footer(ops, i, total)
    title = f"{STRINGS[lang]['footer']} · {business}"
    pages = pdf.pages if not only_page else pdf.pages[only_page - 1:only_page]
    return build_pdf(pages, {"Title": title, "Author": brand["company"]["name"], "Producer": "icp skill make_pdf.py",
                                 "Lang": STRINGS[lang]["lang_code"]}, compress)


def build_pdf(pages: list[list[bytes]], meta: dict, compress: bool) -> bytes:
    objs: list[bytes] = []

    def add(body: bytes) -> int:
        objs.append(body)
        return len(objs)

    n_fonts = len(FONT_RES)
    catalog = add(b"")  # 1, filled later
    pages_obj = add(b"")  # 2
    font_ids = {}
    for name, res in FONT_RES.items():
        font_ids[res] = add(f"<< /Type /Font /Subtype /Type1 /BaseFont /{name} /Encoding /WinAnsiEncoding >>".encode("ascii"))
    info = add(b"")  # 7
    page_ids = []
    font_dict = " ".join(f"/{res} {oid} 0 R" for res, oid in font_ids.items())
    for ops in pages:
        stream = b"\n".join(ops)
        if compress:
            data = zlib.compress(stream)
            content = add(f"<< /Length {len(data)} /Filter /FlateDecode >>\nstream\n".encode("ascii") + data + b"\nendstream")
        else:
            content = add(f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream")
        page = add((f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                    f"/Resources << /Font << {font_dict} >> >> /Contents {content} 0 R >>").encode("ascii"))
        page_ids.append(page)
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objs[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    objs[catalog - 1] = f"<< /Type /Catalog /Pages {pages_obj} 0 R /Lang ({meta['Lang']}) >>".encode("ascii")
    now = dt.datetime.now().strftime("D:%Y%m%d%H%M%S")
    objs[info - 1] = (b"<< /Title (" + pdf_escape(meta["Title"]) + b") /Author (" + pdf_escape(meta["Author"]) +
                      b") /Producer (" + pdf_escape(meta["Producer"]) + b") /CreationDate (" + now.encode("ascii") + b") >>")
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii") + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode("ascii") + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root {catalog} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode("ascii")
    return bytes(out)


def self_check(data: bytes) -> list[str]:
    errors = []
    if not data.startswith(b"%PDF-1."):
        errors.append("missing PDF header")
    if not data.rstrip().endswith(b"%%EOF"):
        errors.append("missing %%EOF")
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    if not m:
        return errors + ["missing startxref"]
    xref_at = int(m.group(1))
    if data[xref_at:xref_at + 4] != b"xref":
        errors.append("startxref does not point at the xref table")
        return errors
    head = re.match(rb"xref\s+0 (\d+)\s+", data[xref_at:])
    count = int(head.group(1))
    pos = xref_at + head.end()
    for i in range(count):
        entry = data[pos + i * 20: pos + (i + 1) * 20]
        if i == 0:
            continue
        off = int(entry[:10])
        if not re.match(rb"%d 0 obj" % i, data[off:off + 20]):
            errors.append(f"xref entry {i} does not point at object {i}")
    n_pages = len(re.findall(rb"/Type /Page\b(?!s)", data))
    if n_pages < 1:
        errors.append("no pages")
    return errors


# ----------------------------------------------------------------------------- text twins
def render_markdown(model: list[dict], business: str) -> str:
    out: list[str] = []
    for p in model:
        if p["kind"] == "cover":
            out += [f"# {p['eyebrow'].title()}: {p['business']}", "", f"**{p['north_star']}**", "", f"_{p['generated']}_ {p['date']}", ""]
        elif p["kind"] == "closing":
            out += [f"## {p['title']}", "", p["paragraph"], "", f"### {p['headline']}", ""]
            out += [f"- **{ln['label']}**: {ln.get('line', '')} {ln.get('url', '')}".rstrip() for ln in p["lines"]]
            out += ["", f"_{p['privacy']}_", ""]
        else:
            out += [f"## {p['num']} {p['title']}", ""]
            for b in p["blocks"]:
                t = b["type"]
                if t == "label":
                    out += [f"### {b['text'].title()}", ""]
                elif t in ("subheading",):
                    out += [f"**{b['text']}**", ""]
                elif t in ("paragraph", "quote"):
                    out += [("> " if t == "quote" else "") + b["text"], ""]
                elif t == "bullets":
                    if b.get("head"):
                        out.append(f"**{b['head']}**")
                    out += [f"- {x}" for x in b["items"]] + [""]
                elif t == "cards":
                    out += [f"- **{it.get('title', '')}** ({it.get('label', '')}): {it.get('body', '')}" for it in b["items"]] + [""]
                elif t == "callout":
                    out += [f"> **{b.get('label', '')}** {b['text']}".replace("**** ", ""), ""]
                elif t == "scores":
                    out += [f"- {it['name']}: {it['score']}/10" for it in b["items"]] + [f"- Total: {b['total']}/40 ({b['band']})", ""]
                elif t == "badges":
                    out += [f"- {it['name']}: {b['yes'] if it['value'] else b['no']}" for it in b["items"]] + [""]
                elif t == "steps":
                    out += [f"{i}. **{it.get('title', '')}** {it.get('body', '')}".rstrip() for i, it in enumerate(b["items"], 1)] + [""]
                elif t == "kv":
                    out += [f"- {k}: {v}" for k, v in b["items"]] + [""]
                elif t == "pair":
                    out += [f"- **{it['label']}**: {it.get('body', '')}" for it in b["items"]] + [""]
                elif t == "twocol":
                    out += [f"- {x}" for x in b["items"]] + [""]
                elif t == "weeks":
                    for it in b["items"]:
                        out += [f"**{it['title']}**"] + [f"- {a}" for a in it["items"]] + [""]
                elif t == "table":
                    out += [f"| {b['head'][0]} | {b['head'][1]} |", "|---|---|"] + [f"| {a} | {c} |" for a, c in b["rows"]] + [""]
                elif t == "segments":
                    out += [f"- {it['name']}: {it['total']}/40" + (f" ({b['picked_label']})" if it["picked"] else "") for it in b["items"]] + [""]
    return "\n".join(out).rstrip() + "\n"


def render_html(model: list[dict], brand: dict, lang: str, business: str) -> str:
    c = brand["colors"]
    md = render_markdown(model, business)
    body = []
    for line in md.splitlines():
        if line.startswith("# "):
            body.append(f"<h1>{esc_html(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{esc_html(line[3:])}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{esc_html(line[4:])}</h3>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.startswith("- "):
            body.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\. ", line):
            body.append(f"<li class='step'>{inline(line.split('. ', 1)[1])}</li>")
        elif line.startswith("|"):
            if line.startswith("|---"):
                continue
            cells = [x.strip() for x in line.strip("|").split("|")]
            body.append("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in cells) + "</tr>")
        elif line.strip():
            body.append(f"<p>{inline(line)}</p>")
    html_body = "\n".join(body)
    html_body = re.sub(r"((?:<li>.*?</li>\n?)+)", r"<ul>\1</ul>", html_body)
    html_body = re.sub(r"((?:<li class='step'>.*?</li>\n?)+)", r"<ol>\1</ol>", html_body)
    html_body = re.sub(r"((?:<tr>.*?</tr>\n?)+)", r"<table>\1</table>", html_body)
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc_html(STRINGS[lang]['footer'])} · {esc_html(business)}</title>
<link rel="stylesheet" href="{brand['fonts']['google_fonts_css']}">
<style>
:root{{--lime:{c['lime']};--bg:{c['black']};--card:{c['off_black']};--text:{c['white']};--muted:{c['gray_400']};--meta:{c['gray_600']};--line:{c['charcoal']}}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Helvetica,Arial,sans-serif;line-height:1.5}}
main{{max-width:760px;margin:0 auto;padding:48px 16px 96px}}
h1{{font-weight:800;font-size:28px;margin:0 0 8px}} h1+p strong{{display:block;font-size:30px;line-height:1.15;color:var(--text);margin:24px 0}}
h2{{font-weight:800;font-size:22px;margin:56px 0 4px}} h2::after{{content:"";display:block;width:56px;height:4px;background:var(--lime);margin-top:10px}}
h3{{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--meta);margin:28px 0 8px}}
h3::before{{content:"";display:inline-block;width:6px;height:6px;background:var(--lime);margin-right:8px;vertical-align:middle}}
p,li{{color:var(--muted)}} strong{{color:var(--text)}} em{{color:var(--meta);font-style:normal;font-size:13px}}
ul{{padding-left:0;list-style:none}} li{{position:relative;padding-left:18px;margin:6px 0}} li::before{{content:"";position:absolute;left:0;top:9px;width:6px;height:6px;background:var(--lime)}}
ol{{padding-left:28px}} ol li::before{{display:none}} ol li{{padding-left:4px}}
blockquote{{margin:12px 0;padding:10px 16px;border-left:3px solid var(--lime);background:var(--card);color:var(--text)}}
table{{width:100%;border-collapse:collapse;margin:8px 0}} td{{padding:8px 0;border-bottom:1px solid var(--line);color:var(--muted)}} td:first-child{{color:var(--text);font-weight:700;width:42%}}
.wm{{font-weight:800}} .wm b{{color:var(--lime)}} footer{{margin-top:64px;border-top:1px solid var(--line);padding-top:16px;color:var(--meta);font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.1em}}
</style></head><body><main>
<div class="wm">WeMake<b>.</b>Tools</div>
{html_body}
<footer>{esc_html(brand['wordmark']['tagline'])}</footer>
</main></body></html>
"""


def esc_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s: str) -> str:
    s = esc_html(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"_(.+?)_", r"<em>\1</em>", s)
    s = re.sub(r"(https?://\S+)", r'<a href="\1" style="color:var(--lime)">\1</a>', s)
    return s


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Render the ICP North Star PDF from icp.json (standard library only).")
    ap.add_argument("--input", required=True, help="path to icp.json")
    ap.add_argument("--out-dir", default=".", help="folder for the outputs (default: current folder)")
    ap.add_argument("--basename", default="icp", help="output file name without extension (default: icp)")
    ap.add_argument("--md", action="store_true", help="also write a Markdown twin")
    ap.add_argument("--html", action="store_true", help="also write an HTML twin (on-brand fonts via Google Fonts)")
    ap.add_argument("--compress", action="store_true", help="compress the page streams (smaller file, not greppable)")
    ap.add_argument("--validate-only", action="store_true", help="only validate icp.json and report")
    ap.add_argument("--brand", help="override the brand.json path (tests)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--debug-page", type=int, default=0, help=argparse.SUPPRESS)
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"input not found: {src}")
        return 2
    try:
        icp = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"icp.json is not valid JSON: {exc}")
        return 2
    errors = validate_icp(icp)
    if errors:
        print("icp.json failed validation:")
        for e in errors:
            print(f"  - {e}")
        return 2
    if args.validate_only:
        print("icp.json is valid")
        for w in WARNINGS:
            print(f"  warning: {w}")
        return 0
    brand = load_brand(Path(args.brand) if args.brand else None)
    model = build_model(icp, brand)
    business = normalize_text(icp["business"]["name"])
    data = render_pdf(model, brand, icp["lang"], business, compress=args.compress, only_page=args.debug_page)
    problems = self_check(data)
    if problems:
        print("internal error, the PDF did not pass its own check: " + "; ".join(problems))
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{args.basename}.pdf"
    pdf_path.write_bytes(data)
    written = [pdf_path]
    if args.md:
        p = out_dir / f"{args.basename}.md"
        p.write_text(render_markdown(model, business), encoding="utf-8")
        written.append(p)
    if args.html:
        p = out_dir / f"{args.basename}.html"
        p.write_text(render_html(model, brand, icp["lang"], business), encoding="utf-8")
        written.append(p)
    if not args.quiet:
        print(f"North Star: {normalize_text(icp['north_star'])}")
        for p in written:
            print(f"wrote {p} ({p.stat().st_size // 1024} KB)")
        for w in dict.fromkeys(WARNINGS):
            print(f"warning: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
