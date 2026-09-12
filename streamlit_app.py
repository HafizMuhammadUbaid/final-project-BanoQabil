import streamlit as st
import datetime
import requests
from plotly import graph_objects as go

# ---------------- CONFIGURATION ----------------
st.set_page_config(
    page_title="WEATHER FORECAST BY HMU ✪",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ---------------- HELPER FUNCTIONS ----------------

def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        st.error("OpenWeather API key is not configured.")
        st.info(
            'Streamlit Cloud: App settings → Secrets → add '
            'OPENWEATHER_API_KEY = "YOUR_API_KEY"'
        )
        return None


def set_custom_theme(bg_image_url):
    st.markdown(
        f"""
        
        """,
        unsafe_allow_html=True,
    )

# ---------------- PAGES ----------------

def page_home():
    set_custom_theme(
        "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1920&q=80"
    )

    st.title("WEATHER FORECAST ⚡")

    col_input, col_settings = st.columns([2, 1])

    with col_input:
        city = st.text_input("ENTER CITY NAME", placeholder="e.g., Karachi, London, Tokyo")

    with col_settings:
        unit = st.selectbox("TEMPERATURE UNIT", ["Celsius", "Fahrenheit"])
        speed = st.selectbox("WIND SPEED UNIT", ["Kilometre/hour", "Metre/sec"])
        graph = st.radio("GRAPH TYPE", ["Line Graph", "Bar Graph"], horizontal=True)

    if st.button("GET FORECAST"):
        if city.strip():
            st.session_state["searched_city"] = city.strip()
        else:
            st.warning("Please enter a city name.")

    target_city = st.session_state.get("searched_city", None)
    if not target_city:
        return

    api = get_api_key()
    if not api:
        return

    try:
        # Fetch Current Weather
        res_curr = requests.get(
            WEATHER_URL,
            params={"q": target_city, "appid": api, "units": "metric"},
            timeout=15
        )
        if res_curr.status_code == 404:
            st.error("Invalid city! Please check the spelling and try again.")
            return
        res_curr.raise_for_status()
        current = res_curr.json()

        # Fetch 5-Day Forecast
        res_fore = requests.get(
            FORECAST_URL,
            params={"q": target_city, "appid": api, "units": "metric"},
            timeout=15
        )
        res_fore.raise_for_status()
        forecast_list = res_fore.json().get("list", [])

        # Process Daily Data
        daily_data = {}
        for item in forecast_list:
            dt_obj = datetime.datetime.fromtimestamp(item["dt"]).date()
            daily_data.setdefault(dt_obj, []).append(item)

        dates_available = sorted([d for d in daily_data.keys() if d >= datetime.date.today()])[:5]

        max_temp, min_temp, pressure, humidity = [], [], [], []
        wind_speed, description, cloud, rain, dates = [], [], [], [], []

        for date in dates_available:
            items = daily_data[date]
            temps = [i["main"]["temp"] for i in items]
            
            max_t = max(temps)
            min_t = min(temps)

            if unit == "Fahrenheit":
                max_t = (max_t * 1.8) + 32
                min_t = (min_t * 1.8) + 32

            max_temp.append(round(max_t, 1))
            min_temp.append(round(min_t, 1))

            selected = min(items, key=lambda x: abs(datetime.datetime.fromtimestamp(x["dt"]).hour - 12))

            pressure.append(selected["main"]["pressure"])
            humidity.append(f"{selected['main']['humidity']}%")
            cloud.append(f"{selected['clouds']['all']}%")

            pop = sum(i.get("pop", 0) for i in items) / len(items)
            rain.append(f"{int(pop * 100)}%")
            description.append(selected["weather"][0]["description"].title())

            avg_w = sum(i["wind"]["speed"] for i in items) / len(items)
            w_val = round(avg_w * 3.6, 1) if speed == "Kilometre/hour" else round(avg_w, 1)
            w_unit = "km/h" if speed == "Kilometre/hour" else "m/s"
            wind_speed.append(f"{w_val} {w_unit}")

            dates.append(date.strftime("%a, %b %d"))

        # Current Temp Display
        temp_unit = "°C" if unit == "Celsius" else "°F"
        curr_t = current["main"]["temp"]
        if unit == "Fahrenheit":
            curr_t = (curr_t * 1.8) + 32
        curr_t = round(curr_t, 1)

        icon = current["weather"][0]["icon"]
        curr_desc = current["weather"][0]["description"].title()

        st.markdown("---")
        st.subheader(f"Current Conditions in {current['name']}, {current['sys']['country']}")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        c1.metric("TEMPERATURE", f"{curr_t} {temp_unit}")
        c2.metric("CONDITION", curr_desc)
        with c3:
            st.image(f"https://openweathermap.org/img/wn/{icon}@4x.png", width=100)

        # Graph Render
        st.markdown("### 📈 5-Day Temperature Forecast")
        fig = go.Figure()

        if graph == "Bar Graph":
            fig.add_trace(go.Bar(name="Max Temp", x=dates, y=max_temp, marker_color="#00D2FF"))
            fig.add_trace(go.Bar(name="Min Temp", x=dates, y=min_temp, marker_color="#3A7BD5"))
            fig.update_layout(barmode="group")
        else:
            fig.add_trace(go.Scatter(name="Max Temp", x=dates, y=max_temp, mode="lines+markers", line=dict(color="#00D2FF", width=3)))
            fig.add_trace(go.Scatter(name="Min Temp", x=dates, y=min_temp, mode="lines+markers", line=dict(color="#3A7BD5", width=3)))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Date",
            yaxis_title=f"Temperature ({temp_unit})",
            margin=dict(l=20, r=20, t=30, b=20),
            height=380
        )
        st.plotly_chart(fig, use_container_width=True)

        # Forecast Tables
        st.markdown("### 📊 Detailed Daily Breakdown")
        
        t1, t2 = st.tabs(["Temperature & Rainfall", "Wind & Atmosphere"])
        
        with t1:
            st.dataframe(
                {
                    "Date": dates,
                    f"Max Temp ({temp_unit})": max_temp,
                    f"Min Temp ({temp_unit})": min_temp,
                    "Rain Chance": rain,
                    "Cloud Cover": cloud,
                    "Humidity": humidity,
                },
                use_container_width=True,
                hide_index=True
            )

        with t2:
            st.dataframe(
                {
                    "Date": dates,
                    "Condition": description,
                    "Wind Speed": wind_speed,
                    "Pressure (hPa)": pressure
                },
                use_container_width=True,
                hide_index=True
            )

        st.caption("Developed by **Hafiz Muhammad Ubaid**")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")


def page_about():
    set_custom_theme(
        "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1920&q=80"
    )

    st.title("📜 ABOUT")

    st.markdown(
        """
