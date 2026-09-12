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
    css_code = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@500;700;800&display=swap');

    /* Main Container Background */
    .stApp {{
        background: linear-gradient(rgba(10, 15, 29, 0.78), rgba(10, 15, 29, 0.88)), url("{bg_url}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        font-family: 'Inter', sans-serif;
    }}

    /* Headings & Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif !important;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }}

    p, label, span, div {{
        color: #E2E8F0 !important;
    }}

    /* Glassmorphism Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    /* Custom Button */
    .stButton > button {{
        width: 100%;
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
        color: #FFFFFF !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, #38BDF8 0%, #1D4ED8 100%);
        transform: translateY(-2px);
    }}

    /* Streamlit Metric Box Override */
    div[data-testid="stMetric"] {{
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px 20px;
        border-radius: 14px;
    }}

    div[data-testid="stMetricValue"] {{
        font-family: 'Poppins', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
    }}

    /* Custom Badges */
    .badge {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-right: 8px;
        margin-bottom: 8px;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

# ---------------- API HELPER FUNCTIONS ----------------
@st.cache_data(ttl=1800)
def geocode_city(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            return results[0]
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
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
        return res.json()
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

    col_search, col_opts1, col_opts2 = st.columns([2.5, 1, 1])

    with col_search:
        city_input = st.text_input("SEARCH CITY", placeholder="e.g. Karachi, Tokyo, London, New York")

    with col_opts1:
        unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"])

    with col_opts2:
        speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"])

    if st.button("GET METEOROLOGICAL FORECAST"):
        if city_input.strip():
            st.session_state["active_city"] = city_input.strip()
        else:
            st.warning("Please enter a valid city name.")

    active_city = st.session_state.get("active_city", None)
    if not active_city:
        st.info("💡 Enter a city name above to load live meteorological data.")
        return

    with st.spinner(f"Fetching data for {active_city}..."):
        geo = geocode_city(active_city)
        if not geo:
            st.error(f"Could not find coordinates for '{active_city}'. Please check the city name.")
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
    
    card_html = f"""
    <div class="glass-card">
        <h2 style="margin-bottom:0px;">{w_icon} {city_full}</h2>
        <p style="color:#94A3B8 !important; margin-top:2px;">Coordinates: {lat:.2f}°N, {lon:.2f}°E</p>
        <h1 style="font-size: 3.5rem; margin: 10px 0;">{round(t_curr, 1)} {u_sym} <span style="font-size:1.5rem; font-weight:400; color:#94A3B8 !important;">({w_desc})</span></h1>
        <div>
            <span class="badge">Feels Like: {round(t_feels, 1)} {u_sym}</span>
            <span class="badge">Humidity: {curr['relative_humidity_2m']}%</span>
            <span class="badge">Wind: {round(wind_spd, 1)} {speed_unit}</span>
            <span class="badge">Pressure: {curr['surface_pressure']} hPa</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Hourly Graph
    st.markdown("### 📈 24-Hour Temperature Trend")
    hourly = weather["hourly"]
    h_times = [datetime.datetime.fromisoformat(t).strftime("%H:00") for t in hourly["time"][:24]]
    h_temps = hourly["temperature_2m"][:24]

    if "Fahrenheit" in unit:
        h_temps = [(t * 1.8) + 32 for t in h_temps]

    fig_hourly = go.Figure()
    fig_hourly.add_trace(
        go.Scatter(
            x=h_times,
            y=h_temps,
            mode="lines+markers",
            name=f"Temp ({u_sym})",
            line=dict(color="#0EA5E9", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(14, 165, 233, 0.15)"
        )
    )
    fig_hourly.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Time of Day",
        yaxis_title=f"Temperature ({u_sym})",
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    # 7-Day Forecast
    st.markdown("### 🗓️ 7-Day Extended Forecast")
    daily = weather["daily"]
    d_dates = [datetime.datetime.fromisoformat(d).strftime("%a, %b %d") for d in daily["time"]]
    d_max = daily["temperature_2m_max"]
    d_min = daily["temperature_2m_min"]

    if "Fahrenheit" in unit:
        d_max = [(t * 1.8) + 32 for t in d_max]
        d_min = [(t * 1.8) + 32 for t in d_min]

    d_codes = [decode_wmo_code(c) for c in daily["weather_code"]]
    d_conditions = [c[0] for c in d_codes]
    d_icons = [c[1] for c in d_codes]

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_max, name=f"Max Temp ({u_sym})", marker_color="#38BDF8"))
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_min, name=f"Min Temp ({u_sym})", marker_color="#1E40AF"))
    
    fig_daily.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="group",
        margin=dict(l=20, r=20, t=20, b=20),
        height=340
    )
    st.plotly_chart(fig_daily, use_container_width=True)

    # Tabular Breakdown
    st.markdown("### 📊 Tabular Breakdown")
    tab1, tab2 = st.tabs(["7-Day Daily Forecast Data", "Hourly Forecast Data (Next 24h)"])

    with tab1:
        st.dataframe(
            {
                "Date": d_dates,
                "Condition": [f"{d_icons[i]} {d_conditions[i]}" for i in range(len(d_dates))],
                f"Max Temp ({u_sym})": [round(x, 1) for x in d_max],
                f"Min Temp ({u_sym})": [round(x, 1) for x in d_min],
                "Rain Probability": [f"{p}%" for p in daily["precipitation_probability_max"]],
                f"Max Wind ({speed_unit})": [round(w if speed_unit == "km/h" else w / 3.6, 1) for w in daily["wind_speed_10m_max"]]
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            {
                "Time": h_times,
                f"Temperature ({u_sym})": [round(x, 1) for x in h_temps],
                "Humidity": [f"{h}%" for h in hourly["relative_humidity_2m"][:24]],
                "Rain Probability": [f"{p}%" for p in hourly["precipitation_probability"][:24]]
            },
            use_container_width=True,
            hide_index=True
        )

    st.caption("Crafted by **Hafiz Muhammad Ubaid** | Powered by Open-Meteo Meteorological API")

# ---------------- PAGE: ABOUT ----------------
def page_about():
    apply_custom_styles("https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1920&q=80")

    st.title("📜 ABOUT THE PROJECT")
    st.markdown(
        """
        <div class="glass-card">
            <h2>WEATHER FORECAST BY HMU ✪</h2>
            <p>Welcome to <b>WEATHER FORECAST BY HMU ✪</b> — a modern, interactive weather tracking platform designed to offer high-precision, real-time meteorological insight for cities across the globe.</p>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <h3>🚀 Advanced Features</h3>
            <ul>
                <li><b>Zero API Keys Required:</b> Powered by Open-Meteo's open-source meteorological API.</li>
                <li><b>Global City Geocoding:</b> Auto-detects coordinates for any city worldwide.</li>
                <li><b>Interactive Data Visuals:</b> Glassmorphism UI rendered with Plotly analytics charts.</li>
                <li><b>Comprehensive Metrics:</b> Feels like temperature, surface pressure, humidity, wind speeds, and precipitation probabilities.</li>
            </ul>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <h3>👨‍💻 Developer</h3>
            <p>Designed and built by <b>Hafiz Muhammad Ubaid</b>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- PAGE: CONTACT ----------------
def page_contact():
    apply_custom_styles("https://images.unsplash.com/photo-1516912481808-3406841bd33c?auto=format&fit=crop&w=1920&q=80")

    st.title("📩 CONNECT WITH ME")
    st.markdown(
        """
        <div class="glass-card">
            <h2>Hafiz Muhammad Ubaid</h2>
            <p>Feel free to reach out for collaborations, feedback, or development inquiries!</p>
            <br>
            <p><b>📧 Email:</b> <a href="mailto:ubaidsajid2006@gmail.com" style="color:#38BDF8;">ubaidsajid2006@gmail.com</a></p>
            <p><b>📸 Instagram:</b> <a href="https://instagram.com/muhammadubaid__" target="_blank" style="color:#38BDF8;">@muhammadubaid__</a></p>
            <p><b>💼 LinkedIn:</b> Hafiz Muhammad Ubaid</p>
            <p><b>💻 GitHub:</b> Muhammad Ubaid</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- MAIN ROUTER ----------------
def main():
    st.sidebar.title("☰ NAVIGATION")
    page = st.sidebar.radio("Navigate to", ["Home", "About", "Contact"])

    try:
        st.sidebar.image("icc.jpg", use_container_width=True)
    except Exception:
        pass

    if page == "Home":
        page_home()
    elif page == "About":
        page_about()
    else:
        page_contact()

if __name__ == "__main__":
    main()
