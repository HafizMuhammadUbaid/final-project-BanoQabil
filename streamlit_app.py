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

# ---------------- CUSTOM CSS & STYLING ----------------
DEFAULT_MESH_BG = (
    "linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)), "
    "linear-gradient(125deg, #0EA5E9 0%, #4F46E5 28%, #7C3AED 55%, #0F172A 80%, #030712 100%)"
)
DEFAULT_BG_COLOR = "#05070d"

def apply_custom_styles(background_css=None, bg_color=None, animate=True):
    background_css = background_css or DEFAULT_MESH_BG
    bg_color = bg_color or DEFAULT_BG_COLOR
    bg_size = "background-size: 320% 320% !important;" if animate else "background-size: cover !important;"
    bg_anim = "animation: gradientShift 18s ease infinite !important;" if animate else ""
    css_lines = [
        "<style>",
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@500;600;700;800&display=swap');",
        "@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');",

        # ---------- INPUT CONTRAST VARIABLES (WebView-safe: LinkedIn / WhatsApp / Safari / Chrome) ----------
        # These are resolved per prefers-color-scheme so the app is readable regardless of the
        # embedding container's own light/dark enforcement -- then applied with hard !important
        # overrides below so no host WebView stylesheet can silently repaint the fields.
        ":root {",
        "    --input-bg-light: #ffffff;",
        "    --input-text-light: #0f172a;",
        "    --input-border-light: rgba(15, 23, 42, 0.28);",
        "    --input-placeholder-light: #64748b;",
        "    --input-bg-dark: #111827;",
        "    --input-text-dark: #f8fafc;",
        "    --input-border-dark: rgba(255, 255, 255, 0.28);",
        "    --input-placeholder-dark: #94a3b8;",
        "    --input-bg: var(--input-bg-dark);",
        "    --input-text: var(--input-text-dark);",
        "    --input-border: var(--input-border-dark);",
        "    --input-placeholder: var(--input-placeholder-dark);",
        "}",
        "@media (prefers-color-scheme: light) {",
        "    :root {",
        "        --input-bg: var(--input-bg-light);",
        "        --input-text: var(--input-text-light);",
        "        --input-border: var(--input-border-light);",
        "        --input-placeholder: var(--input-placeholder-light);",
        "    }",
        "}",
        "@media (prefers-color-scheme: dark) {",
        "    :root {",
        "        --input-bg: var(--input-bg-dark);",
        "        --input-text: var(--input-text-dark);",
        "        --input-border: var(--input-border-dark);",
        "        --input-placeholder: var(--input-placeholder-dark);",
        "    }",
        "}",
        "html, body, .stApp {",
        "    color-scheme: light dark;",
        "}",

        # ---------- FULL-BLEED RESET (no default Streamlit white margins / empty gutters) ----------
        "html, body, #root {",
        "    margin: 0 !important;",
        "    padding: 0 !important;",
        "    height: 100% !important;",
        "}",
        ".block-container {",
        "    padding: 1.25rem 2.5rem 3rem 2.5rem !important;",
        "    max-width: 100% !important;",
        "}",
        "@media (max-width: 768px) {",
        "    .block-container { padding: 1rem 1rem 2rem 1rem !important; }",
        "}",

        # ---------- GLOBAL BACKDROP (dynamic photo OR rich animated CSS gradient) ----------
        "@keyframes gradientShift {",
        "    0% { background-position: 0% 50%; }",
        "    50% { background-position: 100% 50%; }",
        "    100% { background-position: 0% 50%; }",
        "}",
        ".stApp {",
        "    background: " + background_css + " !important;",
        "    background-color: " + bg_color + " !important;",
        "    background-attachment: fixed !important;",
        "    " + bg_size,
        "    " + bg_anim,
        "    background-position: center !important;",
        "    transition: background 0.8s ease-in-out, background-color 0.8s ease-in-out;",
        "    font-family: 'Inter', sans-serif;",
        "}",

        # ---------- CONTENT STACKING (keeps text/cards above the animated fx layer) ----------
        "[data-testid='stAppViewContainer'] {",
        "    position: relative;",
        "    z-index: 1;",
        "}",
        "section[data-testid='stSidebar'] {",
        "    z-index: 3 !important;",
        "}",

        # ---------- ANIMATED WEATHER FX LAYER (pure CSS, no images) ----------
        ".weather-fx {",
        "    position: fixed;",
        "    inset: 0;",
        "    z-index: 0;",
        "    pointer-events: none;",
        "    overflow: hidden;",
        "}",
        "@keyframes sunPulse {",
        "    0%, 100% { opacity: 0.55; transform: scale(1); }",
        "    50% { opacity: 0.9; transform: scale(1.08); }",
        "}",
        ".weather-fx.fx-sun {",
        "    background: radial-gradient(circle at 80% 16%, rgba(255,214,130,0.9) 0%, rgba(255,178,90,0.35) 18%, transparent 42%);",
        "    animation: sunPulse 6s ease-in-out infinite;",
        "}",
        "@keyframes twinkle {",
        "    0%, 100% { opacity: 0.3; }",
        "    50% { opacity: 0.95; }",
        "}",
        ".weather-fx.fx-stars {",
        "    background-image:",
        "        radial-gradient(1.4px 1.4px at 10% 20%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1px 1px at 30% 65%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1.8px 1.8px at 50% 15%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1px 1px at 70% 45%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1.4px 1.4px at 85% 75%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1px 1px at 15% 85%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1.8px 1.8px at 95% 30%, #ffffff 100%, transparent 100%),",
        "        radial-gradient(1px 1px at 60% 92%, #ffffff 100%, transparent 100%);",
        "    background-repeat: repeat;",
        "    background-size: 320px 320px;",
        "    opacity: 0.55;",
        "    animation: twinkle 4.5s ease-in-out infinite;",
        "}",
        "@keyframes rainFall {",
        "    0% { background-position: 0 0; }",
        "    100% { background-position: -60px 220px; }",
        "}",
        ".weather-fx.fx-rain {",
        "    background-image: repeating-linear-gradient(115deg, rgba(180,210,255,0.16) 0px, rgba(180,210,255,0.16) 1px, transparent 1px, transparent 15px);",
        "    background-size: 220% 220%;",
        "    animation: rainFall 0.6s linear infinite;",
        "}",
        ".weather-fx.fx-storm {",
        "    background-image: repeating-linear-gradient(115deg, rgba(190,215,255,0.26) 0px, rgba(190,215,255,0.26) 2px, transparent 2px, transparent 11px);",
        "    background-size: 220% 220%;",
        "    animation: rainFall 0.4s linear infinite;",
        "}",
        "@keyframes stormFlash {",
        "    0%, 91%, 100% { opacity: 0; }",
        "    92%, 95% { opacity: 0.35; }",
        "    93.5% { opacity: 0.05; }",
        "}",
        ".weather-fx.fx-storm::after {",
        "    content: '';",
        "    position: absolute;",
        "    inset: 0;",
        "    background: radial-gradient(circle at 50% 15%, rgba(255,255,255,0.9), transparent 60%);",
        "    animation: stormFlash 7s infinite;",
        "}",
        "@keyframes fogDrift {",
        "    0% { transform: translateX(-12%); }",
        "    50% { transform: translateX(12%); }",
        "    100% { transform: translateX(-12%); }",
        "}",
        ".weather-fx.fx-fog {",
        "    background: linear-gradient(90deg, transparent, rgba(200,230,225,0.16), transparent);",
        "    background-size: 200% 100%;",
        "    animation: fogDrift 14s ease-in-out infinite;",
        "}",
        "@keyframes snowFall {",
        "    0% { background-position: 0 0, 0 0, 0 0, 0 0; }",
        "    100% { background-position: 0 420px, 0 320px, 0 520px, 0 380px; }",
        "}",
        ".weather-fx.fx-snow {",
        "    background-image:",
        "        radial-gradient(2px 2px at 10% 0%, #ffffff, transparent),",
        "        radial-gradient(1.5px 1.5px at 40% 0%, #ffffff, transparent),",
        "        radial-gradient(2.4px 2.4px at 70% 0%, #ffffff, transparent),",
        "        radial-gradient(1.5px 1.5px at 90% 0%, #ffffff, transparent);",
        "    background-repeat: repeat-y;",
        "    background-size: 110px 420px, 150px 320px, 190px 520px, 130px 380px;",
        "    opacity: 0.7;",
        "    animation: snowFall 9s linear infinite;",
        "}",
        "@keyframes cloudDrift {",
        "    0% { transform: translateX(-6%); }",
        "    50% { transform: translateX(6%); }",
        "    100% { transform: translateX(-6%); }",
        "}",
        ".weather-fx.fx-clouds {",
        "    background:",
        "        radial-gradient(ellipse at 20% 30%, rgba(255,255,255,0.12), transparent 55%),",
        "        radial-gradient(ellipse at 70% 60%, rgba(255,255,255,0.08), transparent 60%);",
        "    animation: cloudDrift 18s ease-in-out infinite;",
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

        # ---------- NEON TEMPERATURE TYPOGRAPHY ----------
        ".temp-display {",
        "    font-family: 'Poppins', sans-serif;",
        "    font-size: 4.4rem;",
        "    font-weight: 800;",
        "    line-height: 1;",
        "    margin: 18px 0;",
        "    color: #F0F9FF !important;",
        "    letter-spacing: -1px;",
        "    text-shadow: 0 0 18px rgba(56,189,248,0.65), 0 0 42px rgba(56,189,248,0.35), 0 0 70px rgba(99,102,241,0.2);",
        "}",
        ".temp-condition {",
        "    font-size: 1.5rem;",
        "    font-weight: 400;",
        "    color: #E2E8F0 !important;",
        "    text-shadow: none;",
        "}",

        # ---------- LARGE DYNAMIC WEATHER ICON (Font Awesome, glowing) ----------
        ".weather-icon-large {",
        "    font-size: 5.2rem;",
        "    display: inline-block;",
        "    margin-right: 20px;",
        "    vertical-align: middle;",
        "    filter: drop-shadow(0 0 18px var(--icon-glow, rgba(56,189,248,0.55)));",
        "    animation: iconFloat 4.5s ease-in-out infinite;",
        "}",
        "@keyframes iconFloat {",
        "    0%, 100% { transform: translateY(0px); }",
        "    50% { transform: translateY(-8px); }",
        "}",

        # ---------- GLASSMORPHIC CARD (exact spec values) ----------
        ".glass-card {",
        "    background: rgba(255, 255, 255, 0.08);",
        "    backdrop-filter: blur(12px) saturate(160%);",
        "    -webkit-backdrop-filter: blur(12px) saturate(160%);",
        "    border: 1px solid rgba(255, 255, 255, 0.15);",
        "    border-radius: 16px;",
        "    padding: 32px;",
        "    margin-bottom: 26px;",
        "    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 1px 0 0 rgba(255,255,255,0.08);",
        "    transition: transform 0.35s cubic-bezier(.2,.8,.2,1), border-color 0.35s ease, box-shadow 0.35s ease;",
        "}",
        ".glass-card:hover {",
        "    border-color: rgba(56, 189, 248, 0.45);",
        "    box-shadow: 0 14px 40px 0 rgba(0,0,0,0.4), 0 0 0 1px rgba(56,189,248,0.10);",
        "}",

        # ---------- FORM / INPUT CONTAINER (same translucent dark glass language) ----------
        "div[data-testid='stForm'] {",
        "    background: rgba(255, 255, 255, 0.08) !important;",
        "    backdrop-filter: blur(12px);",
        "    border: 1px solid rgba(255, 255, 255, 0.15) !important;",
        "    border-radius: 16px !important;",
        "    padding: 26px !important;",
        "    box-shadow: 0 6px 24px rgba(0,0,0,0.30);",
        "}",

        # ---------- INPUT / SELECT FIELDS (WebView-safe: solid fallback color + blur as enhancement) ----------
        # A SOLID var(--input-bg) is painted first so contrast holds even if backdrop-filter is
        # unsupported/ignored (this is what breaks inside LinkedIn's in-app browser). The subtle
        # translucent tint + blur is layered ON TOP only where the browser actually supports it.
        "div[data-baseweb='select'] > div, .stTextInput div[data-baseweb='base-input'], .stTextInput input {",
        "    background-color: var(--input-bg) !important;",
        "    border: 1px solid var(--input-border) !important;",
        "    border-radius: 12px !important;",
        "    color: var(--input-text) !important;",
        "    -webkit-text-fill-color: var(--input-text) !important;",
        "    caret-color: var(--input-text) !important;",
        "    transition: border-color 0.25s ease, box-shadow 0.25s ease;",
        "}",
        "@supports ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {",
        "    div[data-baseweb='select'] > div, .stTextInput div[data-baseweb='base-input'] {",
        "        background-color: rgba(255,255,255,0.08) !important;",
        "        backdrop-filter: blur(10px);",
        "        -webkit-backdrop-filter: blur(10px);",
        "    }",
        "}",
        "div[data-baseweb='select'] > div * {",
        "    color: var(--input-text) !important;",
        "    -webkit-text-fill-color: var(--input-text) !important;",
        "}",
        ".stTextInput input::placeholder {",
        "    color: var(--input-placeholder) !important;",
        "    -webkit-text-fill-color: var(--input-placeholder) !important;",
        "    opacity: 1 !important;",
        "}",
        ".stTextInput input:focus {",
        "    border-color: rgba(56, 189, 248, 0.6) !important;",
        "    box-shadow: 0 0 0 3px rgba(56, 189, 233, 0.18) !important;",
        "}",
        # Chromium/WebKit autofill repaints fields with its own white/yellow background + dark
        # text the instant a value is remembered -- this is a common invisible-text trigger too.
        ".stTextInput input:-webkit-autofill,",
        ".stTextInput input:-webkit-autofill:hover,",
        ".stTextInput input:-webkit-autofill:focus {",
        "    -webkit-text-fill-color: var(--input-text) !important;",
        "    -webkit-box-shadow: 0 0 0px 1000px var(--input-bg) inset !important;",
        "    box-shadow: 0 0 0px 1000px var(--input-bg) inset !important;",
        "    caret-color: var(--input-text) !important;",
        "    transition: background-color 9999s ease-in-out 0s;",
        "}",
        # Dropdown popover/menu list (the open options list for the unit/wind selects) renders in
        # a detached portal, so it needs its own explicit contrast rules too.
        "div[data-baseweb='popover'] ul, div[data-baseweb='popover'] li, div[data-baseweb='menu'] {",
        "    background-color: var(--input-bg) !important;",
        "    color: var(--input-text) !important;",
        "}",
        "div[data-baseweb='popover'] li:hover, div[data-baseweb='popover'] li[aria-selected='true'] {",
        "    background-color: rgba(56, 189, 248, 0.18) !important;",
        "    color: var(--input-text) !important;",
        "}",
        "label[data-testid='stWidgetLabel'] p {",
        "    font-size: 0.72rem !important;",
        "    font-weight: 600 !important;",
        "    letter-spacing: 1px !important;",
        "    text-transform: uppercase;",
        "    color: #94A3B8 !important;",
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
        "    background: rgba(255, 255, 255, 0.08);",
        "    backdrop-filter: blur(8px);",
        "    color: #7DD3FC !important;",
        "    border: 1px solid rgba(255, 255, 255, 0.15);",
        "    margin-right: 10px;",
        "    margin-bottom: 10px;",
        "    letter-spacing: 0.2px;",
        "}",

        # ---------- FULL-BLEED LAYOUT (kill default Streamlit whitespace) ----------
        ".block-container {",
        "    padding-top: 2rem !important;",
        "    padding-bottom: 2rem !important;",
        "    padding-left: 3rem !important;",
        "    padding-right: 3rem !important;",
        "    max-width: 100% !important;",
        "}",
        "[data-testid='stAppViewContainer'] > .main {",
        "    padding: 0 !important;",
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

# ---------------- DYNAMIC WEATHER BACKGROUND (pure CSS mesh gradients, zero hardcoded image IDs) ----------------

# 7 granular condition categories, each resolved from OpenWeatherMap's precise
# numeric weather-condition "id" (far more specific than the coarse "main" string).
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

    if 200 <= wid <= 232:                       # thunderstorm family
        return "heavy_rain"
    if 300 <= wid <= 321:                        # drizzle family
        return "light_rain"
    if wid in (500, 501, 520, 521):              # light / moderate rain & showers
        return "light_rain"
    if wid in (502, 503, 504, 511, 522, 531):     # heavy / violent / freezing rain
        return "heavy_rain"
    if 600 <= wid <= 622:                        # snow family
        return "snow"
    if wid in (771, 781):                        # squall / tornado -> severe
        return "heavy_rain"
    if 701 <= wid <= 762:                         # mist, smoke, haze, dust, fog, sand, ash
        return "fog"
    if wid == 800:                                # clear sky
        return "clear"
    if wid in (801, 802):                         # few / scattered clouds
        return "partly_cloudy"
    if wid in (803, 804):                         # broken / overcast clouds
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

# Rich, multi-layer CSS mesh gradient per category + day/night (14 unique looks, zero images required).
# Each entry: "gradient" (the visual), "bg_color" (opaque safety-net fallback), "fx" (animated overlay
# class), and "keywords" (kept for reference/labeling only).
CATEGORY_THEMES = {
    "clear": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 82% 12%, rgba(255,196,90,0.95) 0%, rgba(255,170,70,0.55) 20%, transparent 48%), "
                "radial-gradient(circle at 15% 85%, rgba(56,189,248,0.40) 0%, transparent 55%), "
                "linear-gradient(160deg, rgba(56,130,214,0.65) 0%, rgba(20,40,80,0.72) 100%)"
            ),
            "bg_color": "#0b2340", "fx": "fx-sun", "keywords": "sunny,blue,sky",
            "accent": ("255,180,90", "56,189,248"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(129,49,207,0.65) 0%, transparent 52%), "
                "radial-gradient(circle at 20% 70%, rgba(56,90,220,0.45) 0%, transparent 58%), "
                "linear-gradient(180deg, rgba(15,15,45,0.75) 0%, rgba(4,4,15,0.88) 100%)"
            ),
            "bg_color": "#04050d", "fx": "fx-stars", "keywords": "night,stars,sky",
            "accent": ("129,49,207", "56,90,220"),
        },
    },
    "partly_cloudy": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 75% 20%, rgba(255,220,150,0.55) 0%, transparent 42%), "
                "radial-gradient(circle at 20% 80%, rgba(96,165,250,0.30) 0%, transparent 55%), "
                "linear-gradient(150deg, rgba(96,140,190,0.60) 0%, rgba(25,38,68,0.78) 100%)"
            ),
            "bg_color": "#101d33", "fx": "fx-clouds", "keywords": "clouds,sky,day",
            "accent": ("255,220,150", "96,165,250"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 30% 20%, rgba(148,163,184,0.35) 0%, transparent 48%), "
                "radial-gradient(circle at 80% 70%, rgba(99,102,241,0.25) 0%, transparent 55%), "
                "linear-gradient(160deg, rgba(30,38,66,0.72) 0%, rgba(8,10,20,0.85) 100%)"
            ),
            "bg_color": "#080b14", "fx": "fx-clouds", "keywords": "clouds,night,sky",
            "accent": ("148,163,184", "99,102,241"),
        },
    },
    "overcast": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(148,163,184,0.45) 0%, transparent 58%), "
                "radial-gradient(circle at 85% 90%, rgba(100,116,139,0.30) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(71,85,105,0.65) 0%, rgba(20,26,40,0.82) 100%)"
            ),
            "bg_color": "#0d1119", "fx": "fx-clouds", "keywords": "overcast,grey,sky",
            "accent": ("148,163,184", "71,85,105"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(100,116,139,0.35) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(24,29,45,0.78) 0%, rgba(6,7,14,0.90) 100%)"
            ),
            "bg_color": "#040508", "fx": "fx-clouds", "keywords": "overcast,night",
            "accent": ("100,116,139", "51,65,85"),
        },
    },
    "light_rain": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 70% 10%, rgba(96,165,250,0.45) 0%, transparent 50%), "
                "radial-gradient(circle at 20% 90%, rgba(45,212,191,0.20) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(37,80,130,0.68) 0%, rgba(10,18,32,0.82) 100%)"
            ),
            "bg_color": "#081019", "fx": "fx-rain", "keywords": "rain,drizzle,city",
            "accent": ("96,165,250", "45,212,191"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 30% 10%, rgba(59,130,246,0.35) 0%, transparent 50%), "
                "linear-gradient(165deg, rgba(12,20,38,0.78) 0%, rgba(3,5,12,0.90) 100%)"
            ),
            "bg_color": "#020409", "fx": "fx-rain", "keywords": "rain,night,city",
            "accent": ("59,130,246", "14,116,144"),
        },
    },
    "heavy_rain": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(99,102,241,0.35) 0%, transparent 58%), "
                "radial-gradient(circle at 80% 85%, rgba(139,92,246,0.22) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(30,35,58,0.75) 0%, rgba(6,7,14,0.88) 100%)"
            ),
            "bg_color": "#020308", "fx": "fx-storm", "keywords": "thunderstorm,dark,rain",
            "accent": ("99,102,241", "139,92,246"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 50% 10%, rgba(76,29,149,0.45) 0%, transparent 52%), "
                "linear-gradient(165deg, rgba(14,12,30,0.82) 0%, rgba(2,2,6,0.92) 100%)"
            ),
            "bg_color": "#010104", "fx": "fx-storm", "keywords": "thunderstorm,night,lightning",
            "accent": ("76,29,149", "49,46,129"),
        },
    },
    "snow": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(226,232,240,0.55) 0%, transparent 58%), "
                "radial-gradient(circle at 80% 80%, rgba(125,211,252,0.25) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(148,163,184,0.55) 0%, rgba(24,33,54,0.75) 100%)"
            ),
            "bg_color": "#0c1424", "fx": "fx-snow", "keywords": "snow,winter,day",
            "accent": ("226,232,240", "125,211,252"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 50% 0%, rgba(148,163,184,0.32) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(22,30,50,0.75) 0%, rgba(6,9,18,0.88) 100%)"
            ),
            "bg_color": "#04060e", "fx": "fx-snow", "keywords": "snow,winter,night",
            "accent": ("148,163,184", "71,85,105"),
        },
    },
    "fog": {
        "day": {
            "gradient": (
                "radial-gradient(circle at 50% 30%, rgba(45,212,191,0.30) 0%, transparent 58%), "
                "radial-gradient(circle at 85% 70%, rgba(94,234,212,0.20) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(71,85,105,0.55) 0%, rgba(20,28,42,0.78) 100%)"
            ),
            "bg_color": "#0b1420", "fx": "fx-fog", "keywords": "fog,mist,teal",
            "accent": ("45,212,191", "94,234,212"),
        },
        "night": {
            "gradient": (
                "radial-gradient(circle at 50% 30%, rgba(45,212,191,0.20) 0%, transparent 55%), "
                "linear-gradient(165deg, rgba(14,20,32,0.78) 0%, rgba(4,7,14,0.90) 100%)"
            ),
            "bg_color": "#03050a", "fx": "fx-fog", "keywords": "fog,night,mist",
            "accent": ("45,212,191", "20,83,45"),
        },
    },
}

