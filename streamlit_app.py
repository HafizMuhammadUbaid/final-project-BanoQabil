import streamlit as st
import datetime
import requests
from collections import defaultdict
from urllib.parse import quote
from plotly import graph_objects as go

OWM_BASE = "https://api.openweathermap.org"

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Weather Forecast | Hafiz Muhammad Ubaid",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================================
# WEATHER CATEGORY ENGINE
# 7 granular condition categories, resolved from OpenWeatherMap's precise numeric
# weather-condition "id" (far more specific than the coarse "main" string).
# =====================================================================================
CATEGORY_LABELS = {
    "clear": "Clear / Sunny",
    "partly_cloudy": "Partly Cloudy",
    "overcast": "Overcast / Heavy Clouds",
    "light_rain": "Light Rain / Showers",
    "heavy_rain": "Heavy Rain / Thunderstorm",
    "snow": "Snow",
    "fog": "Fog / Haze",
}

def get_weather_category(weather_id):
    """Maps an OpenWeatherMap condition id to one of 7 granular visual categories."""
    try:
        wid = int(weather_id)
    except (TypeError, ValueError):
        return "clear"

    if 200 <= wid <= 232:                        # thunderstorm family
        return "heavy_rain"
    if 300 <= wid <= 321:                         # drizzle family
        return "light_rain"
    if wid in (500, 501, 520, 521):               # light / moderate rain & showers
        return "light_rain"
    if wid in (502, 503, 504, 511, 522, 531):      # heavy / violent / freezing rain
        return "heavy_rain"
    if 600 <= wid <= 622:                         # snow family
        return "snow"
    if wid in (771, 781):                         # squall / tornado -> severe
        return "heavy_rain"
    if 701 <= wid <= 762:                          # mist, smoke, haze, dust, fog, sand, ash
        return "fog"
    if wid == 800:                                 # clear sky
        return "clear"
    if wid in (801, 802):                          # few / scattered clouds
        return "partly_cloudy"
    if wid in (803, 804):                          # broken / overcast clouds
        return "overcast"
    return "clear"

def compute_is_day(current_json):
    """Strictly determines day vs night using the searched city's own sunrise/sunset epochs."""
    try:
        dt_epoch = current_json.get("dt")
        sys_block = current_json.get("sys", {})
        sunrise = sys_block.get("sunrise")
        sunset = sys_block.get("sunset")
        if dt_epoch is not None and sunrise is not None and sunset is not None:
            return sunrise <= dt_epoch <= sunset
    except Exception:
        pass
    icon_code = (current_json.get("weather") or [{}])[0].get("icon", "")
    return not str(icon_code).endswith("n")

def get_local_time_str(current_json):
    """Formats the searched city's exact local time using its UTC offset."""
    try:
        dt_epoch = current_json.get("dt")
        tz_offset = current_json.get("timezone", 0)
        local_dt = datetime.datetime.utcfromtimestamp(dt_epoch + tz_offset)
        return local_dt.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return "N/A"

# =====================================================================================
# DYNAMIC MP4 VIDEO BACKGROUNDS (with graceful fallback)
# Direct, hotlinkable, royalty-free MP4 loops (Mixkit CDN) mapped per granular category.
# Each video ships with a matching poster thumbnail so the first frame never flashes
# blank while the clip buffers.
# =====================================================================================
def _mixkit_video(clip_id):
    return {
        "src": f"https://assets.mixkit.co/videos/{clip_id}/{clip_id}-720.mp4",
        "poster": f"https://assets.mixkit.co/videos/{clip_id}/{clip_id}-thumb-720-0.jpg",
    }

CATEGORY_VIDEO = {
    "clear": _mixkit_video(9673),          # Sunbeams through moving clouds
    "partly_cloudy": _mixkit_video(31459),  # Clouds moving smoothly in the sky
    "overcast": _mixkit_video(9606),        # Dark storm clouds
    "light_rain": _mixkit_video(25375),     # Soft rain and sun shine
    "heavy_rain": _mixkit_video(47698),     # Lightning in the clouds during a thunderstorm
    "snow": _mixkit_video(8479),            # Thick snow falling in slow motion
    "fog": _mixkit_video(28342),            # Slow aerial tour through a mist-covered forest
}

