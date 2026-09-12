import streamlit as st
import datetime
import requests
from collections import defaultdict
from plotly import graph_objects as go

OWM_BASE = "https://api.openweathermap.org"

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Weather Forecast | Hafiz Muhammad Ubaid",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS & STYLING ----------------
def apply_custom_styles(bg_url, overlay=None):
    overlay_start, overlay_end = overlay if overlay else ("rgba(6, 10, 20, 0.92)", "rgba(8, 13, 26, 0.96)")
    css_lines = [
        "<style>",
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800&display=swap');",
        "@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');",

        # ---------- GLOBAL BACKDROP ----------
        ".stApp {",
        "    background: linear-gradient(160deg, " + overlay_start + ", " + overlay_end + "), url('" + bg_url + "') !important;",
        "    background-attachment: fixed !important;",
        "    background-size: cover !important;",
        "    background-position: center !important;",
        "    transition: background 0.7s ease-in-out;",
        "    font-family: 'Inter', sans-serif;",
        "}",

        "#MainMenu, footer {visibility: hidden;}",
        "header[data-testid='stHeader'] {",
        "    background: transparent !important;",
        "    box-shadow: none !important;",
        "}",

        # ---------- SIDEBAR TOGGLE / COLLAPSE CONTROL ----------
        "[data-testid='stSidebarCollapsedControl'], button[data-testid='collapsedControl'] {",
        "    background: rgba(14, 165, 233, 0.18) !important;",
        "    border: 1px solid rgba(56, 189, 248, 0.45) !important;",
        "    border-radius: 10px !important;",
        "    box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35) !important;",
        "    padding: 4px !important;",
        "}",
        "[data-testid='stSidebarCollapsedControl'] svg, button[data-testid='collapsedControl'] svg {",
        "    fill: #38BDF8 !important;",
        "}",
        "[data-testid='stSidebarCollapsedControl']:hover, button[data-testid='collapsedControl']:hover {",
        "    background: rgba(14, 165, 233, 0.32) !important;",
        "    transform: scale(1.05);",
        "}",
        "[data-testid='stSidebarCollapseButton'] svg, [data-testid='baseButton-headerNoPadding'] svg {",
        "    fill: #38BDF8 !important;",
        "}",

        "h1, h2, h3, h4, h5, h6 {",
        "    font-family: 'Poppins', sans-serif !important;",
        "    color: #F8FAFC !important;",
        "    letter-spacing: 0.3px;",
        "}",
        "p, label, span, div {",
        "    color: #CBD5E1 !important;",
        "}",

        # ---------- HERO TITLE ----------
        ".hero-title {",
        "    font-family: 'Poppins', sans-serif;",
        "    font-weight: 800;",
        "    font-size: 2.6rem;",
        "    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 60%, #C084FC 100%);",
        "    -webkit-background-clip: text;",
        "    -webkit-text-fill-color: transparent;",
        "    background-clip: text;",
        "    margin-bottom: 0px;",
        "    letter-spacing: -0.5px;",
        "}",
        ".hero-subtitle {",
        "    color: #64748B !important;",
        "    font-size: 0.95rem;",
        "    font-weight: 400;",
        "    margin-top: 4px;",
        "    margin-bottom: 28px;",
        "    letter-spacing: 0.5px;",
        "    text-transform: uppercase;",
        "}",

        # ---------- GLASSMORPHIC CARD ----------
        ".glass-card {",
        "    background: linear-gradient(145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.02));",
        "    backdrop-filter: blur(24px) saturate(160%);",
        "    -webkit-backdrop-filter: blur(24px) saturate(160%);",
        "    border: 1px solid rgba(255, 255, 255, 0.10);",
        "    border-radius: 22px;",
        "    padding: 32px;",
        "    margin-bottom: 26px;",
        "    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45), inset 0 1px 0 0 rgba(255,255,255,0.06);",
        "    transition: transform 0.35s cubic-bezier(.2,.8,.2,1), border-color 0.35s ease, box-shadow 0.35s ease;",
        "}",
        ".glass-card:hover {",
        "    border-color: rgba(56, 189, 248, 0.35);",
        "    box-shadow: 0 14px 40px 0 rgba(0,0,0,0.5), 0 0 0 1px rgba(56,189,248,0.08);",
        "}",

        # ---------- FORM / INPUT CONTAINER ----------
        "div[data-testid='stForm'] {",
        "    background: linear-gradient(145deg, rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.45)) !important;",
        "    backdrop-filter: blur(18px);",
        "    border: 1px solid rgba(255, 255, 255, 0.10) !important;",
        "    border-radius: 20px !important;",
        "    padding: 26px !important;",
        "    box-shadow: 0 6px 24px rgba(0,0,0,0.35);",
        "}",

        # ---------- INPUT / SELECT FIELDS ----------
        "div[data-baseweb='select'] > div, .stTextInput input {",
        "    background: rgba(255,255,255,0.045) !important;",
        "    border: 1px solid rgba(255,255,255,0.12) !important;",
        "    border-radius: 12px !important;",
        "    color: #F1F5F9 !important;",
        "    transition: border-color 0.25s ease, box-shadow 0.25s ease;",
        "}",
        ".stTextInput input:focus {",
        "    border-color: rgba(56, 189, 248, 0.55) !important;",
        "    box-shadow: 0 0 0 3px rgba(56, 189, 233, 0.12) !important;",
        "}",
        "label[data-testid='stWidgetLabel'] p {",
        "    font-size: 0.72rem !important;",
        "    font-weight: 600 !important;",
        "    letter-spacing: 1px !important;",
        "    text-transform: uppercase;",
        "    color: #64748B !important;",
        "}",

        # ---------- BUTTONS ----------
        ".stButton > button, .stFormSubmitButton > button {",
        "    width: 100%;",
        "    background: linear-gradient(135deg, #0EA5E9 0%, #4F46E5 100%);",
        "    color: #FFFFFF !important;",
        "    font-family: 'Poppins', sans-serif;",
        "    font-weight: 600;",
        "    font-size: 0.92rem;",
        "    letter-spacing: 0.4px;",
        "    border: none;",
        "    border-radius: 12px;",
        "    padding: 0.8rem 1rem;",
        "    transition: all 0.3s cubic-bezier(.2,.8,.2,1);",
        "    box-shadow: 0 4px 22px rgba(14, 165, 233, 0.35);",
        "}",
        ".stButton > button:hover, .stFormSubmitButton > button:hover {",
        "    background: linear-gradient(135deg, #38BDF8 0%, #6366F1 100%);",
        "    transform: translateY(-2px);",
        "    box-shadow: 0 8px 28px rgba(14, 165, 233, 0.55);",
        "}",
        ".stButton > button:active, .stFormSubmitButton > button:active {",
        "    transform: translateY(0px);",
        "}",

        # ---------- BADGES ----------
        ".badge {",
        "    display: inline-block;",
        "    padding: 9px 18px;",
        "    border-radius: 30px;",
        "    font-size: 0.82rem;",
        "    font-weight: 500;",
        "    background: rgba(56, 189, 248, 0.08);",
        "    color: #7DD3FC !important;",
        "    border: 1px solid rgba(56, 189, 248, 0.22);",
        "    margin-right: 10px;",
        "    margin-bottom: 10px;",
        "    letter-spacing: 0.2px;",
        "}",

        # ---------- SOCIAL / CONTACT ICONS ----------
        ".social-icon-btn {",
        "    display: inline-flex;",
        "    align-items: center;",
        "    justify-content: center;",
        "    width: 56px;",
        "    height: 56px;",
        "    border-radius: 50%;",
        "    font-size: 1.5rem;",
        "    text-decoration: none !important;",
        "    color: #FFFFFF !important;",
        "    transition: all 0.3s cubic-bezier(.2,.8,.2,1);",
        "    margin-right: 16px;",
        "    margin-top: 8px;",
        "    border: 1px solid rgba(255,255,255,0.12);",
        "}",
        ".icon-email {",
        "    background: linear-gradient(135deg, #EA4335 0%, #C5221F 100%);",
        "    box-shadow: 0 4px 18px rgba(234, 67, 53, 0.30);",
        "}",
        ".icon-email:hover {",
        "    transform: translateY(-4px) scale(1.08);",
        "    box-shadow: 0 10px 26px rgba(234, 67, 53, 0.55);",
        "}",
        ".icon-insta {",
        "    background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);",
        "    box-shadow: 0 4px 18px rgba(220, 39, 67, 0.30);",
        "}",
        ".icon-insta:hover {",
        "    transform: translateY(-4px) scale(1.08);",
        "    box-shadow: 0 10px 26px rgba(220, 39, 67, 0.55);",
        "}",
        ".icon-linkedin {",
        "    background: #0A66C2;",
        "    box-shadow: 0 4px 18px rgba(10, 102, 194, 0.30);",
        "}",
        ".icon-linkedin:hover {",
        "    transform: translateY(-4px) scale(1.08);",
        "    box-shadow: 0 10px 26px rgba(10, 102, 194, 0.55);",
        "}",

        # ---------- SIDEBAR ----------
        "section[data-testid='stSidebar'] {",
        "    background: linear-gradient(180deg, rgba(8, 12, 24, 0.96), rgba(6, 9, 18, 0.98)) !important;",
        "    border-right: 1px solid rgba(255, 255, 255, 0.07);",
        "}",
        "section[data-testid='stSidebar'] .block-container {",
        "    padding-top: 1.5rem;",
        "}",

        # Brand block in sidebar
        ".brand-block {",
        "    text-align: left;",
        "    padding: 4px 6px 26px 6px;",
        "    border-bottom: 1px solid rgba(255,255,255,0.08);",
        "    margin-bottom: 22px;",
        "}",
        ".brand-mark {",
        "    display: inline-flex;",
        "    align-items: center;",
        "    justify-content: center;",
        "    width: 42px;",
        "    height: 42px;",
        "    border-radius: 12px;",
        "    background: linear-gradient(135deg, #0EA5E9, #6366F1);",
        "    font-size: 1.2rem;",
        "    color: #fff !important;",
        "    margin-bottom: 12px;",
        "    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.4);",
        "}",
        ".brand-title {",
        "    font-family: 'Poppins', sans-serif;",
        "    font-weight: 700;",
        "    font-size: 1.05rem;",
        "    color: #F8FAFC !important;",
        "    margin: 0;",
        "    letter-spacing: 0.2px;",
        "}",
        ".brand-subtitle {",
        "    font-size: 0.72rem;",
        "    color: #475569 !important;",
        "    margin-top: 2px;",
        "    letter-spacing: 0.4px;",
        "    text-transform: uppercase;",
        "}",
        ".nav-caption {",
        "    font-size: 0.68rem;",
        "    font-weight: 600;",
        "    letter-spacing: 1.6px;",
        "    text-transform: uppercase;",
        "    color: #334155 !important;",
        "    margin: 4px 0 10px 6px;",
        "}",

        # Radio-based nav styled as premium pill list
        "section[data-testid='stSidebar'] div[role='radiogroup'] {",
        "    gap: 6px;",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label {",
        "    background: transparent;",
        "    border: 1px solid transparent;",
        "    border-radius: 12px;",
        "    padding: 11px 14px !important;",
        "    transition: all 0.25s ease;",
        "    width: 100%;",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label:hover {",
        "    background: rgba(255,255,255,0.04);",
        "    border-color: rgba(255,255,255,0.08);",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label p {",
        "    font-family: 'Inter', sans-serif !important;",
        "    font-weight: 500 !important;",
        "    font-size: 0.9rem !important;",
        "    color: #94A3B8 !important;",
        "    letter-spacing: 0.2px;",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label[data-checked='true'] {",
        "    background: linear-gradient(135deg, rgba(14,165,233,0.16), rgba(99,102,241,0.14));",
        "    border-color: rgba(56, 189, 248, 0.35);",
        "    box-shadow: inset 0 0 0 1px rgba(56,189,248,0.15);",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label[data-checked='true'] p {",
        "    color: #F8FAFC !important;",
        "    font-weight: 600 !important;",
        "}",

        # ---------- TABS ----------
        "button[data-baseweb='tab'] {",
        "    font-family: 'Inter', sans-serif;",
        "    font-weight: 500;",
        "    color: #64748B !important;",
        "}",
        "button[data-baseweb='tab'][aria-selected='true'] {",
        "    color: #38BDF8 !important;",
        "}",

        # ---------- DIVIDER ----------
        "hr {",
        "    border-color: rgba(255,255,255,0.08) !important;",
        "}",

        "</style>"
    ]
    st.markdown("\n".join(css_lines), unsafe_allow_html=True)

# ---------------- DYNAMIC WEATHER BACKGROUND ----------------
DEFAULT_BG_IMAGE = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1920&q=80"
DEFAULT_OVERLAY = ("rgba(6, 10, 20, 0.92)", "rgba(8, 13, 26, 0.96)")

# Maps raw OpenWeatherMap "main" condition strings to a visual theme group
CONDITION_GROUPS = {
    "clear": "clear",
    "clouds": "clouds",
    "rain": "rain",
    "drizzle": "rain",
    "thunderstorm": "storm",
    "snow": "snow",
    "mist": "fog",
    "smoke": "fog",
    "haze": "fog",
    "dust": "fog",
    "fog": "fog",
    "sand": "fog",
    "ash": "fog",
    "squall": "storm",
    "tornado": "storm",
}

# High-quality background photo per theme group, split by day / night
THEME_IMAGES = {
    "clear": {
        "day": "https://images.unsplash.com/photo-1601297183305-6df142704ea2?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1920&q=80",
    },
    "clouds": {
        "day": "https://images.unsplash.com/photo-1499956827185-0d63ee78a910?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?auto=format&fit=crop&w=1920&q=80",
    },
    "rain": {
        "day": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1428592953211-077101b2021b?auto=format&fit=crop&w=1920&q=80",
    },
    "storm": {
        "day": "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?auto=format&fit=crop&w=1920&q=80",
    },
    "snow": {
        "day": "https://images.unsplash.com/photo-1477601263568-180e2c6d046e?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?auto=format&fit=crop&w=1920&q=80",
    },
    "fog": {
        "day": "https://images.unsplash.com/photo-1543968996-ee822b8176ba?auto=format&fit=crop&w=1920&q=80",
        "night": "https://images.unsplash.com/photo-1508361001413-7a9dca21d08a?auto=format&fit=crop&w=1920&q=80",
    },
}

# Overlay tint per theme group / time-of-day, tuned so glass cards & text stay fully legible
THEME_OVERLAYS = {
    "clear": {
        "day": ("rgba(15, 45, 90, 0.42)", "rgba(6, 10, 22, 0.80)"),
        "night": ("rgba(3, 6, 18, 0.78)", "rgba(2, 4, 12, 0.94)"),
    },
    "clouds": {
        "day": ("rgba(30, 41, 59, 0.60)", "rgba(8, 13, 26, 0.86)"),
        "night": ("rgba(6, 9, 18, 0.78)", "rgba(4, 6, 14, 0.94)"),
    },
    "rain": {
        "day": ("rgba(8, 22, 40, 0.68)", "rgba(5, 9, 18, 0.90)"),
        "night": ("rgba(4, 8, 18, 0.80)", "rgba(2, 4, 10, 0.95)"),
    },
    "storm": {
        "day": ("rgba(12, 10, 28, 0.72)", "rgba(4, 4, 12, 0.92)"),
        "night": ("rgba(6, 5, 16, 0.82)", "rgba(2, 2, 8, 0.96)"),
    },
    "snow": {
        "day": ("rgba(51, 65, 85, 0.42)", "rgba(10, 15, 29, 0.80)"),
        "night": ("rgba(10, 14, 26, 0.75)", "rgba(4, 6, 14, 0.92)"),
    },
    "fog": {
        "day": ("rgba(30, 35, 45, 0.62)", "rgba(8, 11, 18, 0.85)"),
        "night": ("rgba(6, 8, 14, 0.78)", "rgba(3, 4, 10, 0.93)"),
    },
}

def resolve_weather_theme(main_condition, is_day):
    """Return (background_image_url, (overlay_start, overlay_end)) for a live weather condition."""
    group = CONDITION_GROUPS.get(str(main_condition or "").strip().lower())
    variant = "day" if is_day else "night"
    if not group:
        return DEFAULT_BG_IMAGE, DEFAULT_OVERLAY
    bg_url = THEME_IMAGES.get(group, {}).get(variant, DEFAULT_BG_IMAGE)
    overlay = THEME_OVERLAYS.get(group, {}).get(variant, DEFAULT_OVERLAY)
    return bg_url, overlay

def apply_dynamic_weather_background(main_condition, is_day):
    """Injects a style block that overrides just the .stApp background, adapting to live weather."""
    bg_url, (overlay_start, overlay_end) = resolve_weather_theme(main_condition, is_day)
    st.markdown(
        "<style>.stApp { background: linear-gradient(160deg, " + overlay_start + ", " + overlay_end +
        "), url('" + bg_url + "') !important; background-attachment: fixed !important; "
        "background-size: cover !important; background-position: center !important; "
        "transition: background 0.7s ease-in-out; }</style>",
        unsafe_allow_html=True
    )


def get_api_key():
    """Resolve the OpenWeatherMap API key from st.secrets first, then a sidebar field."""
    secret_key = ""
    try:
        secret_key = st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:
        secret_key = ""

    if secret_key:
        return secret_key.strip()

    st.sidebar.markdown('<p class="nav-caption">API Key</p>', unsafe_allow_html=True)
    entered_key = st.sidebar.text_input(
        "OpenWeatherMap API Key",
        value=st.session_state.get("owm_api_key", ""),
        type="password",
        placeholder="Paste your free OpenWeatherMap key",
        label_visibility="collapsed"
    )
    st.session_state["owm_api_key"] = entered_key.strip()
    st.sidebar.caption("Get a free key at openweathermap.org/api")
    return entered_key.strip()

# ---------------- API HELPER FUNCTIONS ----------------
@st.cache_data(ttl=1800)
def geocode_city(city_name, api_key):
    city_name = str(city_name).strip()
    url = OWM_BASE + "/geo/1.0/direct?q=" + str(city_name) + "&limit=1&appid=" + str(api_key)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json()
            if results:
                item = results[0]
                return {
                    "latitude": item["lat"],
                    "longitude": item["lon"],
                    "name": item.get("name", city_name),
                    "country": item.get("country", "")
                }
    except Exception:
        pass
    return None

@st.cache_data(ttl=600)
def fetch_current_weather(lat, lon, api_key, units):
    url = (
        OWM_BASE + "/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) +
        "&units=" + str(units) + "&appid=" + str(api_key)
    )
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=900)
def fetch_forecast(lat, lon, api_key, units):
    url = (
        OWM_BASE + "/data/2.5/forecast?lat=" + str(lat) + "&lon=" + str(lon) +
        "&units=" + str(units) + "&appid=" + str(api_key)
    )
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=1800)
def fetch_uv_index(lat, lon, api_key):
    url = OWM_BASE + "/data/2.5/uvi?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + str(api_key)
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("value")
    except Exception:
        pass
    return None

def decode_owm_icon(icon_code, description):
    prefix = str(icon_code)[:2] if icon_code else ""
    mapping = {
        "01": "☀️",
        "02": "🌤️",
        "03": "⛅",
        "04": "☁️",
        "09": "🌧️",
        "10": "🌦️",
        "11": "🌩️",
        "13": "❄️",
        "50": "🌫️",
    }
    icon = mapping.get(prefix, "🌡️")
    label = str(description).title() if description else "Unknown"
    return label, icon

def wind_direction_label(deg):
    if deg is None:
        return "N/A"
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = round(float(deg) / 22.5) % 16
    return dirs[idx]

def uv_risk_label(uv_value):
    if uv_value is None:
        return "N/A"
    if uv_value < 3:
        return "Low"
    if uv_value < 6:
        return "Moderate"
    if uv_value < 8:
        return "High"
    if uv_value < 11:
        return "Very High"
    return "Extreme"

# ---------------- PAGE: HOME ----------------
def page_home():
    apply_custom_styles(DEFAULT_BG_IMAGE)

    st.markdown('<div class="hero-title">Weather Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Live meteorological intelligence, refined</div>', unsafe_allow_html=True)

    api_key = get_api_key()
    if not api_key:
        st.warning("Enter your free OpenWeatherMap API key in the sidebar to fetch live forecasts.")
        return

    with st.form(key="search_form"):
        col_search, col_opts1, col_opts2 = st.columns([2.5, 1, 1])

        with col_search:
            default_city = st.session_state.get("active_city", "Karachi").strip()
            city_input = st.text_input("SEARCH CITY", value=default_city, placeholder="e.g. Karachi, Tokyo, London, New York")

        with col_opts1:
            unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"])

        with col_opts2:
            speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"])

        submit_btn = st.form_submit_button("Get Meteorological Forecast")

    if submit_btn:
        cleaned_city = city_input.strip()
        if cleaned_city:
            st.session_state["active_city"] = cleaned_city
        else:
            st.warning("Please enter a valid city name.")

    col_reset, _ = st.columns([1, 3])
    with col_reset:
        if st.button("Reset / Search Another City"):
            st.session_state["active_city"] = ""
            st.rerun()

    active_city = st.session_state.get("active_city", "Karachi").strip()
    if not active_city:
        active_city = "Karachi"

    owm_units = "imperial" if "Fahrenheit" in unit else "metric"
    u_sym = "°F" if "Fahrenheit" in unit else "°C"

    with st.spinner("Fetching live data for " + str(active_city) + "..."):
        geo = geocode_city(active_city, api_key)
        if not geo:
            st.error("Could not find coordinates for '" + str(active_city) + "'. Please enter a valid city name.")
            return

        lat, lon = geo["latitude"], geo["longitude"]
        city_full = str(geo['name']) + ", " + str(geo.get('country', ''))

        current = fetch_current_weather(lat, lon, api_key, owm_units)
        forecast = fetch_forecast(lat, lon, api_key, owm_units)
        uv_value = fetch_uv_index(lat, lon, api_key)

        if not current or not forecast:
            st.error("Unable to retrieve weather details. Please check your API key or try again shortly.")
            return

    main_block = current.get("main", {})
    wind_block = current.get("wind", {})
    weather_block = (current.get("weather") or [{}])[0]

    w_desc, w_icon = decode_owm_icon(weather_block.get("icon"), weather_block.get("description"))

    # Adapt the full-page background to the live weather condition (day/night aware)
    icon_code = str(weather_block.get("icon", ""))
    is_day = not icon_code.endswith("n")
    apply_dynamic_weather_background(weather_block.get("main"), is_day)

    t_curr = main_block.get("temp", 0.0)
    t_feels = main_block.get("feels_like", 0.0)
    humidity = main_block.get("humidity", 0)
    pressure = main_block.get("pressure", 0)
    visibility_km = current.get("visibility", 0) / 1000.0

    wind_spd = wind_block.get("speed", 0.0)
    if owm_units == "metric":
        wind_spd = wind_spd * 3.6  # m/s -> km/h
        if speed_unit == "m/s":
            wind_spd = wind_spd / 3.6
    else:
        # imperial units already return mph; convert to km/h baseline then to requested unit
        wind_spd_kmh = wind_spd * 1.60934
        wind_spd = wind_spd_kmh if speed_unit == "km/h" else wind_spd_kmh / 3.6

    wind_dir = wind_direction_label(wind_block.get("deg"))
    uv_label = uv_risk_label(uv_value)
    uv_display = f"{uv_value:.1f}" if uv_value is not None else "N/A"

    st.markdown("---")

    card_lines = [
        '<div class="glass-card">',
        '<h2 style="margin-bottom:0px;">' + str(w_icon) + ' ' + str(city_full) + '</h2>',
        '<p style="color:#64748B !important; margin-top:4px; font-size:0.85rem; letter-spacing:0.3px;">COORDINATES · ' + f'{lat:.2f}' + '°N, ' + f'{lon:.2f}' + '°E</p>',
        '<h1 style="font-size: 3.8rem; margin: 14px 0; color:#38BDF8 !important; font-weight:700;">' + f'{t_curr:.1f}' + ' ' + str(u_sym) + ' <span style="font-size:1.5rem; font-weight:400; color:#94A3B8 !important;">' + str(w_desc) + '</span></h1>',
        '<div style="margin-top:16px;">',
        '<span class="badge">Feels Like &nbsp;' + f'{t_feels:.1f}' + ' ' + str(u_sym) + '</span>',
        '<span class="badge">Humidity &nbsp;' + str(humidity) + '%</span>',
        '<span class="badge">Wind &nbsp;' + f'{wind_spd:.1f}' + ' ' + str(speed_unit) + ' ' + str(wind_dir) + '</span>',
        '<span class="badge">UV Index &nbsp;' + str(uv_display) + ' (' + str(uv_label) + ')</span>',
        '<span class="badge">Pressure &nbsp;' + str(pressure) + ' hPa</span>',
        '<span class="badge">Visibility &nbsp;' + f'{visibility_km:.1f}' + ' km</span>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(card_lines), unsafe_allow_html=True)

    # ---- Parse 3-hour forecast list into hourly (next 24h) and daily buckets ----
    forecast_list = forecast.get("list", [])

    h_times, h_temps, h_humidity, h_rain = [], [], [], []
    for entry in forecast_list[:8]:  # 8 x 3-hour steps ≈ 24 hours
        dt_txt = entry.get("dt_txt", "")
        try:
            label = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").strftime("%H:00")
        except ValueError:
            label = dt_txt
        h_times.append(label)
        h_temps.append(entry.get("main", {}).get("temp", 0.0))
        h_humidity.append(entry.get("main", {}).get("humidity", 0))
        h_rain.append(round(entry.get("pop", 0.0) * 100))

    daily_buckets = defaultdict(list)
    for entry in forecast_list:
        date_key = entry.get("dt_txt", "")[:10]
        daily_buckets[date_key].append(entry)

    d_dates, d_max, d_min, d_conditions, d_icons, d_rain, d_wind = [], [], [], [], [], [], []
    for date_key in sorted(daily_buckets.keys())[:5]:
        entries = daily_buckets[date_key]
        temps = [e.get("main", {}).get("temp", 0.0) for e in entries]
        pops = [e.get("pop", 0.0) for e in entries]
        winds = [e.get("wind", {}).get("speed", 0.0) for e in entries]
        mid_entry = entries[len(entries) // 2]
        mid_weather = (mid_entry.get("weather") or [{}])[0]
        cond_label, cond_icon = decode_owm_icon(mid_weather.get("icon"), mid_weather.get("description"))

        d_dates.append(datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime("%a, %b %d"))
        d_max.append(max(temps) if temps else 0.0)
        d_min.append(min(temps) if temps else 0.0)
        d_conditions.append(cond_label)
        d_icons.append(cond_icon)
        d_rain.append(round(max(pops) * 100) if pops else 0)
        wind_kmh = (max(winds) * 3.6) if owm_units == "metric" else (max(winds) * 1.60934) if winds else 0.0
        d_wind.append(wind_kmh if speed_unit == "km/h" else wind_kmh / 3.6)

    # 24-Hour Plotly Graph
    st.markdown("### 24-Hour Temperature Trend")
    fig_hourly = go.Figure()
    fig_hourly.add_trace(
        go.Scatter(
            x=h_times,
            y=h_temps,
            mode="lines+markers",
            name="Temp (" + str(u_sym) + ")",
            line=dict(color="#38BDF8", width=3, shape="spline"),
            marker=dict(size=5, color="#818CF8"),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 233, 0.14)"
        )
    )
    fig_hourly.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94A3B8"),
        xaxis_title="Time of Day (3-hour steps)",
        yaxis_title="Temperature (" + str(u_sym) + ")",
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    # 5-Day Forecast Chart
    st.markdown("### 5-Day Extended Forecast")
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_max, name="Max Temp (" + str(u_sym) + ")", marker_color="#38BDF8"))
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_min, name="Min Temp (" + str(u_sym) + ")", marker_color="#4F46E5"))

    fig_daily.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94A3B8"),
        barmode="group",
        margin=dict(l=20, r=20, t=20, b=20),
        height=340
    )
    st.plotly_chart(fig_daily, use_container_width=True)

    # Data Tables
    st.markdown("### Tabular Breakdown")
    tab1, tab2 = st.tabs(["5-Day Daily Forecast Data", "Hourly Forecast Data (Next 24h)"])

    with tab1:
        st.dataframe(
            {
                "Date": d_dates,
                "Condition": [str(d_icons[i]) + " " + str(d_conditions[i]) for i in range(len(d_dates))],
                "Max Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_max],
                "Min Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_min],
                "Rain Probability": [str(p) + "%" for p in d_rain],
                "Max Wind (" + str(speed_unit) + ")": [round(w, 1) for w in d_wind]
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            {
                "Time": h_times,
                "Temperature (" + str(u_sym) + ")": [round(x, 1) for x in h_temps],
                "Humidity": [str(h) + "%" for h in h_humidity],
                "Rain Probability": [str(p) + "%" for p in h_rain]
            },
            use_container_width=True,
            hide_index=True
        )

    st.caption("Crafted by **Hafiz Muhammad Ubaid** · Powered by OpenWeatherMap")

# ---------------- PAGE: ABOUT ----------------
def page_about():
    apply_custom_styles("https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1920&q=80")

    st.markdown('<div class="hero-title">About the Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Design philosophy &amp; technical overview</div>', unsafe_allow_html=True)

    about_lines = [
        '<div class="glass-card">',
        '<h2>Weather Forecast — Hafiz Muhammad Ubaid</h2>',
        '<p>Welcome to <b>Weather Forecast</b> — a modern, interactive weather tracking platform designed to offer high-precision, real-time meteorological insight for cities across the globe.</p>',
        '<hr>',
        '<h3>Advanced Features</h3>',
        '<ul>',
        '<li><b>Seamless City Search:</b> Instantly toggle between multiple cities without refreshing the browser manually.</li>',
        '<li><b>Zero API Keys Required:</b> Powered by Open-Meteo\'s open-source meteorological API.</li>',
        '<li><b>Global Geocoding:</b> Auto-detects coordinates for any city worldwide.</li>',
        '<li><b>Interactive Analytics:</b> Glassmorphism UI rendered with Plotly analytics charts.</li>',
        '</ul>',
        '<hr>',
        '<h3>Developer</h3>',
        '<p>Designed and engineered by <b>Hafiz Muhammad Ubaid</b>.</p>',
        '</div>'
    ]
    st.markdown("".join(about_lines), unsafe_allow_html=True)

# ---------------- PAGE: CONTACT ----------------
def page_contact():
    apply_custom_styles("https://images.unsplash.com/photo-1516912481808-3406841bd33c?auto=format&fit=crop&w=1920&q=80")

    st.markdown('<div class="hero-title">Connect</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Collaboration &amp; feedback channels</div>', unsafe_allow_html=True)

    email_address = "ubaidsajid2006@gmail.com"
    insta_link = "https://www.instagram.com/muhammadubaid__?stkn=eWV4ejI1MXh0Mndr&utm_source=qr"
    linkedin_link = "https://www.linkedin.com/in/muhammad-ubaid-2b88722b3?utm_source=share_via&utm_content=profile&utm_medium=member_ios"

    contact_lines = [
        '<div class="glass-card">',
        '<h2>Hafiz Muhammad Ubaid</h2>',
        '<p style="font-size: 1.02rem; color: #94A3B8 !important;">Feel free to reach out for collaborations, feedback, or development inquiries.</p>',
        '<hr style="margin: 22px 0;">',
        '<h3>Contact &amp; Social Profiles</h3>',
        '<p style="color: #64748B !important; font-size:0.88rem;">Click any icon below to email me or connect directly on my socials.</p>',
        '<div style="margin-top: 22px; display: flex; align-items: center; gap: 4px;">',
        '<a href="mailto:' + str(email_address) + '" class="social-icon-btn icon-email" title="Send Email"><i class="fa-solid fa-envelope"></i></a>',
        '<a href="' + str(insta_link) + '" target="_blank" class="social-icon-btn icon-insta" title="Instagram Profile"><i class="fa-brands fa-instagram"></i></a>',
        '<a href="' + str(linkedin_link) + '" target="_blank" class="social-icon-btn icon-linkedin" title="LinkedIn Profile"><i class="fa-brands fa-linkedin-in"></i></a>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(contact_lines), unsafe_allow_html=True)

# ---------------- MAIN ROUTER ----------------
def main():
    st.sidebar.markdown("""
        <div class="brand-block">
            <div class="brand-mark"><i class="fa-solid fa-cloud-sun"></i></div>
            <p class="brand-title">Weather Forecast</p>
            <p class="brand-subtitle">by Hafiz Muhammad Ubaid</p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<p class="nav-caption">Navigation</p>', unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "About", "Contact"],
        label_visibility="collapsed"
    )

    if page == "Home":
        page_home()
    elif page == "About":
        page_about()
    else:
        page_contact()

if __name__ == "__main__":
    main()