def resolve_weather_theme(category, is_day):
    """Return the full theme dict (gradient, bg_color, fx class, accent colors) for a granular weather category."""
    variant = "day" if is_day else "night"
    group = CATEGORY_THEMES.get(category, CATEGORY_THEMES["clear"])
    return group.get(variant, group["day"])

# Font Awesome (already loaded via CDN import) icon per category + day/night -- real vector icons, zero image risk
WEATHER_ICON_CLASS = {
    ("clear", True): "fa-solid fa-sun",
    ("clear", False): "fa-solid fa-moon",
    ("partly_cloudy", True): "fa-solid fa-cloud-sun",
    ("partly_cloudy", False): "fa-solid fa-cloud-moon",
    ("overcast", True): "fa-solid fa-cloud",
    ("overcast", False): "fa-solid fa-cloud",
    ("light_rain", True): "fa-solid fa-cloud-rain",
    ("light_rain", False): "fa-solid fa-cloud-rain",
    ("heavy_rain", True): "fa-solid fa-cloud-bolt",
    ("heavy_rain", False): "fa-solid fa-cloud-bolt",
    ("snow", True): "fa-solid fa-snowflake",
    ("snow", False): "fa-solid fa-snowflake",
    ("fog", True): "fa-solid fa-smog",
    ("fog", False): "fa-solid fa-smog",
}

