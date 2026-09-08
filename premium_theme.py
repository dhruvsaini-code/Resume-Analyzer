"""
premium_theme.py
-----------------
Theme injection module for Resume Analyzer (Streamlit).
"""

import streamlit as st

COLOR_MAPS = {
    "Indigo": {"primary": "#5E5CE6", "gradient": "linear-gradient(135deg, #5E5CE6 0%, #0A84FF 100%)", "accent": "rgba(94, 92, 230, 0.10)"},
    "Emerald": {"primary": "#30D158", "gradient": "linear-gradient(135deg, #30D158 0%, #00C7BE 100%)", "accent": "rgba(48, 209, 88, 0.10)"},
    "Rose": {"primary": "#FF375F", "gradient": "linear-gradient(135deg, #FF375F 0%, #FF9F0A 100%)", "accent": "rgba(255, 55, 95, 0.10)"},
    "Amber": {"primary": "#FF9F0A", "gradient": "linear-gradient(135deg, #FF9F0A 0%, #FFD60A 100%)", "accent": "rgba(255, 159, 10, 0.10)"},
}


def get_theme_vars(theme_mode: str, primary_color: str) -> dict:
    """Returns a dict of all the CSS-relevant values your app already uses."""
    palette = COLOR_MAPS.get(primary_color, COLOR_MAPS["Indigo"])

    if theme_mode == "Dark Mode":
        bg_primary = "#000000"
        bg_secondary = "rgba(28, 28, 30, 0.72)"
        text_primary = "#F5F5F7"
        text_secondary = "#98989D"
        border_color = "rgba(255, 255, 255, 0.08)"
        card_shadow = "rgba(0, 0, 0, 0.55)"
    else:
        bg_primary = "#FBFBFD"
        bg_secondary = "rgba(255, 255, 255, 0.78)"
        text_primary = "#1D1D1F"
        text_secondary = "#6E6E73"
        border_color = "rgba(0, 0, 0, 0.06)"
        card_shadow = "rgba(0, 0, 0, 0.08)"

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
}}
</style>
""",
        unsafe_allow_html=True,
    )