# Rich, multi-layer CSS mesh gradient per category + day/night -- this is the automatic
# safety net that renders the instant the page paints, before any video/photo has had a
# chance to load, and permanently if both external assets fail.
CATEGORY_THEMES = {
    "clear": {
        "day": {"gradient": (
            "radial-gradient(circle at 82% 12%, rgba(255,196,90,0.85) 0%, rgba(255,170,70,0.35) 20%, transparent 45%), "
            "radial-gradient(circle at 15% 85%, rgba(56,189,248,0.25) 0%, transparent 55%), "
            "linear-gradient(160deg, rgba(30,74,140,0.55) 0%, rgba(10,20,40,0.88) 100%)"
        ), "bg_color": "#0b2340", "keywords": "sunny,blue,sky"},
        "night": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(88,28,135,0.55) 0%, transparent 50%), "
            "radial-gradient(circle at 20% 70%, rgba(30,64,175,0.35) 0%, transparent 55%), "
            "linear-gradient(180deg, rgba(6,8,20,0.9) 0%, rgba(2,3,10,0.97) 100%)"
        ), "bg_color": "#04050d", "keywords": "night,stars,sky"},
    },
    "partly_cloudy": {
        "day": {"gradient": (
            "radial-gradient(circle at 75% 20%, rgba(255,220,150,0.40) 0%, transparent 40%), "
            "linear-gradient(150deg, rgba(70,110,160,0.55) 0%, rgba(20,30,55,0.88) 100%)"
        ), "bg_color": "#101d33", "keywords": "clouds,sky,day"},
        "night": {"gradient": (
            "radial-gradient(circle at 30% 20%, rgba(148,163,184,0.25) 0%, transparent 45%), "
            "linear-gradient(160deg, rgba(20,26,46,0.85) 0%, rgba(6,8,16,0.95) 100%)"
        ), "bg_color": "#080b14", "keywords": "clouds,night,sky"},
    },
    "overcast": {
        "day": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(148,163,184,0.35) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(51,65,85,0.75) 0%, rgba(15,20,32,0.92) 100%)"
        ), "bg_color": "#0d1119", "keywords": "overcast,grey,sky"},
        "night": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(71,85,105,0.30) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(15,20,32,0.88) 0%, rgba(4,5,10,0.96) 100%)"
        ), "bg_color": "#040508", "keywords": "overcast,night"},
    },
    "light_rain": {
        "day": {"gradient": (
            "radial-gradient(circle at 70% 10%, rgba(96,165,250,0.30) 0%, transparent 45%), "
            "linear-gradient(165deg, rgba(30,58,95,0.78) 0%, rgba(8,14,26,0.92) 100%)"
        ), "bg_color": "#081019", "keywords": "rain,drizzle,city"},
        "night": {"gradient": (
            "radial-gradient(circle at 30% 10%, rgba(59,130,246,0.22) 0%, transparent 45%), "
            "linear-gradient(165deg, rgba(8,14,26,0.88) 0%, rgba(2,4,10,0.96) 100%)"
        ), "bg_color": "#020409", "keywords": "rain,night,city"},
    },
    "heavy_rain": {
        "day": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(30,41,59,0.60) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(17,24,39,0.85) 0%, rgba(3,4,10,0.95) 100%)"
        ), "bg_color": "#020308", "keywords": "thunderstorm,dark,rain"},
        "night": {"gradient": (
            "radial-gradient(circle at 50% 10%, rgba(30,27,75,0.50) 0%, transparent 50%), "
            "linear-gradient(165deg, rgba(8,7,20,0.9) 0%, rgba(1,1,4,0.97) 100%)"
        ), "bg_color": "#010104", "keywords": "thunderstorm,night,lightning"},
    },
    "snow": {
        "day": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(226,232,240,0.40) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(100,116,139,0.50) 0%, rgba(15,23,42,0.88) 100%)"
        ), "bg_color": "#0c1424", "keywords": "snow,winter,day"},
        "night": {"gradient": (
            "radial-gradient(circle at 50% 0%, rgba(148,163,184,0.22) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(15,23,42,0.85) 0%, rgba(4,6,14,0.96) 100%)"
        ), "bg_color": "#04060e", "keywords": "snow,winter,night"},
    },
    "fog": {
        "day": {"gradient": (
            "radial-gradient(circle at 50% 30%, rgba(45,212,191,0.18) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(51,65,85,0.60) 0%, rgba(15,23,42,0.90) 100%)"
        ), "bg_color": "#0b1420", "keywords": "fog,mist,teal"},
        "night": {"gradient": (
            "radial-gradient(circle at 50% 30%, rgba(45,212,191,0.12) 0%, transparent 55%), "
            "linear-gradient(165deg, rgba(10,15,25,0.88) 0%, rgba(3,5,10,0.96) 100%)"
        ), "bg_color": "#03050a", "keywords": "fog,night,mist"},
    },
}

CATEGORY_PHOTO_KEYWORD = {
    "clear": "sunny", "partly_cloudy": "cloudy", "overcast": "cloudy",
    "light_rain": "rainy", "heavy_rain": "thunderstorm", "snow": "snow", "fog": "fog",
}

def resolve_weather_theme(category, is_day):
    variant = "day" if is_day else "night"
    group = CATEGORY_THEMES.get(category, CATEGORY_THEMES["clear"])
    return group.get(variant, group["day"])

def build_dynamic_photo_url(category, is_day, city_name):
    """Keyword-driven Unsplash Source URL -- the image fallback tier, matched to
    weather + local time + the exact searched city."""
    weather_kw = CATEGORY_PHOTO_KEYWORD.get(category, "sky")
    day_kw = "day" if is_day else "night"
    city_kw = quote(str(city_name or "").strip()) or "city"
    return "https://source.unsplash.com/1600x900/?" + weather_kw + "," + day_kw + "," + city_kw

