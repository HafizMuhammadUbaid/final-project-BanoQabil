import streamlit as st
st.set_page_config(
    page_title="WEATHER FORECAST BY HMU ✪",
    page_icon= "cloud",
)

def page_home():
    
    import pages
    import streamlit as st
    import datetime,requests
    from plotly import graph_objects as go
    from streamlit_option_menu import option_menu

    def add_bg_from_url():
     st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1536244636800-a3f74db0f3cf?q=80&w=1992&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
    )

    add_bg_from_url() 

    
    st.title("WEATHER FORECAST BY HMU⚡")

    city=st.text_input("ENTER THE NAME OF THE CITY ")

    unit=st.selectbox("SELECT TEMPERATURE UNIT ",["Celsius","Fahrenheit"])

    speed=st.selectbox("SELECT WIND SPEED UNIT ",["Metre/sec","Kilometre/hour"])

    graph=st.radio("SELECT GRAPH TYPE ",["Bar Graph","Line Graph"])

   


    if unit=="Celsius":
           temp_unit=" °C"
    else:
         temp_unit=" °F"
    
    if speed=="Kilometre/hour":
        wind_unit=" km/h"
    else:
     wind_unit=" m/s"

    api="9b833c0ea6426b70902aa7a4b1da285c"
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}"
    response=requests.get(url)
    x=response.json()
    
    if(st.button("SUBMIT")):
     try:
        lon=x["coord"]["lon"]
        lat=x["coord"]["lat"]
        ex="current,minutely,hourly"
        url2=f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={ex}&appid={api}'
        res=requests.get(url2)
        y=res.json()

        maxtemp=[]
        mintemp=[]
        pres=[]
        humd=[]
        wspeed=[]
        desc=[]
        cloud=[]
        rain=[]
        dates=[]
        sunrise=[]
        sunset=[]
        cel=273.15
        
        for item in y["daily"]:
            
            if unit=="Celsius":
                maxtemp.append(round(item["temp"]["max"]-cel,2))
                mintemp.append(round(item["temp"]["min"]-cel,2))
            else:
                maxtemp.append(round((((item["temp"]["max"]-cel)*1.8)+32),2))
                mintemp.append(round((((item["temp"]["min"]-cel)*1.8)+32),2))

            if wind_unit=="m/s":
                wspeed.append(str(round(item["wind_speed"],1))+wind_unit)
            else:
                wspeed.append(str(round(item["wind_speed"]*3.6,1))+wind_unit)

            pres.append(item["pressure"])
            humd.append(str(item["humidity"])+' %')
            
            cloud.append(str(item["clouds"])+' %')
            rain.append(str(int(item["pop"]*100))+'%')

            desc.append(item["weather"][0]["description"].title())

            d1=datetime.date.fromtimestamp(item["dt"])
            dates.append(d1.strftime('%d %b'))
            
            sunrise.append( datetime.datetime.utcfromtimestamp(item["sunrise"]).strftime('%H:%M'))
            sunset.append( datetime.datetime.utcfromtimestamp(item["sunset"]).strftime('%H:%M'))

        def bargraph():
            fig=go.Figure(data=
                [
                go.Bar(name="Maximum",x=dates,y=maxtemp,marker_color='crimson'),
                go.Bar(name="Minimum",x=dates,y=mintemp,marker_color='navy')
                ])
            fig.update_layout(xaxis_title="Dates",yaxis_title="Temperature",barmode='group',margin=dict(l=70, r=10, t=80, b=80),font=dict(color="white"))
            st.plotly_chart(fig)
        
        def linegraph():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=mintemp, name='Minimum '))
            fig.add_trace(go.Scatter(x=dates, y=maxtemp, name='Maximimum ',marker_color='crimson'))
            fig.update_layout(xaxis_title="Dates",yaxis_title="Temperature",font=dict(color="white"))
            st.plotly_chart(fig)
            
        icon=x["weather"][0]["icon"]
        current_weather=x["weather"][0]["description"].title()
        
        if unit=="Celsius":
            temp=str(round(x["main"]["temp"]-cel,2))
        else:
            temp=str(round((((x["main"]["temp"]-cel)*1.8)+32),2))
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("## Current Temperature ")
        with col2:
            st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png",width=70)

        
        col1, col2= st.columns(2)
        col1.metric("TEMPERATURE",temp+temp_unit)
        col2.metric("WEATHER",current_weather)
        st.subheader(" ")
        
        if graph=="Bar Graph":
            bargraph()
            
        elif graph=="Line Graph":
            linegraph()

         
        table1=go.Figure(data=[go.Table(header=dict(
                  values = [
                  '<b>DATES</b>',
                  '<b>MAX TEMP<br>(in'+temp_unit+')</b>',
                  '<b>MIN TEMP<br>(in'+temp_unit+')</b>',
                  '<b>CHANCES OF RAIN</b>',
                  '<b>CLOUD COVERAGE</b>',
                  '<b>HUMIDITY</b>'],
                  line_color='black', fill_color='royalblue',  font=dict(color='white', size=14),height=32),
        cells=dict(values=[dates,maxtemp,mintemp,rain,cloud,humd],
        line_color='black',fill_color=['paleturquoise',['palegreen', '#fdbe72']*7], font_size=14,height=32
            ))])

        table1.update_layout(margin=dict(l=10,r=10,b=10,t=10),height=328)
        st.write(table1)
        
        table2=go.Figure(data=[go.Table(columnwidth=[1,2,1,1,1,1],header=dict(values=['<b>DATES</b>','<b>WEATHER CONDITION</b>','<b>WIND SPEED</b>','<b>PRESSURE<br>(in hPa)</b>','<b>SUNRISE<br>(in UTC)</b>','<b>SUNSET<br>(in UTC)</b>']
                  ,line_color='black', fill_color='royalblue',  font=dict(color='white', size=14),height=36),
        cells=dict(values=[dates,desc,wspeed,pres,sunrise,sunset],
        line_color='black',fill_color=['paleturquoise',['palegreen', '#fdbe72']*7], font_size=14,height=36))])
        
        table2.update_layout(margin=dict(l=10,r=10,b=10,t=10),height=360)
        st.write(table2)
        
        st.header(' ')
        st.header(' ')
        st.markdown("Made By **Hafiz Muhammad Ubaid** ")
    
 
     except KeyError:
        st.error(" Invalid city!!  Please try again !!")



