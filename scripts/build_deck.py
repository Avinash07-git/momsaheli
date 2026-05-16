"""Build the Mom's Saheli pitch deck as a .pptx file.

Run:  python scripts/build_deck.py
Out:  docs/pitch_deck.pptx (5 slides, 16:9, brand-matched)

Brand spec is identical to the product UI: warm amber + cream + ink, with
Georgia (serif) for editorial headlines and Helvetica Neue for body.
Fonts are deliberately chosen for max compatibility across PowerPoint,
Keynote, and Google Slides — no font-embed risk.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

# ── Brand tokens (match frontend/tailwind.config.js exactly) ───────────────
BRAND_500 = RGBColor(0xF5, 0x9E, 0x0B)   # amber
BRAND_600 = RGBColor(0xD9, 0x77, 0x06)
BRAND_700 = RGBColor(0xB4, 0x53, 0x09)   # eyebrow / primary brand
BRAND_100 = RGBColor(0xFE, 0xF3, 0xC7)
BRAND_50  = RGBColor(0xFF, 0xFB, 0xEB)
CREAM     = RGBColor(0xFD, 0xF8, 0xF0)   # canvas
INK_950   = RGBColor(0x09, 0x09, 0x0B)
INK_900   = RGBColor(0x18, 0x18, 0x1B)   # body text
INK_700   = RGBColor(0x3F, 0x3F, 0x46)
INK_500   = RGBColor(0x71, 0x71, 0x7A)
INK_300   = RGBColor(0xD4, 0xD4, 0xD1)
INK_200   = RGBColor(0xE5, 0xE5, 0xE3)
INK_100   = RGBColor(0xF4, 0xF4, 0xF3)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
SUCCESS   = RGBColor(0x15, 0x80, 0x3D)
DANGER    = RGBColor(0xB9, 0x1C, 0x1C)
DANGER_BG = RGBColor(0xFE, 0xE2, 0xE2)
SUCCESS_BG= RGBColor(0xDC, 0xFC, 0xE7)

SERIF = "Georgia"
SANS  = "Helvetica Neue"
MONO  = "Courier New"

# ── Page setup: 16:9 widescreen ───────────────────────────────────────────
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "pitch_deck.pptx"


# ═════════════════════════════════════════════════════════════════════════
# Helpers — keep slide code declarative
# ═════════════════════════════════════════════════════════════════════════
def new_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_slide(prs: Presentation, bg: RGBColor = CREAM):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    bg_rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg_rect.fill.solid()
    bg_rect.fill.fore_color.rgb = bg
    bg_rect.line.fill.background()
    bg_rect.shadow.inherit = False
    return slide


def add_text(
    slide,
    x: float, y: float, w: float, h: float,
    text: str,
    *,
    font: str = SANS,
    size: int = 14,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = INK_900,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    anchor: MSO_ANCHOR = MSO_ANCHOR.TOP,
    spacing: float = 1.15,
    letter_spacing: float | None = None,  # in points
):
    """Add a text box. x/y/w/h in inches."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)

    # Each newline becomes a paragraph so line spacing applies cleanly
    parts = text.split("\n")
    for i, part in enumerate(parts):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = part
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        if letter_spacing is not None:
            # python-pptx doesn't expose char spacing directly; fall back
            # to a manual rPr XML tweak.
            from pptx.oxml.ns import qn
            rPr = r._r.get_or_add_rPr()
            rPr.set("spc", str(int(letter_spacing * 100)))
    return tb


def add_rect(
    slide,
    x: float, y: float, w: float, h: float,
    fill: RGBColor | None,
    line: RGBColor | None = None,
    line_w: float = 0.75,
    radius: float | None = None,
):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius is not None:
        # adjustment value is fraction of the shorter side
        try:
            s.adjustments[0] = max(0.0, min(0.5, radius))
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    return s


def add_accent_bar(slide, x: float, y: float, w: float, h: float = 0.05, color: RGBColor = BRAND_500):
    add_rect(slide, x, y, w, h, fill=color)


def add_eyebrow(slide, x: float, y: float, text: str, color: RGBColor = BRAND_700):
    """The signature small-caps eyebrow used across the product."""
    add_text(slide, x, y, 10, 0.3, text.upper(),
             font=SANS, size=10, bold=True, color=color, letter_spacing=2.0)


