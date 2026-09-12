import streamlit as st
import datetime
import requests
from plotly import graph_objects as go

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="WEATHER FORECAST BY HMU ✪",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS & STYLING ----------------
def apply_custom_styles(bg_url):
    css_code = """
    
    """.format(bg_url=bg_url)
    st.markdown(css_code, unsafe_allow_html=True)

# ---------------- API HELPER FUNCTIONS ----------------
@st.cache_data(ttl=1800)
def geocode_city(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                return results[0]
    except Exception:
        pass
    return None

@st.cache_data(ttl=900)
def fetch_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m"
        "&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max"
        "&timezone=auto"
    )
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def decode_wmo_code(code):
    mapping = {
        0: ("Clear Sky", "☀️"),
        1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        48: ("Depositing Rime Fog", "🌫️"),
        51: ("Light Drizzle", "🌦️"),
        53: ("Moderate Drizzle", "🌧️"),
        55: ("Dense Drizzle", "🌧️"),
        61: ("Slight Rain", "🌧️"),
        63: ("Moderate Rain", "🌧️"),
        65: ("Heavy Rain", "⛈️"),
        71: ("Slight Snow", "🌨️"),
        73: ("Moderate Snow", "❄️"),
        75: ("Heavy Snow", "❄️"),
        80: ("Rain Showers", "🌦️"),
        81: ("Moderate Rain Showers", "🌧️"),
        82: ("Violent Rain Showers", "⛈️"),
        95: ("Thunderstorm", "🌩️"),
        96: ("Thunderstorm with Hail", "⛈️"),
    }
    return mapping.get(code, ("Unknown", "🌡️"))

# ---------------- PAGE: HOME ----------------
def page_home():
    apply_custom_styles("https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1920&q=80")

    st.title("WEATHER FORECAST ⚡")

    with st.form(key="search_form"):
        col_search, col_opts1, col_opts2 = st.columns([2.5, 1, 1])

        with col_search:
            default_city = st.session_state.get("active_city", "Karachi")
            city_input = st.text_input("SEARCH CITY", value=default_city, placeholder="e.g. Karachi, Tokyo, London, New York")

        with col_opts1:
            unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"])

        with col_opts2:
            speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"])

        submit_btn = st.form_submit_button("GET METEOROLOGICAL FORECAST 🔍")

    if submit_btn:
        if city_input.strip():
            st.session_state["active_city"] = city_input.strip()
        else:
            st.warning("Please enter a valid city name.")

    active_city = st.session_state.get("active_city", "Karachi")

    with st.spinner(f"Fetching live data for {active_city}..."):
        geo = geocode_city(active_city)
        if not geo:
            st.error(f"Could not find coordinates for '{active_city}'. Please enter a valid city name.")
            return

        lat, lon = geo["latitude"], geo["longitude"]
        city_full = f"{geo['name']}, {geo.get('country', '')}"
        weather = fetch_weather_data(lat, lon)

        if not weather:
            st.error("Unable to retrieve weather details from meteorological servers.")
            return

    curr = weather["current"]
    w_desc, w_icon = decode_wmo_code(curr["weather_code"])
    
    t_curr = curr["temperature_2m"]
    t_feels = curr["apparent_temperature"]
    
    if "Fahrenheit" in unit:
        t_curr = (t_curr * 1.8) + 32
        t_feels = (t_feels * 1.8) + 32
        u_sym = "°F"
    else:
        u_sym = "°C"

    wind_spd = curr["wind_speed_10m"]
    if speed_unit == "m/s":
        wind_spd = wind_spd / 3.6
    
    st.markdown("---")

    card_html = """
