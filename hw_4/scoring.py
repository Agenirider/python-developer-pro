import hashlib
import json
import redis
import random

r = redis.Redis()


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):

    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday if birthday is not None else "",
    ]

    encoded_key_parts = b','.join([str(part).encode('utf-8') for part in key_parts])
    key = "uid:" + hashlib.md5(encoded_key_parts).hexdigest()

    cashed_data = store.get(key)

    if cashed_data is not None:
        return cashed_data.decode('utf-8')

    else:
        score = 0

        if phone:
            score += 1.5
        if email:
            score += 1.5
        if birthday and gender:
            score += 1.5
        if first_name and last_name:
            score += 0.5

        # cache for 60 minutes
        store.set(key, score, ex = 60 * 60)

    return score


def get_interests(store, clients_id):

    result = {}
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]

    for cid in clients_id:

        key = "i:%s" % cid

        cashed_data = store.get(key)

        if cashed_data is not None:
            result.update({ str(cid) : cashed_data.decode('utf-8').split(',') })

        else: 
            data = random.sample(interests, 2)
            store.set(key, ','.join(data), ex = 60 * 60 )
            result.update({ str(cid) : data })
        
    return result