def render_dynamic_weather_background(category, is_day, city_name):
    """
    Layers three backdrop tiers, back to front:
      1) A pure-CSS mesh gradient (instant, cannot fail) -- z-index -3
      2) A keyword-matched Unsplash photo -- z-index -2
      3) A full-screen looping, silent, controls-free MP4 for the matched weather
         condition -- z-index -1
    A semi-transparent dark scrim sits on top of all three so text/inputs stay legible.

    The <video> carries every attribute mobile browsers require for a true
    background-style autoplay loop (autoplay, loop, muted, playsinline +
    webkit-playsinline, no controls, no picture-in-picture/remote-playback affordances).
    Position/size/z-index are set both via the stylesheet below AND as inline styles on
    the tag itself, so the fixed full-bleed placement holds even if a class selector
    ever fails to match. If the clip 404s or the browser blocks it outright, the
    <source>'s onerror handler removes the element from the layout entirely (rather
    than leaving a paused frame with a native play button) and the photo/gradient
    tiers underneath show straight through -- the UI can never visibly break.
    """
    theme = resolve_weather_theme(category, is_day)
    photo_url = build_dynamic_photo_url(category, is_day, city_name)
    video = CATEGORY_VIDEO.get(category, CATEGORY_VIDEO["clear"])

    st.markdown(
        "<style>.stApp{background:" + theme["gradient"] + " !important;"
        "background-color:" + theme["bg_color"] + " !important;}</style>",
        unsafe_allow_html=True
    )

    video_inline_style = (
        "position:fixed;top:0;left:0;width:100vw;height:100vh;"
        "object-fit:cover;pointer-events:none;z-index:-1;background:#000;"
    )

    backdrop_html = f"""
    <div class="bg-photo-layer" style="background-image:url('{photo_url}');"></div>
    <div class="bg-video-layer">
        <video id="wx-video" class="wx-bg-video" style="{video_inline_style}"
               autoplay loop muted playsinline webkit-playsinline="true"
               disablePictureInPicture disableRemotePlayback
               preload="auto" poster="{video['poster']}">
            <source src="{video['src']}" type="video/mp4"
                    onerror="var w=document.getElementById('wx-video'); if(w){{w.parentNode.removeChild(w);}}">
        </video>
    </div>
    <div class="bg-dark-scrim"></div>
    """
    st.markdown(backdrop_html, unsafe_allow_html=True)

# =====================================================================================
# ANIMATED SVG WEATHER ICONS (lightweight, dependency-free, per-condition)
# =====================================================================================
def get_weather_svg_icon(category, is_day=True):
    common = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" class="wx-svg-icon"'
    if category == "clear":
        return f'''<svg {common}><g class="wx-sun-spin">
            <circle cx="50" cy="50" r="18" fill="#FDB813"/>
            <g stroke="#FDB813" stroke-width="4" stroke-linecap="round">
                <line x1="50" y1="10" x2="50" y2="22"/><line x1="50" y1="78" x2="50" y2="90"/>
                <line x1="10" y1="50" x2="22" y2="50"/><line x1="78" y1="50" x2="90" y2="50"/>
                <line x1="21" y1="21" x2="29" y2="29"/><line x1="71" y1="71" x2="79" y2="79"/>
                <line x1="79" y1="21" x2="71" y2="29"/><line x1="29" y1="71" x2="21" y2="79"/>
            </g></g></svg>'''
    if category in ("partly_cloudy",) or (category == "clear" and not is_day):
        return f'''<svg {common}>
            <circle cx="38" cy="40" r="14" fill="#FDB813" class="wx-sun-spin"/>
            <g class="wx-cloud-drift">
                <ellipse cx="55" cy="62" rx="28" ry="16" fill="#E2E8F0"/>
                <ellipse cx="38" cy="55" rx="16" ry="12" fill="#F1F5F9"/>
            </g></svg>'''
    if category == "overcast":
        return f'''<svg {common}><g class="wx-cloud-drift">
            <ellipse cx="42" cy="48" rx="26" ry="15" fill="#64748B"/>
            <ellipse cx="62" cy="55" rx="22" ry="14" fill="#94A3B8"/>
            <ellipse cx="50" cy="60" rx="30" ry="16" fill="#475569"/>
        </g></svg>'''
    if category == "light_rain":
        drops = "".join(
            f'<line x1="{x}" y1="62" x2="{x-4}" y2="78" stroke="#60A5FA" stroke-width="3" '
            f'stroke-linecap="round" class="wx-rain-drop" style="animation-delay:{d}s"/>'
            for x, d in [(32, 0), (48, 0.25), (64, 0.5), (78, 0.15)]
        )
        return f'''<svg {common}><ellipse cx="52" cy="46" rx="26" ry="15" fill="#94A3B8"/>{drops}</svg>'''
    if category == "heavy_rain":
        drops = "".join(
            f'<line x1="{x}" y1="60" x2="{x-4}" y2="80" stroke="#38BDF8" stroke-width="3" '
            f'stroke-linecap="round" class="wx-rain-drop-fast" style="animation-delay:{d}s"/>'
            for x, d in [(30, 0), (46, 0.15), (62, 0.3), (76, 0.05)]
        )
        return f'''<svg {common}>
            <ellipse cx="50" cy="42" rx="28" ry="15" fill="#334155"/>
            <polygon points="52,50 44,68 52,68 46,86 66,60 56,60 62,50" fill="#FACC15" class="wx-bolt-flash"/>
            {drops}</svg>'''
    if category == "snow":
        flakes = "".join(
            f'<text x="{x}" y="{y}" font-size="12" fill="#F1F5F9" class="wx-snow-fall" '
            f'style="animation-delay:{d}s">&#10052;</text>'
            for x, y, d in [(30, 55, 0), (50, 50, 0.6), (68, 58, 0.3), (40, 70, 0.9)]
        )
        return f'''<svg {common}><ellipse cx="50" cy="42" rx="26" ry="14" fill="#CBD5E1"/>{flakes}</svg>'''
    if category == "fog":
        bands = "".join(
            f'<rect x="10" y="{y}" width="80" height="6" rx="3" fill="#94A3B8" '
            f'class="wx-fog-drift" style="animation-delay:{d}s"/>'
            for y, d in [(38, 0), (52, 0.4), (66, 0.8)]
        )
        return f'''<svg {common}>{bands}</svg>'''
    return f'''<svg {common}><circle cx="50" cy="50" r="20" fill="#94A3B8"/></svg>'''

