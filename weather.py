#############################################################################################################
#############################################################################################################
#############################################################################################################
######                                                                                                 ###### 
######      For questions concerning the lecture plan pls contact @lara_anastasia on discord           ######
######                                                                                                 ######
#############################################################################################################
#############################################################################################################
#############################################################################################################


import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import xlwings as xw
import discord
from datetime import datetime

def feature(plz:str):
    raw_data= getcordinats(plz)
    data= getweather(raw_data[1],raw_data[2])
    date=data["date"].tolist()
    max=data["maximum"].tolist()
    min=data["minimum"].tolist()
    dates_clean= [datetime.strftime(ts, '%d-%m-%Y') for ts in date]
    #formating
    max_clean= ["{:.2f}".format(number) for number in max]
    min_clean= ["{:.2f}".format(number) for number in min]
    #remove the first entry, scince it is the dates for yesterday 
    dates_clean.pop(0)
    max_clean.pop(0)
    min_clean.pop(0)
    x=make_embed(dates_clean,max_clean,min_clean)
    return x




def make_embed(times,maximum,minimum):
    embed = discord.Embed(title="Weather Forecast", color=0xD9A4FC) 
    embed.set_footer(text="‎",icon_url="https://cdn.discordapp.com/attachments/1179867724592193637/1202193113389473832/image.png?ex=65cc9095&is=65ba1b95&hm=dddcb13b59f2772b6b4b352884d8c9424eea27a426e6ac544f854addb88a2ff1&" ) 
    for i in range(len(times)):
        embed.add_field(name=times[i], value=f"{'-'*15}\nMin: {minimum[i]}°C\nMax: {maximum[i]}°C\n {'-'*15}", inline=True)
        
        
    return embed


def getcordinats(plz:str):
    ws= xw.Book("plzdoc.xlsx").sheets["Sheet1"]
    #read only the plz to enable index searching
    halfdata=ws['A2:A8299'].options(ndim=1).value
    fulldata = ws.range("A2:C8299").value
    index= halfdata.index(plz)
    x= fulldata[index]
    return x

#disclamer 
#following code was given by the weather API (AI generator inside the API documentation)- I made minimal changes to it to fit our project 
def getweather(lat,long):
    x=lat
    y=long
# Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/dwd-icon"
    params = {
	"latitude": x,
	"longitude": y,
	"current": "temperature_2m",
	"daily": ["temperature_2m_max", "temperature_2m_min"],
	"timezone": "Europe/Berlin"
}
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()

    print(f"Current time {current.Time()}")
    print(f"Current temperature_2m {current_temperature_2m}")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(),unit="s").normalize(),
        end = pd.to_datetime(daily.TimeEnd(),unit="s").normalize(),
        inclusive = "left"
    )}
    daily_data["maximum"] = daily_temperature_2m_max
    daily_data["minimum"] = daily_temperature_2m_min
    return daily_data

