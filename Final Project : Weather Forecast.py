import streamlit as st
import datetime
import requests
from plotly import graph_objects as go

st.set_page_config(
    page_title="WEATHER FORECAST BY HMU ✪",
    page_icon="☁️",
    layout="wide",
)

API_URL = "https://api.openweathermap.org/data/3.0/onecall"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        st.error("OpenWeather API key is not configured.")
        st.info(
            "Streamlit Cloud: App settings → Secrets → add "
            "OPENWEATHER_API_KEY = \"YOUR_NEW_API_KEY\""
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
    st.title("WEATHER FORECAST⚡")

    city = st.text_input("ENTER THE NAME OF THE CITY")
    unit = st.selectbox("SELECT TEMPERATURE UNIT", ["Celsius", "Fahrenheit"])
    speed = st.selectbox(
        "SELECT WIND SPEED UNIT", ["Metre/sec", "Kilometre/hour"]
    )
    graph = st.radio("SELECT GRAPH TYPE", ["Bar Graph", "Line Graph"])

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
        response = requests.get(
            WEATHER_URL,
            params={"q": city, "appid": api},
            timeout=15,
        )

        if response.status_code == 404:
            st.error("Invalid city! Please try again.")
            return

        response.raise_for_status()
        current = response.json()

        lat = current["coord"]["lat"]
        lon = current["coord"]["lon"]

        forecast_response = requests.get(
            API_URL,
            params={
                "lat": lat,
                "lon": lon,
                "exclude": "minutely,hourly,alerts",
                "appid": api,
                "units": "metric",
            },
            timeout=15,
        )

        if forecast_response.status_code in (401, 403):
            st.error(
                "Your OpenWeather API key/account does not have access to "
                "One Call 3.0. Enable One Call 3.0 in your OpenWeather "
                "account, then try again."
            )
            return

        forecast_response.raise_for_status()
        forecast = forecast_response.json()

        daily = forecast.get("daily", [])
        if not daily:
            st.error("No daily forecast data was returned.")
            return

        max_temp = []
        min_temp = []
        pressure = []
        humidity = []
        wind_speed = []
        description = []
        cloud = []
        rain = []
        dates = []
        sunrise = []
        sunset = []

        for item in daily[:7]:
            if unit == "Celsius":
                max_temp.append(round(item["temp"]["max"], 2))
                min_temp.append(round(item["temp"]["min"], 2))
            else:
                max_temp.append(round((item["temp"]["max"] * 1.8) + 32, 2))
                min_temp.append(round((item["temp"]["min"] * 1.8) + 32, 2))

            if speed == "Kilometre/hour":
                wind_speed.append(f'{round(item["wind_speed"] * 3.6, 1)} km/h')
            else:
                wind_speed.append(f'{round(item["wind_speed"], 1)} m/s')

            pressure.append(item["pressure"])
            humidity.append(f'{item["humidity"]} %')
            cloud.append(f'{item["clouds"]} %')
            rain.append(f'{int(item.get("pop", 0) * 100)}%')
            description.append(item["weather"][0]["description"].title())

            d = datetime.datetime.fromtimestamp(item["dt"]).date()
            dates.append(d.strftime("%d %b"))

            sunrise.append(
                datetime.datetime.fromtimestamp(item["sunrise"]).strftime("%H:%M")
            )
            sunset.append(
                datetime.datetime.fromtimestamp(item["sunset"]).strftime("%H:%M")
            )

        temp_unit = " °C" if unit == "Celsius" else " °F"
        current_temp = current["main"]["temp"]

        if unit == "Fahrenheit":
            current_temp = (current_temp * 1.8) + 32

        current_temp = f"{round(current_temp, 2)}"
        icon = current["weather"][0]["icon"]
        current_weather = current["weather"][0]["description"].title()

        col1, col2 = st.columns(2)
        with col1:
            st.write("## Current Temperature")
        with col2:
            st.image(
                f"https://openweathermap.org/img/wn/{icon}@2x.png",
                width=70,
            )

        col1, col2 = st.columns(2)
        col1.metric("TEMPERATURE", current_temp + temp_unit)
        col2.metric("WEATHER", current_weather)

        if graph == "Bar Graph":
            fig = go.Figure(
                data=[
                    go.Bar(name="Maximum", x=dates, y=max_temp),
                    go.Bar(name="Minimum", x=dates, y=min_temp),
                ]
            )
            fig.update_layout(
                xaxis_title="Dates",
                yaxis_title=f"Temperature ({temp_unit.strip()})",
                barmode="group",
                margin=dict(l=70, r=10, t=80, b=80),
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=dates, y=min_temp, name="Minimum")
            )
            fig.add_trace(
                go.Scatter(x=dates, y=max_temp, name="Maximum")
            )
            fig.update_layout(
                xaxis_title="Dates",
                yaxis_title=f"Temperature ({temp_unit.strip()})",
            )
            st.plotly_chart(fig, use_container_width=True)

        table1 = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "<b>DATES</b>",
                            f"<b>MAX TEMP<br>(in{temp_unit})</b>",
                            f"<b>MIN TEMP<br>(in{temp_unit})</b>",
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
            margin=dict(l=10, r=10, b=10, t=10),
            height=328,
        )
        st.plotly_chart(table1, use_container_width=True)

        table2 = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "<b>DATES</b>",
                            "<b>WEATHER CONDITION</b>",
                            "<b>WIND SPEED</b>",
                            "<b>PRESSURE<br>(in hPa)</b>",
                            "<b>SUNRISE</b>",
                            "<b>SUNSET</b>",
                        ],
                    ),
                    cells=dict(
                        values=[
                            dates,
                            description,
                            wind_speed,
                            pressure,
                            sunrise,
                            sunset,
                        ]
                    ),
                )
            ]
        )
        table2.update_layout(
            margin=dict(l=10, r=10, b=10, t=10),
            height=360,
        )
        st.plotly_chart(table2, use_container_width=True)

        st.markdown("Made By **Hafiz Muhammad Ubaid**")
        st.markdown("Partners Abdul Hadi And Abdullah Tanoli")

    except requests.exceptions.Timeout:
        st.error("Weather service timed out. Please try again.")
    except requests.exceptions.RequestException as exc:
        st.error(f"Weather service error: {exc}")
    except (KeyError, TypeError, ValueError):
        st.error("The weather service returned unexpected data.")


