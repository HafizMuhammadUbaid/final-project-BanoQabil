import streamlit as st
import datetime
import requests
from plotly import graph_objects as go

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="WEATHER FORECAST BY HAFIZ MUHAMMAD UBAID ✪",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS & STYLING ----------------
def apply_custom_styles(bg_url):
    css_lines = [
        "<style>",
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@500;700;800;900&display=swap');",
        "@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');",
        
        "# Main Background",
        ".stApp {",
        "    background: linear-gradient(rgba(10, 15, 29, 0.88), rgba(10, 15, 29, 0.95)), url('" + bg_url + "');",
        "    background-attachment: fixed;",
        "    background-size: cover;",
        "    background-position: center;",
        "    font-family: 'Inter', sans-serif;",
        "}",
        
        "# Sidebar Styling",
        "section[data-testid='stSidebar'] {",
        "    background: rgba(10, 15, 29, 0.95) !important;",
        "    border-right: 1px solid rgba(255, 255, 255, 0.08);",
        "}",
        "div[data-testid='stSidebarUserContent'] {",
        "    padding-top: 1.5rem;",
        "}",
        
        "# Luxury Navigation Radio Buttons",
        "div[role='radiogroup'] {",
        "    gap: 14px;",
        "}",
        "div[role='radiogroup'] label {",
        "    background: rgba(255, 255, 255, 0.04) !important;",
        "    border: 1px solid rgba(255, 255, 255, 0.1) !important;",
        "    border-radius: 16px !important;",
        "    padding: 16px 20px !important;",
        "    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;",
        "    cursor: pointer !important;",
        "    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;",
        "}",
        "div[role='radiogroup'] label:hover {",
        "    background: rgba(56, 189, 248, 0.15) !important;",
        "    border-color: rgba(56, 189, 248, 0.5) !important;",
        "    transform: translateX(4px);",
        "}",
        "div[role='radiogroup'] label[data-checked='true'] {",
        "    background: linear-gradient(135deg, rgba(14, 165, 233, 0.35) 0%, rgba(37, 99, 235, 0.35) 100%) !important;",
        "    border-color: #38BDF8 !important;",
        "    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3) !important;",
        "}",
        "div[role='radiogroup'] label span {",
        "    font-family: 'Poppins', sans-serif !important;",
        "    font-weight: 700 !important;",
        "    font-size: 1.05rem !important;",
        "    letter-spacing: 0.8px !important;",
        "    color: #FFFFFF !important;",
        "}",

        "# Header Branding",
        ".main-header-box {",
        "    text-align: left;",
        "    padding: 10px 0 20px 0;",
        "    margin-bottom: 20px;",
        "}",
        ".main-title {",
        "    font-family: 'Poppins', sans-serif !important;",
        "    font-weight: 900 !important;",
        "    font-size: 2.8rem !important;",
        "    letter-spacing: 2px !important;",
        "    background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 50%, #2563EB 100%);",
        "    -webkit-background-clip: text;",
        "    -webkit-text-fill-color: transparent;",
        "    margin: 0 !important;",
        "    text-transform: uppercase;",
        "}",
        ".main-subtitle {",
        "    font-family: 'Poppins', sans-serif !important;",
        "    font-size: 1rem !important;",
        "    font-weight: 500 !important;",
        "    color: #94A3B8 !important;",
        "    margin-top: 2px !important;",
        "    letter-spacing: 1px !important;",
        "}",

        "# Glass Cards Styling",
        "h1, h2, h3, h4, h5, h6 {",
        "    font-family: 'Poppins', sans-serif !important;",
        "    color: #FFFFFF !important;",
        "}",
        "p, label, span, div {",
        "    color: #E2E8F0 !important;",
        "}",
        ".glass-card {",
        "    background: rgba(255, 255, 255, 0.04);",
        "    backdrop-filter: blur(20px);",
        "    -webkit-backdrop-filter: blur(20px);",
        "    border: 1px solid rgba(255, 255, 255, 0.12);",
        "    border-radius: 20px;",
        "    padding: 28px;",
        "    margin-bottom: 24px;",
        "    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.45);",
        "    transition: transform 0.3s ease, border-color 0.3s ease;",
        "}",
        ".glass-card:hover {",
        "    border-color: rgba(56, 189, 248, 0.4);",
        "}",
        "div[data-testid='stForm'] {",
        "    background: rgba(15, 23, 42, 0.6) !important;",
        "    backdrop-filter: blur(16px);",
        "    border: 1px solid rgba(255, 255, 255, 0.15) !important;",
        "    border-radius: 18px !important;",
        "    padding: 20px !important;",
        "}",
        ".stButton > button {",
        "    width: 100%;",
        "    background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);",
        "    color: #FFFFFF !important;",
        "    font-family: 'Poppins', sans-serif;",
        "    font-weight: 600;",
        "    font-size: 1rem;",
        "    border: none;",
        "    border-radius: 12px;",
        "    padding: 0.75rem 1rem;",
        "    transition: all 0.3s ease;",
        "    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);",
        "}",
        ".stButton > button:hover {",
        "    background: linear-gradient(135deg, #38BDF8 0%, #1D4ED8 100%);",
        "    transform: translateY(-2px);",
        "    box-shadow: 0 6px 24px rgba(14, 165, 233, 0.6);",
        "}",

        "# Contact Social Icons",
        ".social-icon-btn {",
        "    display: inline-flex;",
        "    align-items: center;",
        "    justify-content: center;",
        "    width: 60px;",
        "    height: 60px;",
        "    border-radius: 50%;",
        "    font-size: 1.8rem;",
        "    text-decoration: none !important;",
        "    color: #FFFFFF !important;",
        "    transition: all 0.3s ease;",
        "    margin-right: 18px;",
        "    margin-top: 10px;",
        "}",
        ".icon-email {",
        "    background: linear-gradient(135deg, #EA4335 0%, #C5221F 100%);",
        "    box-shadow: 0 4px 15px rgba(234, 67, 53, 0.35);",
        "}",
        ".icon-email:hover {",
        "    transform: scale(1.15);",
        "    box-shadow: 0 6px 22px rgba(234, 67, 53, 0.65);",
        "}",
        ".icon-insta {",
        "    background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);",
        "    box-shadow: 0 4px 15px rgba(220, 39, 67, 0.35);",
        "}",
        ".icon-insta:hover {",
        "    transform: scale(1.15);",
        "    box-shadow: 0 6px 22px rgba(220, 39, 67, 0.65);",
        "}",
        ".icon-linkedin {",
        "    background: #0A66C2;",
        "    box-shadow: 0 4px 15px rgba(10, 102, 194, 0.35);",
        "}",
        ".icon-linkedin:hover {",
        "    transform: scale(1.15);",
        "    box-shadow: 0 6px 22px rgba(10, 102, 194, 0.65);",
        "}",
        ".badge {",
        "    display: inline-block;",
        "    padding: 8px 16px;",
        "    border-radius: 20px;",
        "    font-size: 0.88rem;",
        "    font-weight: 600;",
        "    background: rgba(56, 189, 248, 0.12);",
        "    color: #38BDF8 !important;",
        "    border: 1px solid rgba(56, 189, 248, 0.3);",
        "    margin-right: 8px;",
        "    margin-bottom: 8px;",
        "}",
        "</style>"
    ]
    st.markdown("\n".join(css_lines), unsafe_allow_html=True)