# =====================================================================================
# GLOBAL STYLING -- immersive full-bleed glassmorphism
# =====================================================================================
def apply_custom_styles():
    css_lines = [
        "<style>",
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800&display=swap');",
        "@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');",

        # ---------- RESET / FULL-BLEED IMMERSION ----------
        "html, body, .stApp { margin:0 !important; padding:0 !important; font-family:'Inter',sans-serif; overflow-x:hidden; }",
        ".block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 1300px !important; }",
        "#MainMenu, footer { visibility:hidden; }",
        # Top nav bar (Streamlit header) and the sidebar sit in their own, much higher
        # stacking layer than the background stack below, so they always stay clean
        # and clickable above the video/photo/gradient.
        "header[data-testid='stHeader'] {",
        "    background: transparent !important; box-shadow:none !important;",
        "    z-index: 1000 !important; position: relative;",
        "}",
        "[data-testid='stAppViewContainer'] { position:relative; z-index:10; background:transparent !important; }",
        "[data-testid='stAppViewContainer'] > .main { background:transparent !important; }",
        "section[data-testid='stSidebar'] { z-index:1000 !important; }",

        # ---------- LAYERED VIDEO BACKGROUND STACK ----------
        # Paint order, back to front: CSS gradient (-3) -> Unsplash photo (-2) ->
        # looping MP4 (-1) -> dark legibility scrim (-1, painted after the video so it
        # sits visually on top of it). Everything here is `position:fixed` + negative
        # z-index, so it always renders behind the header/sidebar/content above.
        ".bg-photo-layer, .bg-video-layer, .bg-dark-scrim {",
        "    position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none;",
        "}",
        ".bg-photo-layer {",
        "    z-index:-3; background-size:cover; background-position:center; opacity:0.9;",
        "    transition:background-image 0.9s ease-in-out;",
        "}",
        ".bg-video-layer { z-index:-2; overflow:hidden; }",
        ".bg-video-layer video, video.wx-bg-video {",
        "    position:fixed !important; top:0 !important; left:0 !important;",
        "    width:100vw !important; height:100vh !important; object-fit:cover !important;",
        "    pointer-events:none !important; z-index:-1 !important; background:#000;",
        "    transition:opacity 0.9s ease-in-out;",
        "}",
        # Kill every native play/controls affordance a browser might still try to draw
        # (this is what causes the centered play-button overlay, especially on
        # Safari/iOS) so the clip reads purely as scenery, never as a media player.
        ".bg-video-layer video::-webkit-media-controls,",
        ".bg-video-layer video::-webkit-media-controls-start-playback-button,",
        ".bg-video-layer video::-webkit-media-controls-play-button,",
        ".bg-video-layer video::-webkit-media-controls-panel,",
        ".bg-video-layer video::-webkit-media-controls-overlay-play-button {",
        "    display:none !important; -webkit-appearance:none !important; opacity:0 !important;",
        "}",
        ".bg-dark-scrim { z-index:-1; background:rgba(0,0,0,0.45); }",

        "h1, h2, h3, h4, h5, h6 { font-family:'Poppins',sans-serif !important; color:#F8FAFC !important; letter-spacing:0.3px; }",
        "p, label, span, div { color:#E2E8F0 !important; }",

        # ---------- HERO TITLE ----------
        ".hero-title {",
        "    font-family:'Poppins',sans-serif; font-weight:800; font-size:2.7rem;",
        "    background:linear-gradient(135deg,#38BDF8 0%,#818CF8 60%,#C084FC 100%);",
        "    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;",
        "    margin-bottom:0px; letter-spacing:-0.5px;",
        "}",
        ".hero-subtitle {",
        "    color:#94A3B8 !important; font-size:0.95rem; font-weight:400; margin-top:4px;",
        "    margin-bottom:26px; letter-spacing:0.5px; text-transform:uppercase;",
        "}",

        # ---------- GLASSMORPHIC CARD (per spec) ----------
        ".glass-card {",
        "    background: rgba(255, 255, 255, 0.08);",
        "    backdrop-filter: blur(14px);",
        "    -webkit-backdrop-filter: blur(14px);",
        "    border: 1px solid rgba(255, 255, 255, 0.18);",
        "    border-radius: 20px;",
        "    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);",
        "    padding: 32px;",
        "    margin-bottom: 24px;",
        "    transition: transform 0.3s ease, border-color 0.3s ease;",
        "}",
        ".glass-card:hover { border-color: rgba(56,189,248,0.4); }",

        # ---------- NEON TEMPERATURE DISPLAY ----------
        ".temp-glow {",
        "    font-size: 4.2rem; font-weight: 700; color: #F0FAFF !important;",
        "    text-shadow: 0 0 8px rgba(56,189,248,0.85), 0 0 22px rgba(56,189,248,0.55), 0 0 46px rgba(129,140,248,0.35);",
        "    letter-spacing: -1px; margin: 10px 0;",
        "}",
        ".temp-glow .unit-cond { font-size:1.5rem; font-weight:400; color:#B9C6D6 !important; text-shadow:none; margin-left:10px; }",

        # ---------- ANIMATED SVG ICON ----------
        ".wx-svg-icon { width:64px; height:64px; vertical-align:middle; }",
        "@keyframes wxSpin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }",
        ".wx-sun-spin { transform-origin:50px 50px; animation: wxSpin 12s linear infinite; }",
        "@keyframes wxDrift { 0%{transform:translateX(-4px);} 50%{transform:translateX(4px);} 100%{transform:translateX(-4px);} }",
        ".wx-cloud-drift { animation: wxDrift 5s ease-in-out infinite; }",
        "@keyframes wxRainDrop { 0%{opacity:0; transform:translateY(-6px);} 40%{opacity:1;} 100%{opacity:0; transform:translateY(14px);} }",
        ".wx-rain-drop { animation: wxRainDrop 1s linear infinite; }",
        ".wx-rain-drop-fast { animation: wxRainDrop 0.5s linear infinite; }",
        "@keyframes wxSnowFall { 0%{opacity:0; transform:translateY(-4px) rotate(0deg);} 50%{opacity:1;} 100%{opacity:0; transform:translateY(12px) rotate(90deg);} }",
        ".wx-snow-fall { animation: wxSnowFall 2.2s ease-in-out infinite; }",
        "@keyframes wxFogDrift { 0%{transform:translateX(-6px); opacity:0.5;} 50%{transform:translateX(6px); opacity:0.9;} 100%{transform:translateX(-6px); opacity:0.5;} }",
        ".wx-fog-drift { animation: wxFogDrift 3s ease-in-out infinite; }",
        "@keyframes wxBoltFlash { 0%,88%,100%{opacity:1;} 90%,94%{opacity:0.15;} }",
        ".wx-bolt-flash { animation: wxBoltFlash 2.6s ease-in-out infinite; }",

        # ---------- FORM / INPUT CONTAINER (glass, blended) ----------
        "div[data-testid='stForm'] {",
        "    background: rgba(255,255,255,0.06) !important;",
        "    backdrop-filter: blur(14px);",
        "    border: 1px solid rgba(255,255,255,0.18) !important;",
        "    border-radius: 20px !important; padding: 26px !important;",
        "    box-shadow: 0 8px 32px rgba(0,0,0,0.37);",
        "}",

        # ---------- INPUT / SELECT FIELDS ----------
        "div[data-baseweb='select'] > div, .stTextInput input {",
        "    background: rgba(255,255,255,0.07) !important;",
        "    backdrop-filter: blur(10px);",
        "    border: 1px solid rgba(255,255,255,0.18) !important;",
        "    border-radius: 12px !important; color:#F1F5F9 !important;",
        "    transition: border-color 0.25s ease, box-shadow 0.25s ease;",
        "}",
        ".stTextInput input:focus { border-color: rgba(56,189,248,0.6) !important; box-shadow:0 0 0 3px rgba(56,189,233,0.15) !important; }",
        "label[data-testid='stWidgetLabel'] p {",
        "    font-size:0.72rem !important; font-weight:600 !important; letter-spacing:1px !important;",
        "    text-transform:uppercase; color:#94A3B8 !important;",
        "}",

        # ---------- BUTTONS ----------
        ".stButton > button, .stFormSubmitButton > button {",
        "    width:100%; background: linear-gradient(135deg,#0EA5E9 0%,#4F46E5 100%);",
        "    color:#FFFFFF !important; font-family:'Poppins',sans-serif; font-weight:600;",
        "    font-size:0.92rem; letter-spacing:0.4px; border:none; border-radius:12px;",
        "    padding:0.8rem 1rem; transition: all 0.3s cubic-bezier(.2,.8,.2,1);",
        "    box-shadow: 0 4px 22px rgba(14,165,233,0.35);",
        "}",
        ".stButton > button:hover, .stFormSubmitButton > button:hover {",
        "    background: linear-gradient(135deg,#38BDF8 0%,#6366F1 100%);",
        "    transform: translateY(-2px); box-shadow: 0 8px 28px rgba(14,165,233,0.55);",
        "}",
        ".stButton > button:active, .stFormSubmitButton > button:active { transform: translateY(0px); }",

        # ---------- BADGES (glass pills) ----------
        ".badge {",
        "    display:inline-block; padding:9px 18px; border-radius:30px; font-size:0.82rem; font-weight:500;",
        "    background: rgba(255,255,255,0.08); backdrop-filter: blur(10px);",
        "    color:#DDEBFF !important; border:1px solid rgba(255,255,255,0.18);",
        "    margin-right:10px; margin-bottom:10px; letter-spacing:0.2px;",
        "}",

        # ---------- SOCIAL / CONTACT ICONS ----------
        ".social-icon-btn {",
        "    display:inline-flex; align-items:center; justify-content:center; width:56px; height:56px;",
        "    border-radius:50%; font-size:1.5rem; text-decoration:none !important; color:#FFFFFF !important;",
        "    transition: all 0.3s cubic-bezier(.2,.8,.2,1); margin-right:16px; margin-top:8px;",
        "    border:1px solid rgba(255,255,255,0.16);",
        "}",
        ".icon-email { background: linear-gradient(135deg,#EA4335 0%,#C5221F 100%); box-shadow:0 4px 18px rgba(234,67,53,0.30); }",
        ".icon-email:hover { transform: translateY(-4px) scale(1.08); box-shadow:0 10px 26px rgba(234,67,53,0.55); }",
        ".icon-insta { background: linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); box-shadow:0 4px 18px rgba(220,39,67,0.30); }",
        ".icon-insta:hover { transform: translateY(-4px) scale(1.08); box-shadow:0 10px 26px rgba(220,39,67,0.55); }",
        ".icon-linkedin { background:#0A66C2; box-shadow:0 4px 18px rgba(10,102,194,0.30); }",
        ".icon-linkedin:hover { transform: translateY(-4px) scale(1.08); box-shadow:0 10px 26px rgba(10,102,194,0.55); }",

        # ---------- SIDEBAR (glass) ----------
        "section[data-testid='stSidebar'] {",
        "    background: rgba(6,9,18,0.72) !important; backdrop-filter: blur(18px);",
        "    border-right: 1px solid rgba(255,255,255,0.10);",
        "}",
        "section[data-testid='stSidebar'] .block-container { padding-top:1.5rem; }",
        "[data-testid='stSidebarCollapsedControl'], button[data-testid='collapsedControl'] {",
        "    background: rgba(14,165,233,0.18) !important; border:1px solid rgba(56,189,248,0.45) !important;",
        "    border-radius:10px !important; box-shadow:0 4px 16px rgba(14,165,233,0.35) !important; padding:4px !important;",
        "}",
        "[data-testid='stSidebarCollapsedControl'] svg, button[data-testid='collapsedControl'] svg { fill:#38BDF8 !important; }",

        ".brand-block { text-align:left; padding:4px 6px 26px 6px; border-bottom:1px solid rgba(255,255,255,0.10); margin-bottom:22px; }",
        ".brand-mark {",
        "    display:inline-flex; align-items:center; justify-content:center; width:42px; height:42px;",
        "    border-radius:12px; background: linear-gradient(135deg,#0EA5E9,#6366F1); font-size:1.2rem;",
        "    color:#fff !important; margin-bottom:12px; box-shadow:0 4px 18px rgba(99,102,241,0.4);",
        "}",
        ".brand-title { font-family:'Poppins',sans-serif; font-weight:700; font-size:1.05rem; color:#F8FAFC !important; margin:0; letter-spacing:0.2px; }",
        ".brand-subtitle { font-size:0.72rem; color:#64748B !important; margin-top:2px; letter-spacing:0.4px; text-transform:uppercase; }",
        ".nav-caption { font-size:0.68rem; font-weight:600; letter-spacing:1.6px; text-transform:uppercase; color:#475569 !important; margin:4px 0 10px 6px; }",

        "section[data-testid='stSidebar'] div[role='radiogroup'] { gap:6px; }",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label {",
        "    background: transparent; border:1px solid transparent; border-radius:12px; padding:11px 14px !important;",
        "    transition: all 0.25s ease; width:100%;",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.10); }",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label p {",
        "    font-family:'Inter',sans-serif !important; font-weight:500 !important; font-size:0.9rem !important;",
        "    color:#B4C2D4 !important; letter-spacing:0.2px;",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label[data-checked='true'] {",
        "    background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(99,102,241,0.16));",
        "    border-color: rgba(56,189,248,0.4); box-shadow: inset 0 0 0 1px rgba(56,189,248,0.18);",
        "}",
        "section[data-testid='stSidebar'] div[role='radiogroup'] label[data-checked='true'] p { color:#F8FAFC !important; font-weight:600 !important; }",

        "button[data-baseweb='tab'] { font-family:'Inter',sans-serif; font-weight:500; color:#94A3B8 !important; }",
        "button[data-baseweb='tab'][aria-selected='true'] { color:#38BDF8 !important; }",
        "hr { border-color: rgba(255,255,255,0.10) !important; }",

        "</style>"
    ]
    st.markdown("\n".join(css_lines), unsafe_allow_html=True)


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
                    "latitude": item["lat"], "longitude": item["lon"],
                    "name": item.get("name", city_name), "country": item.get("country", "")
                }
    except Exception:
        pass
    return None

