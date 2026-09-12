import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="WEATHER FORECAST BY HAFIZ MUHAMMAD UBAID", layout="wide")

# FontAwesome Icons CDN link for clean vector SVG icons
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    /* Styling for custom contact icons */
    .social-icon {
        font-size: 28px;
        margin-right: 15px;
        text-decoration: none;
        color: white !important;
        transition: transform 0.2s ease-in-out;
    }
    .social-icon:hover {
        transform: scale(1.2);
    }
    .fa-instagram {
        background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%,#d6249f 60%,#285AEB 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
    }
    .fa-linkedin { color: #0A66C2 !important; }
    .fa-envelope { color: #EA4335 !important; }
    </style>
""", unsafe_allow_html=True)

# Navigation without Emojis
nav_selection = st.sidebar.radio("NAVIGATION", ["Home", "About", "Contact"])

if nav_selection == "Home":
    st.title("WEATHER FORECAST")
    st.caption("By Hafiz Muhammad Ubaid")

    col1, col2, col3 = st.columns(3)
    with col1:
        # Strip string to eliminate trailing whitespace errors
        city_input = st.text_input("SEARCH CITY", value="Karachi")
        city = city_input.strip()
    with col2:
        temp_unit = st.selectbox("TEMPERATURE UNIT", ["Celsius (°C)", "Fahrenheit (°F)"])
    with col3:
        wind_speed_unit = st.selectbox("WIND SPEED", ["km/h", "m/s", "mph"])

    if st.button("GET LIVE ACCURATE FORECAST 🔍"):
        if city:
            try:
                # Open-Meteo Geocoding API for free city lookup
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
                geo_res = requests.get(geo_url).json()

                if "results" in geo_res and len(geo_res["results"]) > 0:
                    lat = geo_res["results"][0]["latitude"]
                    lon = geo_res["results"][0]["longitude"]
                    country = geo_res["results"][0].get("country", "")

                    # Weather API Call
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                    w_res = requests.get(weather_url).json()
                    
                    if "current_weather" in w_res:
                        curr = w_res["current_weather"]
                        temp = curr["temperature"]
                        
                        if "Fahrenheit" in temp_unit:
                            temp = (temp * 9/5) + 32
                            
                        st.success(f"Current Temperature in {city.title()}, {country}: **{temp:.1f}**")
                    else:
                        st.error(f"Could not fetch accurate weather for '{city}'. Please check the spelling.")
                else:
                    st.error(f"Could not fetch accurate weather for '{city}'. Please check the spelling.")
            except Exception as e:
                st.error("Network error. Please try again later.")
        else:
            st.warning("Please enter a city name.")

    if st.button("Reset / Search Another City"):
        st.experimental_rerun()

elif nav_selection == "About":
    st.title("About Weather Forecast App")
    st.write("This app provides accurate, real-time weather information globally.")

elif nav_selection == "Contact":
    st.title("Contact Hafiz Muhammad Ubaid")
    st.write("Feel free to reach out via my official social profiles:")
    
    # VIP Vector round icons using FontAwesome HTML
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 20px; margin-top: 20px;">
            <a href="https://linkedin.com" target="_blank" class="social-icon"><i class="fa-brands fa-linkedin fa-2x"></i></a>
            <a href="https://instagram.com" target="_blank" class="social-icon"><i class="fa-brands fa-instagram fa-2x"></i></a>
            <a href="mailto:example@gmail.com" target="_blank" class="social-icon"><i class="fa-solid fa-envelope fa-2x"></i></a>
        </div>
    """, unsafe_allow_html=True)