# ---------------- ACCURATE WEATHER API (WeatherAPI Service) ----------------
@st.cache_data(ttl=300)
def fetch_google_accurate_weather(city_name):
    # Live high-accuracy meteorological endpoint matching Google Weather
    api_key = "3b08e24c7f074d2db17105022241505"
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city_name}&days=7&aqi=no&alerts=no"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

# ---------------- PAGE: HOME ----------------
def page_home():
    apply_custom_styles("https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1920&q=80")

    st.markdown("""
        <div class="main-header-box">
            <h1 class="main-title">WEATHER FORECAST</h1>
            <p class="main-subtitle">By Hafiz Muhammad Ubaid</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form(key="search_form"):
        col_search, col_opts1, col_opts2 = st.columns([2.5, 1, 1])

        with col_search:
            default_city = st.session_state.get("active_city", "Karachi")
            city_input = st.text_input("SEARCH CITY", value=default_city, placeholder="e.g. Karachi, Tokyo, London, New York")

        with col_opts1:
            unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"])

        with col_opts2:
            speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s"])

        submit_btn = st.form_submit_button("GET LIVE ACCURATE FORECAST 🔍")

    if submit_btn:
        if city_input.strip():
            st.session_state["active_city"] = city_input.strip()
        else:
            st.warning("Please enter a valid city name.")

    col_reset, _ = st.columns([1, 3])
    with col_reset:
        if st.button("🔄 Reset / Search Another City"):
            st.session_state["active_city"] = ""
            st.rerun()

    active_city = st.session_state.get("active_city", "Karachi")
    if not active_city:
        active_city = "Karachi"

    with st.spinner("Fetching accurate live weather data for " + str(active_city) + "..."):
        wdata = fetch_google_accurate_weather(active_city)

        if not wdata:
            st.error("Could not fetch accurate weather for '" + str(active_city) + "'. Please check the spelling.")
            return

        loc = wdata["location"]
        curr = wdata["current"]
        forecast_days = wdata["forecast"]["forecastday"]

        city_full = f"{loc['name']}, {loc['country']}"
        lat, lon = loc['lat'], loc['lon']
        
        t_curr = curr["temp_c"]
        t_feels = curr["feelslike_c"]
        humidity = curr["humidity"]
        pressure = curr["pressure_mb"]
        wind_spd = curr["wind_kph"]
        w_desc = curr["condition"]["text"]
        w_icon = "🌤️"

    if "Fahrenheit" in unit:
        t_curr = (t_curr * 1.8) + 32
        t_feels = (t_feels * 1.8) + 32
        u_sym = "°F"
    else:
        u_sym = "°C"

    if speed_unit == "m/s":
        wind_spd = wind_spd / 3.6

    st.markdown("---")

    card_lines = [
        '<div class="glass-card">',
        '<h2 style="margin-bottom:0px;">' + str(w_icon) + ' ' + str(city_full) + '</h2>',
        '<p style="color:#94A3B8 !important; margin-top:2px; font-size:0.9rem;">Coordinates: ' + f'{lat:.2f}' + '°N, ' + f'{lon:.2f}' + '°E</p>',
        '<h1 style="font-size: 3.8rem; margin: 12px 0; color:#38BDF8 !important;">' + f'{t_curr:.1f}' + ' ' + str(u_sym) + ' <span style="font-size:1.6rem; font-weight:400; color:#CBD5E1 !important;">(' + str(w_desc) + ')</span></h1>',
        '<div style="margin-top:15px;">',
        '<span class="badge">Feels Like: ' + f'{t_feels:.1f}' + ' ' + str(u_sym) + '</span>',
        '<span class="badge">Humidity: ' + str(humidity) + '%</span>',
        '<span class="badge">Wind: ' + f'{wind_spd:.1f}' + ' ' + str(speed_unit) + '</span>',
        '<span class="badge">Pressure: ' + str(pressure) + ' hPa</span>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(card_lines), unsafe_allow_html=True)

    # 24-Hour Plotly Graph
    st.markdown("### 📈 24-Hour Temperature Trend")
    hourly_data = forecast_days[0]["hour"]
    h_times = [datetime.datetime.strptime(h["time"], "%Y-%m-%d %H:%M").strftime("%H:00") for h in hourly_data]
    h_temps = [h["temp_c"] for h in hourly_data]

    if "Fahrenheit" in unit:
        h_temps = [(t * 1.8) + 32 for t in h_temps]

    fig_hourly = go.Figure()
    fig_hourly.add_trace(
        go.Scatter(
            x=h_times,
            y=h_temps,
            mode="lines+markers",
            name="Temp (" + str(u_sym) + ")",
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
        yaxis_title="Temperature (" + str(u_sym) + ")",
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    # 7-Day Forecast Chart
    st.markdown("### 🗓️ Extended Forecast")
    d_dates = [datetime.datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a, %b %d") for d in forecast_days]
    d_max = [d["day"]["maxtemp_c"] for d in forecast_days]
    d_min = [d["day"]["mintemp_c"] for d in forecast_days]

    if "Fahrenheit" in unit:
        d_max = [(t * 1.8) + 32 for t in d_max]
        d_min = [(t * 1.8) + 32 for t in d_min]

    d_conditions = [d["day"]["condition"]["text"] for d in forecast_days]

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_max, name="Max Temp (" + str(u_sym) + ")", marker_color="#38BDF8"))
    fig_daily.add_trace(go.Bar(x=d_dates, y=d_min, name="Min Temp (" + str(u_sym) + ")", marker_color="#1E40AF"))
    
    fig_daily.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="group",
        margin=dict(l=20, r=20, t=20, b=20),
        height=340
    )
    st.plotly_chart(fig_daily, use_container_width=True)

    # Data Tables
    st.markdown("### 📊 Tabular Breakdown")
    tab1, tab2 = st.tabs(["Daily Forecast Data", "Hourly Forecast Data"])

    with tab1:
        st.dataframe(
            {
                "Date": d_dates,
                "Condition": d_conditions,
                "Max Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_max],
                "Min Temp (" + str(u_sym) + ")": [round(x, 1) for x in d_min],
                "Rain Chance": [str(d["day"]["daily_chance_of_rain"]) + "%" for d in forecast_days],
                "Max Wind (" + str(speed_unit) + ")": [round(d["day"]["maxwind_kph"] if speed_unit == "km/h" else d["day"]["maxwind_kph"] / 3.6, 1) for d in forecast_days]
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            {
                "Time": h_times,
                "Temperature (" + str(u_sym) + ")": [round(x, 1) for x in h_temps],
                "Humidity": [str(h["humidity"]) + "%" for h in hourly_data],
                "Rain Chance": [str(h["chance_of_rain"]) + "%" for h in hourly_data]
            },
            use_container_width=True,
            hide_index=True
        )

    st.caption("Crafted by **Hafiz Muhammad Ubaid** | Live Accurate Weather Data")

# ---------------- PAGE: ABOUT ----------------
def page_about():
    apply_custom_styles("https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1920&q=80")

    st.markdown("""
        <div class="main-header-box">
            <h1 class="main-title">ABOUT THE PROJECT</h1>
            <p class="main-subtitle">By Hafiz Muhammad Ubaid</p>
        </div>
    """, unsafe_allow_html=True)
    
    about_lines = [
        '<div class="glass-card">',
        '<h2>WEATHER FORECAST BY HAFIZ MUHAMMAD UBAID ✪</h2>',
        '<p>Welcome to <b>WEATHER FORECAST BY HAFIZ MUHAMMAD UBAID ✪</b> — a modern, interactive weather tracking platform designed to offer high-precision meteorological insight.</p>',
        '<hr style="border-color: rgba(255,255,255,0.1);">',
        '<h3>🚀 Key Features</h3>',
        '<ul>',
        '<li><b>High Accuracy:</b> Matched real-time data aligned with official regional temperature stations.</li>',
        '<li><b>Luxury Navigation:</b> Modernized sidebar navigation layout.</li>',
        '<li><b>Interactive Analytics:</b> Clean dark-themed Plotly graphs for hourly and daily forecasts.</li>',
        '</ul>',
        '<hr style="border-color: rgba(255,255,255,0.1);">',
        '<h3>👨‍💻 Developer</h3>',
        '<p>Designed and engineered by <b>Hafiz Muhammad Ubaid</b>.</p>',
        '</div>'
    ]
    st.markdown("".join(about_lines), unsafe_allow_html=True)

# ---------------- PAGE: CONTACT ----------------
def page_contact():
    apply_custom_styles("https://images.unsplash.com/photo-1516912481808-3406841bd33c?auto=format&fit=crop&w=1920&q=80")

    st.markdown("""
        <div class="main-header-box">
            <h1 class="main-title">CONNECT WITH ME</h1>
            <p class="main-subtitle">By Hafiz Muhammad Ubaid</p>
        </div>
    """, unsafe_allow_html=True)
    
    email_address = "ubaidsajid2006@gmail.com"
    insta_link = "https://www.instagram.com/muhammadubaid__?stkn=eWV4ejI1MXh0Mndr&utm_source=qr"
    linkedin_link = "https://www.linkedin.com/in/muhammad-ubaid-2b88722b3?utm_source=share_via&utm_content=profile&utm_medium=member_ios"

    contact_lines = [
        '<div class="glass-card">',
        '<h2>Hafiz Muhammad Ubaid</h2>',
        '<p style="font-size: 1.05rem; color: #CBD5E1 !important;">Feel free to reach out for collaborations, feedback, or development inquiries!</p>',
        '<hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">',
        '<h3>🌐 Contact & Social Profiles</h3>',
        '<p style="color: #94A3B8 !important;">Click any button below to email me or connect directly on my socials:</p>',
        '<div style="margin-top: 20px; display: flex; align-items: center; gap: 10px;">',
        '<a href="mailto:' + str(email_address) + '" class="social-icon-btn icon-email" title="Send Email"><i class="fa-solid fa-envelope"></i></a>',
        '<a href="' + str(insta_link) + '" target="_blank" class="social-icon-btn icon-insta" title="Instagram Profile"><i class="fa-brands fa-instagram"></i></a>',
        '<a href="' + str(linkedin_link) + '" target="_blank" class="social-icon-btn icon-linkedin" title="LinkedIn Profile"><i class="fa-brands fa-linkedin-in"></i></a>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(contact_lines), unsafe_allow_html=True)

# ---------------- MAIN APP ROUTER ----------------
def main():
    st.sidebar.markdown("""
        <div style="padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
            <h2 style="margin:0; font-size: 1.3rem; letter-spacing: 1px; color: #38BDF8 !important;">WEATHER APP</h2>
            <p style="font-size: 0.8rem; color: #94A3B8 !important; margin-top: 4px;">By Hafiz Muhammad Ubaid</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Improved Navigation Cards in Sidebar
    page = st.sidebar.radio(
        "NAVIGATION", 
        ["🏠  Home", "ℹ️  About", "📞  Contact"]
    )

    if "Home" in page:
        page_home()
    elif "About" in page:
        page_about()
    else:
        page_contact()

if __name__ == "__main__":
    main()