def get_weather_icon_class(category, is_day):
    return WEATHER_ICON_CLASS.get((category, is_day), "fa-solid fa-cloud")

def apply_dynamic_weather_background(category, is_day):
    """
    Paints the page with a rich, ANIMATED CSS gradient mesh tuned to the exact weather
    category and local day/night state -- always dynamic, no external photo dependency.
    Also stores the active category/day-night state in session_state so every other
    page in the app can reproduce the exact same background.
    """
    st.session_state["bg_weather_category"] = category
    st.session_state["bg_is_day"] = is_day

    theme = resolve_weather_theme(category, is_day)
    dark_overlay = "linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45))"
    full_background = dark_overlay + ", " + theme["gradient"]
    size_css = "background-size: 320% 320% !important;"
    anim_css = "animation: gradientShift 16s ease infinite !important;"

    st.markdown(
        "<style>.stApp { "
        "background: " + full_background + " !important; "
        "background-color: " + theme["bg_color"] + " !important; "
        "background-attachment: fixed !important; "
        + size_css + " "
        + anim_css + " "
        "background-position: center !important; "
        "transition: background 0.8s ease-in-out; "
        "}</style>",
        unsafe_allow_html=True
    )
    st.markdown('<div class="weather-fx ' + theme["fx"] + '"></div>', unsafe_allow_html=True)

