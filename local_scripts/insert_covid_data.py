import os
import time
import COVID19Py
from mysql.connector import connect

def get_covid_data_by_country(countrie_cody: str = 'BR'):
    covid19 = COVID19Py.COVID19(url="https://cvtapi.nl")
    dict_data = covid19.getLocationByCountryCode(countrie_cody, timelines=True)[0]
    latitude = dict_data['coordinates']['latitude']
    longitude = dict_data['coordinates']['longitude']
    confirmed_timelines = dict_data['timelines']['confirmed']['timeline']
    deaths_timelines = dict_data['timelines']['deaths']['timeline']
    for time in confirmed_timelines:
        try:
            yield {'timestamp': time ,'country_code': countrie_cody, 'latitude': latitude,
                'longitude': longitude, 'acumulated_confirmed_cases': confirmed_timelines[time],
                'acumulated_deaths': deaths_timelines[time]}
        except KeyError:
            yield {'timestamp': time ,'country_code': countrie_cody, 'latitude': latitude,
                'longitude': longitude, 'acumulated_confirmed_cases': confirmed_timelines[time],
                'acumulated_deaths': 0}

rdsdb = connect(host=os.environ["RDS_HOST"], user=os.environ["RDS_USER"], password=os.environ["RDS_PASSWORD"], database="covid_cases", port=5432)
print('Conectado')
cursor = rdsdb.cursor()
initial_query = """CREATE TABLE IF NOT EXISTS covid_timeline(measured_at datetime, country_code varchar(10), latitude float, longitude float, acumulated_confirmed_cases integer, acumulated_deaths integer)"""
cursor.execute(initial_query)

if __name__ == "__main__":
    for data in get_covid_data_by_country("US"):
        print(data)
        query = f"""INSERT INTO covid_timeline(measured_at, country_code, latitude, longitude, acumulated_confirmed_cases, acumulated_deaths)
                    VALUES ('{data["timestamp"]}', '{data["country_code"]}', {data['latitude']}, {data['longitude']}, {data['acumulated_confirmed_cases']}, {data['acumulated_deaths']})"""
        cursor.execute(query)
        time.sleep(0.2)