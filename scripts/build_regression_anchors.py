#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "skills/silver-gold-image-pipeline/assets"

SILVER = "#B8BDC5"
SILVER_DARK = "#7A828D"
GOLD = "#C89B2B"
GOLD_LIGHT = "#E4C56A"
LIGHT_BG = "#F4F5F7"
DARK_BG = "#24262B"


def svg_document(body: str, background: str | None = None, title: str = "") -> str:
    bg = f'<rect width="1024" height="1024" fill="{background}"/>' if background else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">\n'
        f"<title>{escape(title)}</title>\n"
        f"{bg}\n{body}\n</svg>\n"
    )


def faceted_core(cx: int = 512, cy: int = 520, scale: float = 1.0, silver: str = SILVER, gold: str = GOLD) -> str:
    def p(points: str, fill: str, stroke: str = "none", sw: int = 0) -> str:
        return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    s = scale
    def pt(x: int, y: int) -> tuple[int, int]:
        return (round(cx + (x - 512) * s), round(cy + (y - 520) * s))
    pts = {
        "a": pt(512, 250), "b": pt(730, 390), "c": pt(670, 690), "d": pt(512, 800),
        "e": pt(354, 690), "f": pt(294, 390), "m": pt(512, 520),
    }
    def ps(*keys: str) -> str:
        return " ".join(f"{pts[k][0]},{pts[k][1]}" for k in keys)
    return "\n".join([
        p(ps("a", "b", "m"), silver),
        p(ps("b", "c", "m"), SILVER_DARK),
        p(ps("c", "d", "m"), "#9AA1AA"),
        p(ps("d", "e", "m"), silver),
        p(ps("e", "f", "m"), "#D2D6DB"),
        p(ps("f", "a", "m"), "#A4AAB2"),
        p(ps("a", "b", "c"), "none", gold, max(8, round(18*s))),
        p(ps("d", "e", "f"), "none", gold, max(8, round(14*s))),
    ])


def accepted_product_light() -> str:
    body = '<ellipse cx="512" cy="790" rx="250" ry="55" fill="#000" opacity="0.16"/>\n' + faceted_core()
    return svg_document(body, LIGHT_BG, "Accepted product-light Silver-Gold QA anchor")


def accepted_showcase_neutral() -> str:
    rim = '<path d="M300 390 L512 245 L728 390" fill="none" stroke="#F4F6F8" stroke-width="10" opacity="0.72"/>'
    shadow = '<ellipse cx="512" cy="800" rx="245" ry="50" fill="#000" opacity="0.42"/>'
    return svg_document(f"{shadow}\n{rim}\n{faceted_core()}", DARK_BG, "Accepted showcase-neutral Silver-Gold QA anchor")


def accepted_transparency() -> str:
    return svg_document(faceted_core(scale=0.88), None, "Accepted transparent Silver-Gold QA anchor")


def accepted_edit() -> str:
    divider = '<line x1="512" y1="120" x2="512" y2="904" stroke="#9AA1AA" stroke-width="4" stroke-dasharray="18 16"/>'
    before = '<rect x="120" y="260" width="280" height="420" rx="42" fill="#B9C0C8"/><circle cx="260" cy="470" r="72" fill="#8A929C"/>'
    after = faceted_core(cx=760, cy=520, scale=0.62)
    labels = '<text x="260" y="760" text-anchor="middle" font-family="Arial" font-size="32" fill="#5D6570">INPUT</text><text x="760" y="760" text-anchor="middle" font-family="Arial" font-size="32" fill="#5D6570">EDIT</text>'
    return svg_document(f"{divider}\n{before}\n{after}\n{labels}", LIGHT_BG, "Accepted edit-preservation QA anchor")


def accepted_people() -> str:
    head = '<circle cx="512" cy="330" r="92" fill="#D6A17D"/>'
    hair = '<path d="M430 322 Q450 205 520 220 Q605 230 602 330 Q548 286 430 322" fill="#3B4149"/>'
    jacket = '<path d="M330 800 L380 470 Q512 410 644 470 L694 800 Z" fill="#AEB5BE"/>'
    lapels = '<path d="M430 470 L512 610 L594 470 L560 800 L464 800 Z" fill="#858D97"/>'
    pin = '<circle cx="603" cy="570" r="20" fill="#C89B2B"/>'
    return svg_document(f"{jacket}\n{lapels}\n{head}\n{hair}\n{pin}", LIGHT_BG, "Accepted people case with non-metal living tissue")


def accepted_text_logo() -> str:
    object_part = faceted_core(cx=330, cy=530, scale=0.62)
    safe = '<rect x="590" y="260" width="320" height="500" rx="28" fill="none" stroke="#A3AAB3" stroke-width="6" stroke-dasharray="22 14"/>'
    label = '<text x="750" y="495" text-anchor="middle" font-family="Arial" font-size="34" fill="#6A727D">TEXT / LOGO</text><text x="750" y="545" text-anchor="middle" font-family="Arial" font-size="24" fill="#8A929C">POST-PROCESS SAFE AREA</text>'
    return svg_document(f"{object_part}\n{safe}\n{label}", LIGHT_BG, "Accepted deterministic text and logo overlay workflow")