def page_about():
    set_background(
        "https://images.pexels.com/photos/207700/pexels-photo-207700.jpeg"
        "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    )

    st.title("📜 ABOUT")
    st.markdown(
        """
**MY WEATHER FORECAST SERVICE:**

Welcome to WEATHER FORECAST BY HMU ✪, your go-to destination for
weather forecasts.

**About the Creator**

**Hafiz Muhammad Ubaid**, the creator of WEATHER FORECAST BY HMU ✪,
is a passionate weather enthusiast dedicated to providing accessible
weather forecasts.

**My Mission**

Our mission is to provide users with up-to-date weather forecasts
tailored to their location and preferences.

**What Sets Us Apart**

- **Accuracy:** Real-time weather data from an external weather API.
- **Customization:** Temperature and wind-speed unit choices.
- **User-Friendly Interface:** Simple weather search and forecast display.

**Our Team**

Behind WEATHER FORECAST BY HMU ✪ is a dedicated project team working
to make weather information easy to access.

**Get in Touch**

We value feedback from our users and welcome questions and suggestions.
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
**CONTACT INFORMATION**

Group Leader: Muhammad Ubaid

Project Partners: Abdul Hadi And Abdullah Tanoli

**Instagram:** https://www.instagram.com/muhammadubaid__/

**LinkedIn:** https://www.linkedin.com/in/hafiz-muhammad-ubaid-2b88722b3/

**GitHub:** https://github.com/dashboard

**Email:** ubaidsajid2006@gmail.com

Remember, you can always contact the team through these accounts.
"""
    )


def main():
    st.sidebar.title("☰ MENU")
    page = st.sidebar.radio("Go to", ["Home", "About", "Contact"])

    # Optional local image. The app will still run if icc.jpg is not present.
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
         

     
        
        


                       

     
        
        
