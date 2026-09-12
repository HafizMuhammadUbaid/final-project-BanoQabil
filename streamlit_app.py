
import streamlit as st
import datetime
import requests
from plotly import graph_objects as go

st.set_page_config(
    page_title="WEATHER FORECAST BY HMU ✪",
    page_icon="☁️",
    layout="wide",
)

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


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


def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: white !important;
        }}

        .stButton > button {{
            width: 100%;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_home():

    set_background(
        "https://images.unsplash.com/photo-1536244636800-a3f74db0f3cf"
        "?q=80&w=1992&auto=format&fit=crop"
    )

    st.title("BANO QABIL 2.0")
    st.title("WEATHER FORECAST ⚡")

    city = st.text_input("ENTER THE NAME OF THE CITY")

    unit = st.selectbox(
        "SELECT TEMPERATURE UNIT",
        ["Celsius", "Fahrenheit"]
    )

    speed = st.selectbox(
        "SELECT WIND SPEED UNIT",
        ["Metre/sec", "Kilometre/hour"]
    )

    graph = st.radio(
        "SELECT GRAPH TYPE",
        ["Bar Graph", "Line Graph"]
    )

    if not st.button("SUBMIT"):
        return

    city = city.strip()

    if not city:
        st.warning("Please enter a city name.")
        return

    api = get_api_key()

    if not api:
        return

    try:

        # ---------------- CURRENT WEATHER ----------------

        response = requests.get(
            WEATHER_URL,
            params={
                "q": city,
                "appid": api,
                "units": "metric",
            },
            timeout=15,
        )

        if response.status_code == 404:
            st.error("Invalid city! Please try again.")
            return

        if response.status_code in (401, 403):
            st.error("Invalid API key or API access problem.")
            return

        response.raise_for_status()

        current = response.json()

        # ---------------- 5 DAY FORECAST ----------------

        forecast_response = requests.get(
            FORECAST_URL,
            params={
                "q": city,
                "appid": api,
                "units": "metric",
            },
            timeout=15,
        )

        if forecast_response.status_code in (401, 403):
            st.error("Your OpenWeather API key does not have access to the forecast API.")
            return

        forecast_response.raise_for_status()

        forecast = forecast_response.json()

        forecast_list = forecast.get("list", [])

        if not forecast_list:
            st.error("No forecast data was returned.")
            return

        # ---------------- DAILY DATA ----------------

        daily_data = {}

        for item in forecast_list:

            date = datetime.datetime.fromtimestamp(
                item["dt"]
            ).date()

            if date not in daily_data:
                daily_data[date] = []

            daily_data[date].append(item)

        # Remove today's partial data
        dates_available = sorted(daily_data.keys())

        today = datetime.date.today()

        dates_available = [
            d for d in dates_available
            if d >= today
        ]

        # Maximum 5 forecast days
        dates_available = dates_available[:5]

        max_temp = []
        min_temp = []
        pressure = []
        humidity = []
        wind_speed = []
        description = []
        cloud = []
        rain = []
        dates = []

        for date in dates_available:

            items = daily_data[date]

            temps = [
                item["main"]["temp"]
                for item in items
            ]

            max_t = max(temps)
            min_t = min(temps)

            # Temperature conversion
            if unit == "Celsius":

                max_temp.append(round(max_t, 2))
                min_temp.append(round(min_t, 2))

            else:

                max_temp.append(
                    round((max_t * 1.8) + 32, 2)
                )

                min_temp.append(
                    round((min_t * 1.8) + 32, 2)
                )

            # Use midday/central forecast where possible
            selected = min(
                items,
                key=lambda x: abs(
                    datetime.datetime.fromtimestamp(
                        x["dt"]
                    ).hour - 12
                )
            )

            pressure.append(
                selected["main"]["pressure"]
            )

            humidity.append(
                f'{selected["main"]["humidity"]} %'
            )

            cloud.append(
                f'{selected["clouds"]["all"]} %'
            )

            # Average probability of precipitation
            pop = sum(
                item.get("pop", 0)
                for item in items
            ) / len(items)

            rain.append(
                f"{int(pop * 100)}%"
            )

            description.append(
                selected["weather"][0]["description"].title()
            )

            # Average wind speed
            avg_wind = sum(
                item["wind"]["speed"]
                for item in items
            ) / len(items)

            if speed == "Kilometre/hour":

                wind_speed.append(
                    f"{round(avg_wind * 3.6, 1)} km/h"
                )

            else:

                wind_speed.append(
                    f"{round(avg_wind, 1)} m/s"
                )

            dates.append(
                date.strftime("%d %b")
            )

        # ---------------- CURRENT WEATHER ----------------

        temp_unit = "°C" if unit == "Celsius" else "°F"

        current_temp = current["main"]["temp"]

        if unit == "Fahrenheit":

            current_temp = (
                current_temp * 1.8
            ) + 32

        current_temp = round(
            current_temp,
            2
        )

        icon = current["weather"][0]["icon"]

        current_weather = (
            current["weather"][0]["description"]
            .title()
        )

        # ---------------- CURRENT DISPLAY ----------------

        col1, col2 = st.columns(2)

        with col1:
            st.write("## Current Temperature")

        with col2:
            st.image(
                f"https://openweathermap.org/img/wn/{icon}@2x.png",
                width=70,
            )

        col1, col2 = st.columns(2)

        col1.metric(
            "TEMPERATURE",
            f"{current_temp} {temp_unit}"
        )

        col2.metric(
            "WEATHER",
            current_weather
        )

        # ---------------- GRAPH ----------------

        if graph == "Bar Graph":

            fig = go.Figure(
                data=[
                    go.Bar(
                        name="Maximum",
                        x=dates,
                        y=max_temp,
                    ),
                    go.Bar(
                        name="Minimum",
                        x=dates,
                        y=min_temp,
                    ),
                ]
            )

            fig.update_layout(
                xaxis_title="Dates",
                yaxis_title=f"Temperature ({temp_unit})",
                barmode="group",
                margin=dict(
                    l=70,
                    r=10,
                    t=80,
                    b=80,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=min_temp,
                    name="Minimum",
                    mode="lines+markers",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=max_temp,
                    name="Maximum",
                    mode="lines+markers",
                )
            )

            fig.update_layout(
                xaxis_title="Dates",
                yaxis_title=f"Temperature ({temp_unit})",
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ---------------- TABLE 1 ----------------

        table1 = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "<b>DATES</b>",
                            f"<b>MAX TEMP<br>(in {temp_unit})</b>",
                            f"<b>MIN TEMP<br>(in {temp_unit})</b>",
                            "<b>CHANCES OF RAIN</b>",
                            "<b>CLOUD COVERAGE</b>",
                            "<b>HUMIDITY</b>",
                        ],
                    ),
                    cells=dict(
                        values=[
                            dates,
                            max_temp,
                            min_temp,
                            rain,
                            cloud,
                            humidity,
                        ]
                    ),
                )
            ]
        )

        table1.update_layout(
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10,
            ),
            height=328,
        )

        st.plotly_chart(
            table1,
            use_container_width=True
        )

        # ---------------- TABLE 2 ----------------

        table2 = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "<b>DATES</b>",
                            "<b>WEATHER CONDITION</b>",
                            "<b>WIND SPEED</b>",
                            "<b>PRESSURE<br>(in hPa)</b>",
                        ],
                    ),
                    cells=dict(
                        values=[
                            dates,
                            description,
                            wind_speed,
                            pressure,
                        ]
                    ),
                )
            ]
        )

        table2.update_layout(
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10,
            ),
            height=300,
        )

        st.plotly_chart(
            table2,
            use_container_width=True
        )

        st.markdown(
            "Made By **Hafiz Muhammad Ubaid**"
        )

        st.markdown(
            "Partners Abdul Hadi And Abdullah Tanoli"
        )

    except requests.exceptions.Timeout:

        st.error(
            "Weather service timed out. Please try again."
        )

    except requests.exceptions.RequestException as exc:

        st.error(
            f"Weather service error: {exc}"
        )

    except (KeyError, TypeError, ValueError):

        st.error(
            "The weather service returned unexpected data."
        )