def rejected_gold_dominance() -> str:
    return svg_document(faceted_core(silver=GOLD_LIGHT, gold="#FFD75A"), LIGHT_BG, "Rejected gold-dominant anchor")


def rejected_chrome_gloss() -> str:
    defs = '<defs><linearGradient id="chrome" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.24" stop-color="#585F68"/><stop offset="0.5" stop-color="#FFFFFF"/><stop offset="0.75" stop-color="#444B54"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient></defs>'
    body = defs + '<ellipse cx="512" cy="530" rx="280" ry="300" fill="url(#chrome)" stroke="#FFFFFF" stroke-width="18"/><ellipse cx="430" cy="390" rx="80" ry="150" fill="#FFFFFF" opacity="0.86"/><path d="M300 720 Q512 880 724 720" fill="none" stroke="#D6A62D" stroke-width="34"/>'
    return svg_document(body, DARK_BG, "Rejected chrome and glossy anchor")


def rejected_obsidian_drift() -> str:
    body = '<ellipse cx="512" cy="800" rx="250" ry="48" fill="#000" opacity="0.5"/>' + faceted_core(silver="#0B0D10", gold="#D0A129")
    return svg_document(body, "#000000", "Rejected black-gold contamination anchor")


def rejected_noisy_texture() -> str:
    defs = '<defs><pattern id="noise" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" fill="#AEB5BE"/><circle cx="6" cy="8" r="3" fill="#626A74"/><circle cx="24" cy="22" r="4" fill="#E0E3E6"/><path d="M0 28 L28 0" stroke="#7F8791" stroke-width="3"/></pattern></defs>'
    body = defs + '<polygon points="512,210 790,420 680,790 344,790 234,420" fill="url(#noise)" stroke="#C89B2B" stroke-width="20"/>'
    return svg_document(body, LIGHT_BG, "Rejected noisy metallic texture anchor")


def rejected_unreadable_silhouette() -> str:
    tiny = faceted_core(cx=512, cy=520, scale=0.16, silver="#E5E7EA", gold="#D3C39A")
    return svg_document(tiny, "#E8EAED", "Rejected unreadable target-size silhouette anchor")


def ambiguous_weak_rim() -> str:
    body = '<ellipse cx="512" cy="800" rx="250" ry="52" fill="#000" opacity="0.18"/>' + faceted_core()
    return svg_document(body, LIGHT_BG, "Ambiguous weak rim-light anchor")


def ambiguous_borderline_ratio() -> str:
    body = '\n'.join([
        '<polygon points="512,220 790,420 690,790 334,790 234,420" fill="#B8BDC5"/>',
        '<polygon points="512,220 790,420 690,790 512,520" fill="#C89B2B"/>',
        '<polygon points="512,520 690,790 512,850 334,790" fill="#9AA1AA"/>',
        '<path d="M512 220 L790 420 L690 790" fill="none" stroke="#E4C56A" stroke-width="16"/>',
    ])
    return svg_document(body, DARK_BG, "Ambiguous declared 70/30 but visually borderline anchor")


ANCHORS = {
    "examples/accepted/product-light.svg": accepted_product_light,
    "examples/accepted/showcase-neutral.svg": accepted_showcase_neutral,
    "examples/accepted/transparency.svg": accepted_transparency,
    "examples/accepted/edit-preservation.svg": accepted_edit,
    "examples/accepted/people-nonmetal-tissue.svg": accepted_people,
    "examples/accepted/text-logo-postprocess.svg": accepted_text_logo,
    "examples/rejected/gold-dominance.svg": rejected_gold_dominance,
    "examples/rejected/chrome-gloss.svg": rejected_chrome_gloss,
    "examples/rejected/obsidian-drift.svg": rejected_obsidian_drift,
    "examples/rejected/noisy-texture.svg": rejected_noisy_texture,
    "examples/rejected/unreadable-silhouette.svg": rejected_unreadable_silhouette,
    "examples/ambiguous/weak-rim-light.svg": ambiguous_weak_rim,
    "examples/ambiguous/borderline-metal-allocation.svg": ambiguous_borderline_ratio,
}


def build(output_root: Path = ASSET_ROOT) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel, factory in ANCHORS.items():
        target = output_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = factory().encode("utf-8")
        target.write_bytes(data)
        hashes[rel] = hashlib.sha256(data).hexdigest()
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic synthetic Silver-Gold QA anchors.")
    parser.add_argument("--output-root", type=Path, default=ASSET_ROOT)
    args = parser.parse_args()
    hashes = build(args.output_root)
    for path, digest in sorted(hashes.items()):
        print(f"{digest}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
