# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 10:58:47 2022

@author: rodra04
"""
import requests
import json
import pandas as pd



from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


import math


def get_weather(city, mode):
    
    if mode == 'normal':
        request = requests.get('https://api.oikolab.com/weather',params={
            'param': ['temperature',
                      'wind_speed',
                      'surface_solar_radiation',
                      'total_precipitation',
                      'relative_humidity'],
            'start': '2021-01-01',
            'end': '2021-12-31',
            'freq':'M',
            'resample_method':'mean',
            'location': city,
            'api-key': '7e0f551b1d5c40acb05b1c06fbcd8a91'}, verify = False)
        
        
    
        weather_data = json.loads(request.json()['data'])
        df = pd.DataFrame(index=pd.to_datetime(weather_data['index'], 
                                               unit='s'),
                          data=weather_data['data'],
                          columns=weather_data['columns'])
    
    elif mode == 'other':
        request = requests.get('https://api.oikolab.com/weather',params={
            'param': ['snowfall',
                      'dewpoint_temperature',
                      'surface_pressure',
                      'temperature',
                      'wind_speed'],
            'start': '2021-01-01',
            'end': '2021-12-31',
            'freq':'M',
            'resample_method':'mean',
            'location': city,
            'api-key': '7e0f551b1d5c40acb05b1c06fbcd8a91'}, verify = False)
        
        print(request)
    
        weather_data = json.loads(request.json()['data'])
        df = pd.DataFrame(index=pd.to_datetime(weather_data['index'], 
                                               unit='s'),
                          data=weather_data['data'],
                          columns=weather_data['columns'])
        
    return df

def solarOutput(COUNTRY, measurment, region):
   
    df = pd.read_excel('Sunlight Hours.xlsx')
    
    df.drop('Delete', axis=1, inplace=True)
    country = COUNTRY
    df_Country = df['Country']
    number_of_countries = len(df_Country)
    cities = []
    error = False
    solarPanelW = 400
    returnMessage = 'Country not found. Run function again'
    if region == None:
        
        
        
        
        #Start the function
        
        
        for i in range(number_of_countries):
            if df_Country[i] == country:
                cities.append(df['City'][i])
                l = i
                
        if len(cities) == 0:
            print('Country not found. Try again')
            return returnMessage
            
        while (error == False):
            if len(cities) > 1:
                return cities
            x = 0
            
            if len(cities) == 1:
                selectedCity = df['City'][l]
                return selectedCity
            
            
                
            else:
                error = True
    elif region != None:
        
        
        df_City = df["City"]
        for i in range(number_of_countries):
            if df_City[i] == region:
                sunlightHrs = df['Year'][i]
            
            
        
        energyProducedWatts = round((solarPanelW * sunlightHrs * 0.75) / 365, 2)
        energyProducedKilowatt = round(energyProducedWatts / 1000, 2) 
    
        if measurment == 'Watts' or measurment == 'watts':
            return [energyProducedWatts, 450]
        
        elif measurment == 'Kilowatts' or measurment == 'kilowatts':
            return [450, energyProducedKilowatt]
        
        else:
            return "Second arguement not typed in correctly"
    
def windOutput(getWeather_other):
    
    def airDensity(Templist, Dewlist, Pressurelist):
        
        import time
        #Converted list
        converted = []
        
        #Initialzing driver and putting in standard API key
        browser = webdriver.Chrome(ChromeDriverManager().install())
        
       #Launching browser
        browser.get('https://www.gribble.org/cycling/air_density.html')
        
        for i in range(2):
            print('Checking')
            time.sleep(1.5) 
        
        for i in range(len(Templist)):
            #Enter first input
            Temp_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[1]').clear()
            Temp_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[1]').send_keys(Templist[i])

            #Enter second input
            AirPressure_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[2]').clear()
            AirPressure_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[2]').send_keys(Pressurelist[i])

            #Enter third input
            DewPoint_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[3]').clear()
            DewPoint_press = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/input[3]').send_keys(Dewlist[i])

            #Get Air Density
            AirDensity = browser.find_element_by_xpath('/html/body/div[2]/div/main/div/div/div[2]/div/div/i[1]/b/span')
            converted.append(AirDensity.text)
        
        return converted
        
        browser.close()
    
    
    
    getWeather_other.drop(['coordinates (lat,lon)', 'model (name)', 'model elevation (surface)', 'utc_offset (hrs)'], axis=1, inplace=True)
    
    TempList = []
    DewList = []
    PressureList = []
    WindList = []
    
    titles = ['temperature (degC)', 'dewpoint_temperature (degC)', 'surface_pressure (Pa)', 'wind_speed (m/s)']
    
    for i in range(len(getWeather_other)):
        for x in range(len(titles)):
            if x == 0:
                TempList.append(getWeather_other[titles[x]][i])
            if x == 1:
                DewList.append(getWeather_other[titles[x]][i])
            if x == 2:
                PressureList.append(getWeather_other[titles[x]][i])
            if x == 3:
                WindList.append(getWeather_other[titles[x]][i])
                
    properPressure = []
    for i in range(len(PressureList)):
        properPressure.append(float(PressureList[i])/100 )
    

    densityList = airDensity(TempList, DewList, properPressure)
    

    radius = 45
    wind_speed = WindList
    air_density = densityList
    efficiency_factor = 0.4
    firstPower = []
    pi = math.pi
    
    #Calculate for all months
    for i in range(len(wind_speed)):
        firstPower.append((pi/2)*(radius**2)*(wind_speed[i]**3)*float(air_density[i])*efficiency_factor)
        firstPower[i] = firstPower[i]/1000
        
    #Calculate Daily Yield
    time = 24
    capacity_factor = 0.3
    power = firstPower
    dailyKilowatts = []
    
    for i in range(len(firstPower)):
        dailyKilowatts.append(power[i]*time*capacity_factor)    
    
    f = 0
    for i in range(len(dailyKilowatts)):
         f += dailyKilowatts[i]
    
    averageDaykW = f / len(dailyKilowatts)
    
    return [2640000, averageDaykW]

def waveOutput(COUNTRY):
    def areaFinder(lat, lon):
        from math import radians, cos, sin, asin, sqrt
        
        #Your location 
        you = [lat, lon]
        
        #Seas
        pacificOcean = [[50.017229, -157.454142], [50.017229, -138.063949], [37.126777, -127.498780], [21.943072, -116.365625], [-0.854523, -88.576626], [-24.195279, -77.194962], [-53.065385, -79.157711], [59.581580, 176.527807], [54.783140, 148.443182], [39.103622, 136.026821], [29.477912, 128.636130], [-17.340352, 157.016384], [-41.503182, 141.200305]]
        americanGap = [[27.886905, -92.834401], [26.572620, -84.556827], [11.380520, -81.087240], [13.269456, -71.946615], [20.001841, -80.296224]]
        atlanticOcean = [[74.172700, -68.259939], [60.032667, -55.457440], [66.980212, -26.745038], [66.488994, 7.087071], [47.237925, -48.284022], [47.237925, -48.284022], [36.298302, -72.202188], [9.980196, -52.986390], [-3.270415, -34.066222], [-23.973423, -39.535333], [-33.913335, -50.177928], [46.974038, -10.120384], [29.607518, -17.363261], [5.146262, -13.667916], [-12.484484, 7.912903], [-28.869042, 12.938573]]
        indianOcean = [[-30.873109, 32.855391], [-17.869403, 41.426043], [-0.084356, 46.547531], [22.226184, 63.688836], [5.759051, 77.590016], [19.885401, 89.714354], [-29.153624, 111.036466]]
        arcticOcean = [[71.616353, -146.368574], [77.452500, -122.638106], [81.663395, -96.270919], [82.779649, -60.235764], [83.879726, -32.462326], [81.325452, -5.040452], [80.750605, 19.920486], [70.059759, 41.429760], [74.620570, 62.699293], [78.336822, 93.812574], [75.393150, 119.828198], [76.665422, 142.503980], [71.224312, 168.519604]]
        balticSea = [[64.845805, 22.832865], [62.059280, 19.493021], [58.12042271394, 30.039896], [42.353098, 37.598490], [45.946025, 36.368021]]
        caspianSea = [[45.782670, 50.682801], [41.969803, 50.660613], [38.313083, 51.219945], [46.195079, 52.379618]]
        redSea = [[25.181786, 35.904735], [19.493959, 38.949990], [14.142173, 42.430281], [12.388043, 47.153533]]
        southChinaSea = [[8, 19.932475], [55.574179, 17.119975], [56.892979, 11.319193]]
        mediSea = [[38.816849, 2.002788], [39.498354, 10.703959], [38.266903, 19.668803], [33.718210, 16.416850], [36.662507, 25.996928], [35.740531, 31.358256], [32.243742, 25.557474]]
        blackSea = [ [7.635267, 104.212086], [-0.515854, 107.639820], [-2.624318, 117.835132], [9.893587, 120.471851], [-2.624318, 123.811695], [-9.524425, 129.964038], [18.823586, 107.376148], [42.418016, 33.731302]]
        
        waters = [pacificOcean, americanGap, atlanticOcean, indianOcean, arcticOcean, balticSea, caspianSea, redSea, southChinaSea, mediSea, blackSea]
        def haversine(lon1, lat1, lon2, lat2):
            """
            Calculate the great circle distance between two points 
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians 
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
            # haversine formula 
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles
            return c * r
        
        
        
        center_point = [{'lat': you[0], 'lng': you[1]}]
        closest = 100000000000000000000
        marker = 0
        
        for i in range(len(waters)):
            for x in range(len(waters[i])):
                test_point = [{'lat': waters[i][x][0], 'lng': waters[i][x][1]}]
                
                lat1 = center_point[0]['lat']
                lon1 = center_point[0]['lng']
                lat2 = test_point[0]['lat']
                lon2 = test_point[0]['lng']
                
                radius = 25.00 # in kilometer
                a = haversine(lon1, lat1, lon2, lat2)
                
                while radius < a:
                    radius += 5.00
                    
                if radius < closest:
                    closest = radius
                    marker = i


        #Stupid dumb dumb 'its blaaaack' hardcoded part not blaaaaaaaaaaaaaaaaaack
        if marker == 0:
            return('Pacific Ocean')
        elif marker == 1:
            return('American Gap')
        elif marker == 2:
            return('Atlantic Ocean')
        elif marker == 3:
            return('Indian Ocean')
        elif marker == 4:
            return('Arctic Ocean')
        elif marker == 5:
            return('Baltic Sea')
        elif marker == 6:
            return('Caspian Sea')
        elif marker == 7:
            return('Red Sea')
        elif marker == 8:
            return('South China Sea')
        elif marker == 9:
            return('Meditteranean Sea')
        elif marker == 10:
            return('Black Sea')
    
    
    country = COUNTRY
    
    
    dfEEZ = pd.read_excel('EEZ.xlsx')
    
    #Would normally return something here
    for i in range(len(dfEEZ)):
        if country in dfEEZ['Country'][i]:
            print("Country found")
            
    dfLL = pd.read_csv('landlocked.csv')
    
    markers = []
    for i in range(len(dfEEZ)):
        for x in range(len(dfLL)):
            if dfLL['country'][x] in dfEEZ['Country'][i]:
                markers.append(i)
                
    for i in range(len(markers)):
        dfEEZ.drop(markers[i], axis=0, inplace=True)
        
    dfEEZ = dfEEZ.reset_index()
    del dfEEZ['index']
    
    accept = False
    
    for i in range(len(dfEEZ)):
        if country in dfEEZ['Country'][i]:
            accept = True
    
    if accept:
        print('Everything okay')
        locStats = get_weather(country, 'normal')
        print(locStats)
        
        cityCoordinates = locStats['coordinates (lat,lon)'][0]
        
        cityCoordinates = cityCoordinates.strip('()')
        x = cityCoordinates.split(", ")
        lat = float(x[0])
        lon = float(x[1])
        coord = [lat, lon]
        
        returned = areaFinder(coord[0], coord[1])
        
        dPacific = [2.5, 33.80]   
        dAmerican = [1.6, 24.48]  
        dAtlantic = [3.0, 42.12]
        dIndian = [2.5, 20.88]  
        dArctic = [3.0, 32.4]
        dBaltic = [1.8, 34.05]  
        dCaspian = [0.9, 20.05]   
        dRed = [1.6, 31.55]  
        dChina = [2.2, 28.40]   
        dMedi = [2.7, 25.77]
        dBlack = [1.3, 24.26]    
        
        #list with all d
        dList = [dCaspian, dBlack, dRed, dAmerican, dBaltic, dChina, dIndian, dPacific, dMedi, dAtlantic, dArctic]
        
        #Rank the start points
        rankedStarts = {'Caspian Sea': dCaspian, 'Black Sea': dBlack, 'Red Sea': dRed, 'American Gap': dAmerican, 'Baltic Sea': dBaltic, 'South China Sea': dChina, 'Indian Ocean': dIndian, 'Pacific Ocean': dPacific, 'Meditteranean Sea': dMedi, 'Atlantic Ocean': dAtlantic, 'Arctic Ocean': dArctic}
        
        
        #Get parabola formula: y = a(x)**2+q
        convertedDic = list(rankedStarts)
        multiple = convertedDic.index(returned)
        
        q = ((multiple + 1) * 4.54)
        
        bottom_a = 1440 - ((q/4.54)*120)
        
        y = ((1/bottom_a)*(rankedStarts[returned][0])**2 + q)
        
        marker = 0 
        for i in range(len(rankedStarts)):
            if rankedStarts[convertedDic[i]] == returned:
                marker = i
            
        
        
        if dList[marker][1]<= 20:
            perS = 0.1
        
        elif dList[marker][1] <= 26 and dList[marker][1] > 20:
            perS = 0.07
            
        elif dList[marker][1] > 26:
            perS = 0.04
            
        #Finish Calculations
        perDay = perS * 86400
        
        return [2080944.73, (perDay * y)]
        
    else:
        print('Has no coast')
        return [2080944.73, 0]
        
    

#df = get_weather('Switzerland', 'other')
#a = windOutput(df)
#b = solarOutput('Spain', 'kilowatts')
#c = waveOutput('Switzerland')