def add_footer(slide, idx: int, total: int = 5):
    add_text(slide, 0.6, 7.1, 6, 0.3,
             "🌸  Mom's Saheli  ·  Agent Forge AI Hackathon  ·  May 16 2026",
             font=SANS, size=9, color=INK_500)
    add_text(slide, 12.0, 7.1, 1.0, 0.3,
             f"{idx:02d} / {total:02d}",
             font=MONO, size=9, color=INK_500, align=PP_ALIGN.RIGHT)


# ═════════════════════════════════════════════════════════════════════════
# Slide 1 — TITLE
# ═════════════════════════════════════════════════════════════════════════
def slide_title(prs):
    s = add_slide(prs, bg=CREAM)

    # Decorative warm wash on the right side (faux gradient using two soft rects)
    add_rect(s, 8.5, 0,  4.8, 7.5, fill=BRAND_50)
    add_rect(s, 9.5, 0,  3.8, 7.5, fill=BRAND_100)

    # Floral logomark + eyebrow row
    add_text(s, 0.7, 0.55, 1.0, 1.0, "🌸",
             font=SERIF, size=60, color=BRAND_500, anchor=MSO_ANCHOR.TOP)
    add_eyebrow(s, 1.75, 0.85,
                "Agent Forge AI Hackathon  ·  San Francisco  ·  May 16 2026")

    # Headline (Fraunces-style serif, italic accent on 'finally')
    add_text(s, 0.7, 1.8, 8.8, 2.4,
             "The friend every working mom\ncan ", # split so we can italic-color 'finally'
             font=SERIF, size=54, bold=True, color=INK_950, spacing=1.0)
    # Italic gradient-style accent (PPT can't gradient text natively — use BRAND_700)
    add_text(s, 1.6, 3.0, 7.0, 1.0,
             "finally afford.",
             font=SERIF, size=54, bold=True, italic=True, color=BRAND_700, spacing=1.0)

    # Subhead
    add_text(s, 0.7, 4.6, 8.5, 1.5,
             "A 5-agent AI swarm that delivers $2,000 of consultant value\n"
             "for free — for America's 7 million single moms.",
             font=SANS, size=20, color=INK_700, spacing=1.3)

    # Live-pulse badge equivalent
    add_rect(s, 0.7, 6.05, 0.18, 0.18, fill=SUCCESS, radius=0.5)
    add_text(s, 0.95, 5.97, 7, 0.3,
             "LIVE DEMO  ·  REAL GEMINI  ·  REAL CITED .GOV LAW  ·  REAL LAUNCH PAGES",
             font=SANS, size=10, bold=True, color=INK_700, letter_spacing=1.5)

    # Author block (right wash area)
    add_text(s, 9.0, 5.4, 4.0, 0.35,
             "BUILT IN 24 HOURS  ·  SOLO",
             font=SANS, size=10, bold=True, color=BRAND_700, letter_spacing=2.0)
    add_text(s, 9.0, 5.85, 4.0, 0.5,
             "Avinash Ahuja",
             font=SERIF, size=22, bold=True, color=INK_900)
    add_text(s, 9.0, 6.4, 4.0, 0.4,
             "github.com/Avinash07-git/momsaheli",
             font=MONO, size=10, color=INK_500)

    add_footer(s, 1)