def apply_active_weather_background():
    """
    Re-applies whichever weather background was last computed on the Home page
    (stored in session_state), so the About and Contact pages show the exact same
    live, dynamic background instead of the generic default mesh. Falls back to a
    clear-sky daytime theme before any city has ever been searched.
    """
    category = st.session_state.get("bg_weather_category", "clear")
    is_day = st.session_state.get("bg_is_day", True)
    apply_dynamic_weather_background(category, is_day)




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
def sync_active_city():
    """
    Callback bound to the search widget's on_change/on_click.
    Runs BEFORE the rerun that redraws the page, so by the time page_home()
    executes, st.session_state['active_city'] already reflects the newest
    input -- no stale weather data, no manual reset step required.
    """
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

    # Initialize session state exactly once -- never pass value= on the widget itself,
    # since the widget's own key already owns that slot in session_state.
    st.session_state.setdefault("active_city", "Karachi")
    st.session_state.setdefault("city_input", st.session_state["active_city"])

    col_search, col_opts1, col_opts2, col_btn = st.columns([2.5, 1, 1, 1])

    with col_search:
        st.text_input(
            "SEARCH CITY",
            key="city_input",
            placeholder="e.g. Karachi, Tokyo, London, New York",
            on_change=sync_active_city,
        )

    with col_opts1:
        unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"], key="unit_select")

    with col_opts2:
        speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"], key="speed_select")

    with col_btn:
        st.markdown('<div style="height: 26px;"></div>', unsafe_allow_html=True)
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

    # Precise category + strict local-time day/night check for this exact city, then paint the background
    weather_category = get_weather_category(weather_block.get("id"))
    is_day = compute_is_day(current)
    local_time_str = get_local_time_str(current)
    apply_dynamic_weather_background(weather_category, is_day)

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
    day_night_label = "Day" if is_day else "Night"

    icon_class = get_weather_icon_class(weather_category, is_day)
    active_theme = resolve_weather_theme(weather_category, is_day)
    accent_glow = "rgba(" + active_theme["accent"][0] + ",0.6)"

    st.markdown("---")

    card_lines = [
        '<div class="glass-card">',
        '<div style="display:flex; align-items:center; gap:28px; flex-wrap:wrap;">',
        '<i class="' + str(icon_class) + ' weather-icon-large" style="--icon-glow:' + accent_glow + ';"></i>',
        '<div style="flex:1; min-width:220px;">',
        '<h2 style="margin-bottom:0px;">' + str(city_full) + '</h2>',
        '<p style="color:#64748B !important; margin-top:4px; font-size:0.85rem; letter-spacing:0.3px;">COORDINATES · ' + f'{lat:.2f}' + '°N, ' + f'{lon:.2f}' + '°E &nbsp;·&nbsp; LOCAL TIME ' + str(local_time_str) + ' (' + str(day_night_label) + ')</p>',
        '<div class="temp-display">' + f'{t_curr:.1f}' + ' ' + str(u_sym) + ' <span class="temp-condition">' + str(w_desc) + '</span></div>',
        '</div>',
        '</div>',
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
    apply_custom_styles()
    apply_active_weather_background()

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
    apply_custom_styles()
    apply_active_weather_background()

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
