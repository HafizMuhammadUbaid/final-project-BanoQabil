import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="WEATHER FORECAST | HMU ✪",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEATHER_URL = "[https://api.openweathermap.org/data/2.5/weather](https://api.openweathermap.org/data/2.5/weather)"
FORECAST_URL = "[https://api.openweathermap.org/data/2.5/forecast](https://api.openweathermap.org/data/2.5/forecast)"

# ---------------------------------------------------------
# STYLING & GLASSMORPHISM CSS
# ---------------------------------------------------------
def inject_custom_css(bg_url):
    st.markdown(
        f"""
        <style>
        @import url('[https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap)');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                        url("{bg_url}") no-repeat center center fixed;
            background-size: cover;
        }}

        /* Glassmorphism Containers */
        .glass-card {{
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}

        .metric-badge {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6, p, label, span {{
            color: #FFFFFF !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            color: white !important;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }}

        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }}

        /* Inputs & Selectboxes */
        .stTextInput input, .stSelectbox select {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }}

        /* Custom Table Styling */
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.95em;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}

        .styled-table thead tr {{
            background-color: rgba(59, 130, 246, 0.4);
            color: #ffffff;
            text-align: left;
            font-weight: bold;
        }}

        .styled-table th, .styled-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .styled-table tbody tr {{
            background-color: rgba(255, 255, 255, 0.03);
            transition: background-color 0.2s ease;
        }}

        .styled-table tbody tr:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# API KEY RETRIEVAL
# ---------------------------------------------------------
def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        st.error("⚠️ OpenWeather API key is missing.")
        st.info("Add `OPENWEATHER_API_KEY = \"YOUR_KEY\"` in your `.streamlit/secrets.toml` file.")
        return None

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
def page_home():
    inject_custom_css("[https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=2000&auto=format&fit=crop](https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=2000&auto=format&fit=crop)")

    st.markdown("<h1 style='text-align: center; font-weight: 700;'>⚡ WEATHER FORECAST DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.8;'>Real-time weather telemetry & 5-day predictive insights</p><br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        
        with c1:
            city = st.text_input("📍 CITY NAME", placeholder="e.g. Karachi, London, Tokyo")
        with c2:
            unit = st.selectbox("🌡️ TEMPERATURE", ["Celsius", "Fahrenheit"])
        with c3:
            speed = st.selectbox("💨 WIND SPEED", ["Kilometre/hour", "Metre/sec"])
        with c4:
            graph = st.radio("📊 GRAPH STYLE", ["Bar Graph", "Line Graph"], horizontal=True)

        submit_btn = st.button("GET FORECAST 🚀")
        st.markdown('</div>', unsafe_allow_html=True)

    if not submit_btn:
        return

    city_clean = city.strip()
    if not city_clean:
        st.warning("Please enter a valid city name.")
        return

    api = get_api_key()
    if not api:
        return

    try:
        # Fetch Current Weather
        res_current = requests.get(WEATHER_URL, params={"q": city_clean, "appid": api, "units": "metric"}, timeout=12)
        if res_current.status_code == 404:
            st.error("City not found. Please check spelling.")
            return
        res_current.raise_for_status()
        current_data = res_current.json()

        # Fetch 5-Day Forecast
        res_forecast = requests.get(FORECAST_URL, params={"q": city_clean, "appid": api, "units": "metric"}, timeout=12)
        res_forecast.raise_for_status()
        forecast_data = res_forecast.json()

        forecast_list = forecast_data.get("list", [])
        if not forecast_list:
            st.error("No forecast metrics returned.")
            return

        # Process Daily Metrics
        daily_map = {}
        for item in forecast_list:
            dt_obj = datetime.datetime.fromtimestamp(item["dt"]).date()
            daily_map.setdefault(dt_obj, []).append(item)

        valid_dates = [d for d in sorted(daily_map.keys()) if d >= datetime.date.today()][:5]

        dates, max_temps, min_temps = [], [], []
        pressures, humidities, clouds, rain_pops, wind_speeds, desc_list = [], [], [], [], [], []

        for d in valid_dates:
            items = daily_map[d]
            t_max = max(x["main"]["temp"] for x in items)
            t_min = min(x["main"]["temp"] for x in items)

            if unit == "Fahrenheit":
                t_max = (t_max * 1.8) + 32
                t_min = (t_min * 1.8) + 32

            max_temps.append(round(t_max, 1))
            min_temps.append(round(t_min, 1))

            mid_item = min(items, key=lambda x: abs(datetime.datetime.fromtimestamp(x["dt"]).hour - 12))
            pressures.append(mid_item["main"]["pressure"])
            humidities.append(f"{mid_item['main']['humidity']}%")
            clouds.append(f"{mid_item['clouds']['all']}%")

            pop_avg = sum(i.get("pop", 0) for i in items) / len(items)
            rain_pops.append(f"{int(pop_avg * 100)}%")

            desc_list.append(mid_item["weather"][0]["description"].title())

            w_avg = sum(i["wind"]["speed"] for i in items) / len(items)
            if speed == "Kilometre/hour":
                wind_speeds.append(f"{round(w_avg * 3.6, 1)} km/h")
            else:
                wind_speeds.append(f"{round(w_avg, 1)} m/s")

            dates.append(d.strftime("%d %b"))

        # Main Temperature Display
        curr_temp = current_data["main"]["temp"]
        if unit == "Fahrenheit":
            curr_temp = (curr_temp * 1.8) + 32

        temp_unit_label = "°C" if unit == "Celsius" else "°F"
        icon_code = current_data["weather"][0]["icon"]
        weather_desc = current_data["weather"][0]["description"].title()

        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2 style="margin: 0;">{current_data['name']}, {current_data['sys']['country']}</h2>
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin: 10px 0;">
                <img src="[https://openweathermap.org/img/wn/](https://openweathermap.org/img/wn/){icon_code}@4x.png" width="100" />
                <span style="font-size: 3.5rem; font-weight: 700;">{round(curr_temp, 1)}{temp_unit_label}</span>
            </div>
            <h4 style="text-transform: uppercase; letter-spacing: 2px; color: #60A5FA !important;">{weather_desc}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Plotly Chart Section
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Temperature Trend (5-Day)")
        
        fig = go.Figure()
        if graph == "Bar Graph":
            fig.add_trace(go.Bar(x=dates, y=max_temps, name="Max Temp", marker_color='#3B82F6'))
            fig.add_trace(go.Bar(x=dates, y=min_temps, name="Min Temp", marker_color='#93C5FD'))
            fig.update_layout(barmode='group')
        else:
            fig.add_trace(go.Scatter(x=dates, y=max_temps, name="Max Temp", mode='lines+markers', line=dict(color='#3B82F6', width=3)))
            fig.add_trace(go.Scatter(x=dates, y=min_temps, name="Min Temp", mode='lines+markers', line=dict(color='#93C5FD', width=3)))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title=f'Temperature ({temp_unit_label})'),
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # HTML Data Tables
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 Forecast Breakdown")
        
        table_html = f"""
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Condition</th>
                    <th>Max ({temp_unit_label})</th>
                    <th>Min ({temp_unit_label})</th>
                    <th>Rain Chance</th>
                    <th>Humidity</th>
                    <th>Wind Speed</th>
                    <th>Pressure</th>
                </tr>
            </thead>
            <tbody>
        """
        for i in range(len(dates)):
            table_html += f"""
                <tr>
                    <td><strong>{dates[i]}</strong></td>
                    <td>{desc_list[i]}</td>
                    <td>{max_temps[i]}</td>
                    <td>{min_temps[i]}</td>
                    <td>{rain_pops[i]}</td>
                    <td>{humidities[i]}</td>
                    <td>{wind_speeds[i]}</td>
                    <td>{pressures[i]} hPa</td>
                </tr>
            """
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except requests.exceptions.RequestException:
        st.error("Network timeout or connection failure. Please try again.")

# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------
def page_about():
    inject_custom_css("[https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000&auto=format&fit=crop](https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000&auto=format&fit=crop)")
    
    st.markdown("""
    <div class="glass-card" style="max-width: 800px; margin: 40px auto;">
        <h1 style="color: #60A5FA !important;">📜 ABOUT THE PROJECT</h1>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            WEATHER FORECAST BY HMU ✪ is a high-performance web dashboard built to deliver precise real-time weather analytics and 5-day predictive forecasts. 
        </p>
        <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 20px 0;">
        <h3>✨ Core Highlights</h3>
        <ul style="line-height: 1.8;">
            <li>Dynamic UI with glassmorphism overlays and ambient thematic lighting</li>
            <li>Live OpenWeather API integration for accurate globally-sampled weather</li>
            <li>Customizable unit systems (Imperial & Metric)</li>
            <li>Interactive Plotly temperature projection charts</li>
        </ul>
        <hr style="border: 0.5px solid rgba(255,255,255,0.1); margin: 20px 0;">
        <h3>👨‍💻 Creator</h3>
        <p>Designed & Developed by <strong style="color: #60A5FA;">Hafiz Muhammad Ubaid</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONTACT PAGE
# ---------------------------------------------------------
def page_contact():
    inject_custom_css("[https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2000&auto=format&fit=crop](https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2000&auto=format&fit=crop)")
    
    st.markdown("""
    <div class="glass-card" style="max-width: 600px; margin: 40px auto; text-align: center;">
        <h1 style="color: #60A5FA !important;">📩 GET IN TOUCH</h1>
        <p>Have questions, feedback, or collaboration ideas? Reach out via any of the channels below:</p>
        <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 30px;">
            <div class="metric-badge">📧 <strong>Email:</strong> ubaidsajid2006@gmail.com</div>
            <div class="metric-badge">📸 <strong>Instagram:</strong> @muhammadubaid__</div>
            <div class="metric-badge">💼 <strong>LinkedIn:</strong> Hafiz Muhammad Ubaid</div>
            <div class="metric-badge">💻 <strong>GitHub:</strong> Muhammad Ubaid</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN ROUTER
# ---------------------------------------------------------
def main():
    st.sidebar.title("☰ NAVIGATION")
    page = st.sidebar.radio("Go to", ["Home", "About", "Contact"])

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
