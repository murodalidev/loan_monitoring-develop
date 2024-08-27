import redis
import json
import pickle
from .config import POSTGRES_HOST
rd = redis.Redis(host=POSTGRES_HOST, port=6379, db=0)





def cache_add(user_id, cache_type, response):
    dict_bytes = pickle.dumps(response)
    rd.set(f'{user_id}_{cache_type}', dict_bytes)
    rd.expire(f'{user_id}_{cache_type}', 14400)
    

def cache_get(user_id, cache_type):
    cached_data =  rd.get(f'{user_id}_{cache_type}')
    if cached_data:
        return pickle.loads(cached_data)
    else:
        return False