import streamlit as st
import requests
import datetime
from plotly import graph_objects as go


def page_home():
    st.title("🌤️ WEATHER FORECAST BY HMU")

    city = st.text_input("Enter City Name", "Karachi")

    if st.button("Get Weather"):
        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url)
            data = response.json()

            current = data["current_condition"][0]

            st.subheader(f"Weather in {city}")

            st.write("🌡️ Temperature:", current["temp_C"], "°C")
            st.write("🤔 Feels Like:", current["FeelsLikeC"], "°C")
            st.write("💧 Humidity:", current["humidity"], "%")
            st.write("💨 Wind Speed:", current["windspeedKmph"], "km/h")
            st.write("☁️ Condition:", current["weatherDesc"][0]["value"])

        except Exception as e:
            st.error(f"Error: {e}")


def page_about():
    st.title("About")
    st.write("Weather Forecast App by HMU")
