"""
premium_theme.py
-----------------
Editorial Audit theme for Resume Analyzer (Streamlit).

Concept: "Editorial Audit" — the app reads like a reviewer's marked-up
report rather than a generic AI SaaS dashboard. Flat index cards, hairline
top rules, a serif headline face (Source Serif 4), sans-serif body (IBM Plex Sans),
monospace for real data strings (IBM Plex Mono).
"""

import streamlit as st

# --- Theme Colors: four "pen" colors an editor might grade with ---
COLOR_MAPS = {
    "Ink Blue":     {"primary": "#2C3E63", "gradient": "#2C3E63", "accent": "rgba(44, 62, 99, 0.10)"},
    "Editor Red":   {"primary": "#A6303D", "gradient": "#A6303D", "accent": "rgba(166, 48, 61, 0.10)"},
    "Ledger Green": {"primary": "#2F6B4F", "gradient": "#2F6B4F", "accent": "rgba(47, 107, 79, 0.10)"},
    "Graphite":     {"primary": "#3B3B3B", "gradient": "#3B3B3B", "accent": "rgba(59, 59, 59, 0.10)"},
    # Backwards compatibility fallbacks
    "Indigo":       {"primary": "#2C3E63", "gradient": "#2C3E63", "accent": "rgba(44, 62, 99, 0.10)"},
    "Emerald":      {"primary": "#2F6B4F", "gradient": "#2F6B4F", "accent": "rgba(47, 107, 79, 0.10)"},
    "Rose":         {"primary": "#A6303D", "gradient": "#A6303D", "accent": "rgba(166, 48, 61, 0.10)"},
    "Amber":        {"primary": "#3B3B3B", "gradient": "#3B3B3B", "accent": "rgba(59, 59, 59, 0.10)"},
}


def get_theme_vars(theme_mode: str, primary_color: str) -> dict:
    """Returns a dict of all the CSS-relevant values your app already uses."""
    palette = COLOR_MAPS.get(primary_color, COLOR_MAPS["Ink Blue"])

    if theme_mode == "Dark Mode":
        bg_primary = "#12151C"
        bg_secondary = "#171B24"
        text_primary = "#E7E5DD"
        text_secondary = "#9CA1AC"
        border_color = "rgba(255, 255, 255, 0.10)"
        card_shadow = "rgba(0, 0, 0, 0.35)"
    else:
        bg_primary = "#EEF0EA"
        bg_secondary = "#FFFFFF"
        text_primary = "#1B1F27"
        text_secondary = "#5B6272"
        border_color = "rgba(0, 0, 0, 0.12)"
        card_shadow = "rgba(0, 0, 0, 0.05)"

    return {
        "primary": palette["primary"],
        "gradient": palette["gradient"],
        "accent": palette["accent"],
        "bg_primary": bg_primary,
        "bg_secondary": bg_secondary,
        "text_primary": text_primary,
        "text_secondary": text_secondary,
        "border_color": border_color,
        "card_shadow": card_shadow,
    }


def inject_theme(t: dict) -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..700&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* Base */
html, body, [class*="css"], .stApp {{
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
    -webkit-font-smoothing: antialiased;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 600;
    letter-spacing: -0.01em;
}}

p, span, div, label {{ letter-spacing: -0.005em; }}

/* Numbers and short data strings only — not decorative */
.kpi-value, code {{
    font-family: 'IBM Plex Mono', monospace;
}}

/* Headline: solid serif, no gradient clip, thin rule underneath
   stands in for decoration instead of glow/color */
.title-gradient {{
    color: {t['text_primary']} !important;
    background: none !important;
    -webkit-background-clip: initial !important;
    -webkit-text-fill-color: initial !important;
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 2.75rem;
    margin-bottom: 0.4rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid {t['primary']};
    display: inline-block;
}}

.subtitle-saas {{
    color: {t['text_secondary']};
    font-size: 1.05rem;
    margin-bottom: 2rem;
    font-weight: 400;
    line-height: 1.6;
    max-width: 640px;
}}

/* Cards: flat index-card treatment. No shadow bloom, no lift-on-hover,
   no gradient wash. A single hairline top rule signals "reviewed". */
.glass-card {{
    background: {t['bg_secondary']};
    border-radius: 6px;
    border: 1px solid {t['border_color']};
    border-top: 3px solid {t['primary']};
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px 0 {t['card_shadow']};
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    transition: border-color 0.15s ease;
    animation: none;
}}
.glass-card::before {{
    display: none;
}}
.glass-card:hover {{
    border-color: {t['primary']};
    transform: none;
    box-shadow: 0 1px 3px 0 {t['card_shadow']};
}}

/* KPI labels: sentence case, not tracked-out caps */
.kpi-title {{
    font-size: 0.8rem;
    color: {t['text_secondary']};
    font-weight: 600;
    margin-bottom: 0.4rem;
    text-transform: none;
    letter-spacing: normal;
}}
.kpi-value {{
    font-size: 2rem;
    font-weight: 600;
    color: {t['text_primary']};
    line-height: 1.15;
}}
.kpi-sub {{
    font-size: 0.82rem;
    color: {t['primary']};
    margin-top: 0.35rem;
    font-weight: 500;
}}

/* Badges: flat stamp-like tags, sentence case */
.saas-badge {{
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: none;
    display: inline-block;
    border: 1px solid transparent;
}}
.badge-high     {{ background-color: rgba(166, 48, 61, 0.12); color: #A6303D; border-color: rgba(166, 48, 61, 0.3); }}
.badge-medium   {{ background-color: rgba(180, 128, 30, 0.14); color: #8A6412; border-color: rgba(180, 128, 30, 0.3); }}
.badge-low      {{ background-color: rgba(44, 62, 99, 0.12); color: #2C3E63; border-color: rgba(44, 62, 99, 0.3); }}
.badge-success  {{ background-color: rgba(47, 107, 79, 0.14); color: #2F6B4F; border-color: rgba(47, 107, 79, 0.3); }}

/* Buttons: quiet, one clean state change */
div.stButton > button {{
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.45rem 1.1rem;
    border: 1px solid {t['border_color']};
    background: {t['bg_secondary']};
    color: {t['text_primary']};
    transition: border-color 0.15s ease, color 0.15s ease;
}}
div.stButton > button:hover {{
    border-color: {t['primary']};
    color: {t['primary']};
    transform: none;
    box-shadow: none;
}}

/* File uploader: plain dashed rule, no glow */
div[data-testid="stFileUploader"] {{
    background: {t['bg_secondary']};
    border: 1px dashed {t['border_color']};
    border-radius: 6px;
    padding: 1.5rem;
}}
div[data-testid="stFileUploader"]:hover {{
    border-color: {t['primary']};
    box-shadow: none;
}}

/* Tabs */
button[data-baseweb="tab"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
}}

/* Sidebar: plain panel, hairline divider, no shadow */
section[data-testid="stSidebar"] {{
    background: {t['bg_secondary']};
    border-right: 1px solid {t['border_color']};
    backdrop-filter: none;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: {t['border_color']};
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {t['primary']}; }}

/* Single load-in for the page's main content only — not per card */
.stApp {{
    animation: settleIn 0.35s ease-out;
}}
@keyframes settleIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}

@keyframes shimmer {{
    0%   {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
}}
.shimmer-loading {{
    background: linear-gradient(90deg, {t['border_color']} 25%, {t['primary']} 50%, {t['border_color']} 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    height: 16px;
    margin-bottom: 8px;
}}

/* Divider */
hr {{ border-color: {t['border_color']} !important; }}
</style>
""",
        unsafe_allow_html=True,
    )
