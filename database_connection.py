import json
from pymongo import MongoClient
from pymongo.results import InsertManyResult
from typing import List, Dict, Union

client = MongoClient("mongodb://localhost:27017")
db = client["meteo"]

def find_many(table_name:str, filter:Dict={}) -> List[Dict]:
    collection = db[table_name]
    result = collection.find(filter)
    return result.to_list()
    
def insert(table_name:str, data:Dict[str, any]) -> InsertManyResult:
    collection = db[table_name]
    try :
        collection.insert_one(data)
    except :
        print(f'WARN : {data.get('_id')} : duplicate key')
# <>