def page_about():

    set_background(
        "https://images.pexels.com/photos/207700/pexels-photo-207700.jpeg"
        "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    )

    st.title("📜 ABOUT")

    st.markdown(
        """
## WEATHER FORECAST BY HMU ✪

Welcome to WEATHER FORECAST BY HMU ✪, your weather
forecast application.

### About the Creator

**Hafiz Muhammad Ubaid** created this project as a
weather forecasting application designed to make
weather information easy to access.

### Features

- Real-time weather information
- 5-day weather forecast
- Celsius / Fahrenheit
- Metre/sec / Kilometre/hour
- Bar graph
- Line graph
- Weather forecast tables

### Our Team

**Group Leader:** Muhammad Ubaid

**Partners:** Abdul Hadi And Abdullah Tanoli
"""
    )


def page_contact():

    set_background(
        "https://w0.peakpx.com/wallpaper/117/681/HD-wallpaper-wood-ahsap"
        "-black-brown-dark-lumber-madera-papers-wall-woods.jpg"
    )

    st.title("📩 CONTACT")

    st.markdown(
        """
## CONTACT INFORMATION

**Group Leader:** Muhammad Ubaid

**Project Partners:** Abdul Hadi And Abdullah Tanoli

**Instagram:** @muhammadubaid__

**LinkedIn:** Hafiz Muhammad Ubaid

**GitHub:** Muhammad Ubaid

**Email:** ubaidsajid2006@gmail.com
"""
    )


def main():

    st.sidebar.title("☰ MENU")

    page = st.sidebar.radio(
        "Go to",
        ["Home", "About", "Contact"]
    )

    try:

        st.sidebar.image(
            "icc.jpg",
            use_container_width=True
        )

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

