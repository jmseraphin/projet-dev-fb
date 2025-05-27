from fastapi import FastAPI
from  typing import Union, Dict
from database_connection import find_many, insert
from get_weather_data import get_weather_data
from fastapi.middleware.cors import CORSMiddleware

origins = ['*']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/get-weather-date/city={city}&units={units}&date={date}")
def get_weather_by_date(city:str, units:str, date:str):
    response = get_weather_from_database(city, units, "Days", filter={
            '_id': date + ' ' + city,
            'city': city
        })
    try :
        return_value = response[0]
        return {"main": return_value}
    except IndexError :
        return {"main": {}}


@app.get("/get-weather-hour/city={city}&units={units}&date={date}&time={time}")
def get_weather_by_hour(city:str, units:str, date:str, time:str):
    response = get_weather_from_database(city, units, "Hours", filter={
        '_id': date + ' ' + time + ' ' + city,
        'city': city
    })
    try :
        return_value = response[0]
        return {"main": return_value}
    except IndexError :
        return {"main": {}}

def get_weather_from_database(city:str, units:str, type_:Union["Days", "Hours"], filter:Dict={}):
    days_data = find_many(type_, filter=filter)
    if len(days_data) == 0:
        fetch_and_insert(city, units)
    return find_many(table_name=type_, filter=filter)

    
def fetch_and_insert(city, units:str='metric'):
    weather_data = get_weather_data(
        city=city,
        units=units,
    )
    main_data = weather_data.get('main')
    for date in main_data:
        hourly_data = date.pop('three-hourly')
        date.update({
            '_id': date.get('date') + ' ' + city,
            'city': city
        })
        insert('Days', date)
        for hour in hourly_data:
            hour['_id'] = date['date'] + ' ' + hour['time']+ ' ' + city
            hour['city'] = city
            insert('Hours', hour)