# ═════════════════════════════════════════════════════════════════════════
# Slide 2 — THE PROBLEM
# ═════════════════════════════════════════════════════════════════════════
def slide_problem(prs):
    s = add_slide(prs, bg=WHITE)

    add_eyebrow(s, 0.7, 0.6, "The world's pain")

    add_text(s, 0.7, 1.05, 11.5, 1.6,
             "She's not short on effort.",
             font=SERIF, size=46, bold=True, color=INK_950, spacing=1.0)
    add_text(s, 0.7, 1.95, 11.5, 1.6,
             "She's short on margin.",
             font=SERIF, size=46, bold=True, italic=True, color=BRAND_700, spacing=1.0)

    # 4 stat cards in a row (2.7" wide each)
    stats = [
        ("7.3M",  "single moms in\nAmerica",                 "Center for American Progress"),
        ("75%",   "already working —\nmost full-time",       "CAP"),
        ("$40K",  "median income,\nworking single mom",      "CAP"),
        ("35%",   "of that income eaten\nby childcare",       "Child Care Aware"),
    ]
    card_w, card_h = 2.85, 2.2
    gap = 0.15
    start_x = 0.7
    y = 3.95
    for i, (num, label, src) in enumerate(stats):
        x = start_x + i * (card_w + gap)
        # Card surface
        add_rect(s, x, y, card_w, card_h, fill=CREAM, line=INK_100, radius=0.05)
        # Big number
        add_text(s, x + 0.25, y + 0.25, card_w - 0.5, 1.0, num,
                 font=SERIF, size=44, bold=True, color=BRAND_700, spacing=0.95)
        # Label
        add_text(s, x + 0.25, y + 1.15, card_w - 0.5, 0.7, label,
                 font=SANS, size=12, color=INK_900, spacing=1.2)
        # Source eyebrow
        add_text(s, x + 0.25, y + card_h - 0.4, card_w - 0.5, 0.25,
                 f"SOURCE: {src}".upper(),
                 font=SANS, size=8, bold=True, color=INK_500, letter_spacing=1.5)

    # Brutal arithmetic closer
    add_rect(s, 0.7, 6.45, 11.95, 0.5, fill=INK_950, radius=0.15)
    add_text(s, 0.9, 6.49, 11.6, 0.45,
             "What she needs:  consultant $2,000  ·  lawyer $200/hr  ·  marketer $200/hr  ·  bookkeeper $200/hr        "
             "What she can afford:  $0",
             font=SANS, size=11, bold=True, color=CREAM,
             anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)

    add_footer(s, 2)