@st.cache_data(ttl=600)
def fetch_current_weather(lat, lon, api_key, units):
    url = (OWM_BASE + "/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) +
           "&units=" + str(units) + "&appid=" + str(api_key))
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=900)
def fetch_forecast(lat, lon, api_key, units):
    url = (OWM_BASE + "/data/2.5/forecast?lat=" + str(lat) + "&lon=" + str(lon) +
           "&units=" + str(units) + "&appid=" + str(api_key))
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
    mapping = {"01": "☀️", "02": "🌤️", "03": "⛅", "04": "☁️", "09": "🌧️",
               "10": "🌦️", "11": "🌩️", "13": "❄️", "50": "🌫️"}
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
def sync_active_city():
    """Callback bound to the search widget so the newest input is applied before rerun."""
    typed_city = st.session_state.get("city_input", "").strip()
    if typed_city:
        st.session_state["active_city"] = typed_city

def page_home():
    apply_custom_styles()

    st.markdown('<div class="hero-title">Weather Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Live meteorological intelligence, refined</div>', unsafe_allow_html=True)

    api_key = get_api_key()
    if not api_key:
        st.warning("Enter your free OpenWeatherMap API key in the sidebar to fetch live forecasts.")
        return

    st.session_state.setdefault("active_city", "Karachi")
    st.session_state.setdefault("city_input", st.session_state["active_city"])

    col_search, col_opts1, col_opts2, col_btn = st.columns([2.5, 1, 1, 1])
    with col_search:
        st.text_input("SEARCH CITY", key="city_input",
                       placeholder="e.g. Karachi, Tokyo, London, New York", on_change=sync_active_city)
    with col_opts1:
        unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"], key="unit_select")
    with col_opts2:
        speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"], key="speed_select")
    with col_btn:
        st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
        st.button("Search", on_click=sync_active_city, use_container_width=True)

    active_city = st.session_state.get("active_city", "Karachi").strip() or "Karachi"
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

    weather_category = get_weather_category(weather_block.get("id"))
    is_day = compute_is_day(current)
    local_time_str = get_local_time_str(current)
    render_dynamic_weather_background(weather_category, is_day, geo.get("name", active_city))
    svg_icon = get_weather_svg_icon(weather_category, is_day)

    t_curr = main_block.get("temp", 0.0)
    t_feels = main_block.get("feels_like", 0.0)
    humidity = main_block.get("humidity", 0)
    pressure = main_block.get("pressure", 0)
    visibility_km = current.get("visibility", 0) / 1000.0

    wind_spd = wind_block.get("speed", 0.0)
    if owm_units == "metric":
        wind_spd = wind_spd * 3.6
        if speed_unit == "m/s":
            wind_spd = wind_spd / 3.6
    else:
        wind_spd_kmh = wind_spd * 1.60934
        wind_spd = wind_spd_kmh if speed_unit == "km/h" else wind_spd_kmh / 3.6

    wind_dir = wind_direction_label(wind_block.get("deg"))
    uv_label = uv_risk_label(uv_value)
    uv_display = f"{uv_value:.1f}" if uv_value is not None else "N/A"
    day_night_label = "Day" if is_day else "Night"

    st.markdown("---")

    card_lines = [
        '<div class="glass-card">',
        '<div style="display:flex; align-items:center; gap:16px;">',
        svg_icon,
        '<h2 style="margin:0;">' + str(w_icon) + ' ' + str(city_full) + '</h2>',
        '</div>',
        '<p style="color:#94A3B8 !important; margin-top:8px; font-size:0.85rem; letter-spacing:0.3px;">COORDINATES · ' + f'{lat:.2f}' + '°N, ' + f'{lon:.2f}' + '°E &nbsp;·&nbsp; LOCAL TIME ' + str(local_time_str) + ' (' + str(day_night_label) + ')</p>',
        '<div class="temp-glow">' + f'{t_curr:.1f}' + ' ' + str(u_sym) + '<span class="unit-cond">' + str(w_desc) + '</span></div>',
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
    for entry in forecast_list[:8]:
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

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 24-Hour Temperature Trend")
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=h_times, y=h_temps, mode="lines+markers", name="Temp (" + str(u_sym) + ")",
        line=dict(color="#38BDF8", width=3, shape="spline"), marker=dict(size=5, color="#818CF8"),
        fill="tozeroy", fillcolor="rgba(56, 189, 233, 0.14)"
    ))
    fig_hourly.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94A3B8"),
        xaxis_title="Time of Day (3-hour steps)", yaxis_title="Temperature (" + str(u_sym) + ")",
        margin=dict(l=20, r=20, t=20, b=20), height=320
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 5-Day Extended Forecast")
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_max, name="Max Temp (" + str(u_sym) + ")", marker_color="#38BDF8"))
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_min, name="Min Temp (" + str(u_sym) + ")", marker_color="#4F46E5"))
    fig_daily.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94A3B8"), barmode="group",
        margin=dict(l=20, r=20, t=20, b=20), height=340
    )
    st.plotly_chart(fig_daily, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Tabular Breakdown")
    tab1, tab2 = st.tabs(["5-Day Daily Forecast Data", "Hourly Forecast Data (Next 24h)"])
    with tab1:
        st.dataframe({
            "Date": d_dates,
            "Condition": [str(d_icons[i]) + " " + str(d_conditions[i]) for i in range(len(d_dates))],
            "Max Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_max],
            "Min Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_min],
            "Rain Probability": [str(p) + "%" for p in d_rain],
            "Max Wind (" + str(speed_unit) + ")": [round(w, 1) for w in d_wind]
        }, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe({
            "Time": h_times,
            "Temperature (" + str(u_sym) + ")": [round(x, 1) for x in h_temps],
            "Humidity": [str(h) + "%" for h in h_humidity],
            "Rain Probability": [str(p) + "%" for p in h_rain]
        }, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Crafted by **Hafiz Muhammad Ubaid** · Powered by OpenWeatherMap")

# ---------------- PAGE: ABOUT ----------------
def page_about():
    apply_custom_styles()
    render_dynamic_weather_background("clear", True, "About")

    st.markdown('<div class="hero-title">About the Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Design philosophy &amp; technical overview</div>', unsafe_allow_html=True)

    about_lines = [
        '<div class="glass-card">',
        '<h2>Weather Forecast — Hafiz Muhammad Ubaid</h2>',
        '<p>Welcome to <b>Weather Forecast</b> — a modern, interactive weather tracking platform designed to offer high-precision, real-time meteorological insight for cities across the globe.</p>',
        '<hr>',
        '<h3>Advanced Features</h3>',
        '<ul>',
        '<li><b>Live MP4 Weather Backdrops:</b> A full-screen looping video matches the searched city\'s exact condition, with photo and gradient fallbacks so the UI never breaks.</li>',
        '<li><b>Seamless City Search:</b> Instantly toggle between multiple cities without refreshing the browser manually.</li>',
        '<li><b>Glassmorphic Interface:</b> Translucent, blurred cards keep every metric legible over a moving backdrop.</li>',
        '<li><b>Interactive Analytics:</b> Plotly-powered hourly and 5-day trend charts.</li>',
        '</ul>',
        '<hr>',
        '<h3>Developer</h3>',
        '<p>Designed and engineered by <b>Hafiz Muhammad Ubaid</b>.</p>',
        '</div>'
    ]
    st.markdown("".join(about_lines), unsafe_allow_html=True)

# ---------------- PAGE: CONTACT ----------------
def page_contact():
    apply_custom_styles()
    render_dynamic_weather_background("partly_cloudy", True, "Contact")

    st.markdown('<div class="hero-title">Connect</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Collaboration &amp; feedback channels</div>', unsafe_allow_html=True)

    email_address = "ubaidsajid2006@gmail.com"
    insta_link = "https://www.instagram.com/muhammadubaid__?stkn=eWV4ejI1MXh0Mndr&utm_source=qr"
    linkedin_link = "https://www.linkedin.com/in/muhammad-ubaid-2b88722b3?utm_source=share_via&utm_content=profile&utm_medium=member_ios"

    contact_lines = [
        '<div class="glass-card">',
        '<h2>Hafiz Muhammad Ubaid</h2>',
        '<p style="font-size:1.02rem; color:#94A3B8 !important;">Feel free to reach out for collaborations, feedback, or development inquiries.</p>',
        '<hr style="margin:22px 0;">',
        '<h3>Contact &amp; Social Profiles</h3>',
        '<p style="color:#64748B !important; font-size:0.88rem;">Click any icon below to email me or connect directly on my socials.</p>',
        '<div style="margin-top:22px; display:flex; align-items:center; gap:4px;">',
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
    page = st.sidebar.radio("Navigation", ["Home", "About", "Contact"], label_visibility="collapsed")

    if page == "Home":
        page_home()
    elif page == "About":
        page_about()
    else:
        page_contact()

if __name__ == "__main__":
    main()