def page_about():
 st.title("📜ABOUT")
 
 def add_bg_from_url():
     st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.pexels.com/photos/207700/pexels-photo-207700.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
    )
 
 add_bg_from_url() 
    
 
 st.markdown(
    """
      
 **MY  WEATHER  FORECAST  SERVICE :**

 Welcome to WEATHER FORECAST BY HMU ✪, your go-to destination for accurate and reliable weather forecasts. At WEATHER FORECAST BY HMU ✪, we understand the importance of staying informed about weather conditions, whether you're planning a weekend getaway, scheduling outdoor activities, or simply staying prepared for the day ahead.

 **About the Creator**

 **Hafiz Muhammad Ubaid** , the creator of [WEATHER FORECAST BY HMU ✪], is a passionate weather enthusiast dedicated to providing accurate and accessible weather forecasts to users worldwide.

 **My Mission**

 Our mission is to provide users with up-to-date and precise weather forecasts tailored to their specific location. We aim to empower individuals and businesses with the information they need to make informed decisions, enhance safety measures, and optimize their plans based on weather conditions.

 **What Sets Us Apart**

  **Accuracy**: My forecasts are backed by advanced meteorological models and real-time data sources, ensuring the highest level of accuracy.
  
  **Customization**: We offer personalized weather forecasts based on your location, preferences, and specific interests, providing you with relevant and actionable information.
  
 **User-Friendly Interface**: My website is designed with simplicity and ease of use in mind, making it effortless for users to access the weather information they need, when they need it.

 **Our Team**

 Behind WEATHER FORECAST BY HMU ✪ is a dedicated team of meteorologists, data analysts, and web developers who are passionate about delivering top-notch weather forecasting services. With years of experience in the field, our team works tirelessly to ensure that our users receive the most reliable and timely weather information.

 **Get in Touch**

 We value feedback from our users as it helps us improve our services. If you have any questions, suggestions, or concerns, please don't hesitate to contact us. You can reach out to our team via email, phone, or through our website's contact form.

 Thank you for choosing [WEATHER FORECAST BY HMU ✪] for your weather forecast needs. We look forward to serving you and helping you stay ahead of the weather!
 """
)




 

 



def Page_contact():
 st.title("📩CONTACT")
 def add_bg_from_url():
     st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://w0.peakpx.com/wallpaper/117/681/HD-wallpaper-wood-ahsap-black-brown-dark-lumber-madera-papers-wall-woods.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
    )
 
 add_bg_from_url() 
 st.markdown(
    """
  **CONTACT INFORMATION**:

 **Instagram**: https://www.instagram.com/muhammadubaid__?igsh=eWV4ejI1MXh0Mndr

 **LinkedIn**: https://www.linkedin.com/in/hafiz-muhammad-ubaid-2b88722b3/ 

 **GitHub**: https://github.com/dashboard

 **Email**: ubaidsajid2006@gmail.com.

 Remember, you can always contact me directly through these Accounts. I're eager to hear from you!



 """
)
 

def main():
    st.sidebar.title("☰MENU")
    page = st.sidebar.radio("Go to", options=["Home","About","Contact"])
    
    


    if page =="Home":
       page_home()
    elif page == "About":
       page_about()
    elif page == "Contact":
       Page_contact()

if __name__ == "__main__":
    main()
                       

     
        
        



       
        
        