# ═════════════════════════════════════════════════════════════════════════
# Slide 3 — THE PRODUCT (5 agents + shock moment)
# ═════════════════════════════════════════════════════════════════════════
def slide_product(prs):
    s = add_slide(prs, bg=CREAM)

    add_eyebrow(s, 0.7, 0.6, "Our solution  ·  Mom's Saheli")

    add_text(s, 0.7, 1.05, 11.5, 1.4,
             "5 specialist AI agents do the\n$2,000-of-consultant work — free.",
             font=SERIF, size=36, bold=True, color=INK_950, spacing=1.05)

    # 5 agents as a row of pill-style nodes (LEFT 8")
    agents = [
        ("1", "Profile",              "Normalize skills,\nhours, constraints"),
        ("2", "Market Scout",         "Rank 6–10 paths by\nrealistic net $/mo"),
        ("3", "Reality & Compliance", "Block illegal options\nwith cited state law"),
        ("4", "Launch",               "Offer + 7-day plan +\nreal published page"),
        ("5", "Memory",               "Persist + surface\ncross-user pattern"),
    ]
    agent_y = 3.4
    agent_w = 1.55
    gap = 0.05
    start_x = 0.7
    # Connector line
    add_rect(s, start_x + 0.4, agent_y + 0.5, (agent_w + gap) * len(agents) - 0.7, 0.03,
             fill=BRAND_500)
    for i, (n, name, desc) in enumerate(agents):
        x = start_x + i * (agent_w + gap)
        # Numbered circle (the journey node)
        add_rect(s, x + 0.3, agent_y, 0.8, 0.8, fill=WHITE, line=BRAND_500, line_w=1.5, radius=0.5)
        add_text(s, x + 0.3, agent_y + 0.05, 0.8, 0.7, n,
                 font=SERIF, size=28, bold=True, color=BRAND_700,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # Name
        add_text(s, x, agent_y + 0.95, agent_w + 0.2, 0.4, name,
                 font=SANS, size=11, bold=True, color=INK_900, align=PP_ALIGN.CENTER)
        # Desc
        add_text(s, x, agent_y + 1.35, agent_w + 0.2, 0.8, desc,
                 font=SANS, size=9, color=INK_500, align=PP_ALIGN.CENTER, spacing=1.2)

    # Tag line under the agent row
    add_text(s, 0.7, 5.6, 12, 0.4,
             "Real Gemini 2.5 Flash  ·  Real Tavily SERP  ·  Real Bright Data  ·  Real Actionbook browser  ·  Real published .com page",
             font=SANS, size=11, italic=True, color=INK_500, align=PP_ALIGN.CENTER)

    # SHOCK MOMENT card (right-aligned dramatic block)
    block_x, block_y, block_w, block_h = 0.7, 6.15, 11.95, 0.85
    add_rect(s, block_x, block_y, block_w, block_h, fill=DANGER_BG, line=DANGER, line_w=1.0, radius=0.1)
    # Left accent rail
    add_rect(s, block_x, block_y, 0.08, block_h, fill=DANGER)
    add_text(s, block_x + 0.25, block_y + 0.1, 5.5, 0.3,
             "🛑  THE DEMO MOMENT  ·  COMPLIANCE BLOCK",
             font=SANS, size=10, bold=True, color=DANGER, letter_spacing=1.5)
    add_text(s, block_x + 0.25, block_y + 0.4, block_w - 0.4, 0.45,
             "Jenny's #1 ranked offer gets BLOCKED. Cited live: California Health & Safety Code §114365 — "
             "“Direct sale of home-prepared meals requires a Cottage Food Operator permit.” Source: cdph.ca.gov",
             font=SERIF, size=11, italic=True, color=INK_900, spacing=1.25)

    add_footer(s, 3)


# ═════════════════════════════════════════════════════════════════════════
# Slide 4 — THE PROOF (Jenny vs Jessica)
# ═════════════════════════════════════════════════════════════════════════
def slide_proof(prs):
    s = add_slide(prs, bg=WHITE)

    add_eyebrow(s, 0.7, 0.6, "Proof  ·  nothing is hardcoded")

    add_text(s, 0.7, 1.05, 12, 1.4,
             "Two moms. Same engine.\nCompletely different output.",
             font=SERIF, size=36, bold=True, color=INK_950, spacing=1.05)

    # Two persona cards side-by-side
    card_y = 3.2
    card_h = 3.45
    gap = 0.3
    card_w = (12.6 - gap) / 2  # 6.15 each
    jenny_x = 0.7
    jess_x = jenny_x + card_w + gap

    def persona_card(x, emoji, name, sub, color_accent, steps):
        # Card
        add_rect(s, x, card_y, card_w, card_h, fill=CREAM, line=INK_200, radius=0.04)
        # Header strip
        add_rect(s, x, card_y, card_w, 0.85, fill=color_accent, radius=0.04)
        add_text(s, x + 0.25, card_y + 0.18, 1.0, 0.5, emoji,
                 font=SERIF, size=28, color=WHITE)
        add_text(s, x + 1.1, card_y + 0.18, card_w - 1.2, 0.35, name,
                 font=SERIF, size=20, bold=True, color=WHITE)
        add_text(s, x + 1.1, card_y + 0.50, card_w - 1.2, 0.3, sub,
                 font=SANS, size=10, color=WHITE)
        # Steps
        step_y = card_y + 1.05
        for i, (icon, text) in enumerate(steps):
            add_text(s, x + 0.3, step_y + i * 0.45, 0.3, 0.4, icon,
                     font=SANS, size=12, color=INK_900)
            add_text(s, x + 0.65, step_y + i * 0.45, card_w - 0.85, 0.4, text,
                     font=SANS, size=10.5, color=INK_700, spacing=1.2)

    persona_card(
        jenny_x, "👩🏽‍🍳", "Jenny",
        "Daycare aide  ·  California  ·  $600/mo gap  ·  5 hr/wk",
        BRAND_700,
        [
            ("→", "Top opp: weekend tiffin / meal-pack subscription"),
            ("⚖", "BLOCKED: CA Health & Safety §114365 (cottage food)"),
            ("↩", "Pivots to a legal #2: home-cooked freezer kits at the farmers' market"),
            ("🚀", "Real launch page published at /launch/jenny-…"),
            ("✓", "Net $/mo projection: $620 — closes the gap"),
        ],
    )
    persona_card(
        jess_x, "💻", "Jessica",
        "Customer-service rep (WFH)  ·  Texas  ·  $400/mo gap  ·  3 hr/wk  ·  digital-only",
        INK_900,
        [
            ("→", "Top opp: Etsy printable kids' lunchbox planner pack"),
            ("✓", "Zero compliance hits — digital, async, no permits"),
            ("✓", "Constraint math passes (3 hr/wk feasible)"),
            ("🚀", "Real Etsy listing draft + launch page published"),
            ("✓", "Net $/mo projection: $430 — closes the gap"),
        ],
    )

    # Footer caption
    add_text(s, 0.7, 6.8, 12, 0.3,
             "Same swarm. Different regulation. Different math. Different launch — it's the system doing the work, not a script.",
             font=SANS, size=11, italic=True, color=INK_500, align=PP_ALIGN.CENTER)

    add_footer(s, 4)


# ═════════════════════════════════════════════════════════════════════════
# Slide 5 — THE ASK
# ═════════════════════════════════════════════════════════════════════════
def slide_ask(prs):
    s = add_slide(prs, bg=INK_950)

    # Decorative warm wash (top-right)
    add_rect(s, 8.5, 0,  4.8, 7.5, fill=INK_900)
    add_rect(s, 11.5, 0, 1.83, 7.5, fill=BRAND_700)

    add_eyebrow(s, 0.7, 0.7, "The ask", color=BRAND_500)

    add_text(s, 0.7, 1.15, 11.5, 1.6,
             "Pick us.",
             font=SERIF, size=84, bold=True, color=CREAM, spacing=1.0)

    add_text(s, 0.7, 3.0, 11.5, 1.2,
             "We're not shipping AI features.\nWe're closing the margin gap.",
             font=SERIF, size=28, italic=True, color=BRAND_500, spacing=1.15)

    # Sponsor strip — 9 names in a wide rounded chip
    sponsors = [
        "AgentField", "Bright Data", "Actionbook", "Evermind", "Butterbase",
        "Qwen Cloud", "Z.ai", "TokenRouter", "Zeabur",
    ]
    add_text(s, 0.7, 4.6, 11.5, 0.3, "BUILT ON THE AGENT FORGE STACK · EVERY TOOL LOAD-BEARING",
             font=SANS, size=10, bold=True, color=INK_500, letter_spacing=2.0)
    add_rect(s, 0.7, 4.95, 11.95, 0.6, fill=INK_900, line=INK_700, radius=0.15)
    add_text(s, 0.7, 5.05, 11.95, 0.45,
             "  ·  ".join(sponsors),
             font=SANS, size=11, bold=True, color=CREAM,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # CTA card
    add_rect(s, 0.7, 6.0, 6.0, 0.95, fill=BRAND_500, radius=0.1)
    add_text(s, 0.9, 6.10, 5.7, 0.35,
             "TRY IT NOW",
             font=SANS, size=10, bold=True, color=INK_950, letter_spacing=2.0)
    add_text(s, 0.9, 6.42, 5.7, 0.45,
             "github.com/Avinash07-git/momsaheli",
             font=MONO, size=14, bold=True, color=INK_950)

    # Thank-you logomark right
    add_text(s, 11.4, 6.0, 1.5, 1.0, "🌸",
             font=SERIF, size=60, color=BRAND_500, align=PP_ALIGN.CENTER)

    # Footer — dark version
    add_text(s, 0.6, 7.1, 12.0, 0.3,
             "🐶 Built with love for every mom doing the math at 11pm.",
             font=SANS, size=10, italic=True, color=INK_500)
    add_text(s, 12.0, 7.1, 1.0, 0.3,
             "05 / 05",
             font=MONO, size=9, color=INK_500, align=PP_ALIGN.RIGHT)


# ═════════════════════════════════════════════════════════════════════════
def main():
    prs = new_deck()
    slide_title(prs)
    slide_problem(prs)
    slide_product(prs)
    slide_proof(prs)
    slide_ask(prs)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT_PATH)
    print(f"✅ Saved {OUT_PATH}")
    print(f"   {OUT_PATH.stat().st_size / 1024:.1f} KB · {len(prs.slides)} slides · 16:9")


if __name__ == "__main__":
    main()
