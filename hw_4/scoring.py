import hashlib
import random

import redis


def is_redis_available(store):
    try:
        store.ping()
        return True
    except (
            redis.exceptions.ConnectionError,
            ConnectionRefusedError,
            redis.exceptions.TimeoutError,
    ):
        return False
    return False


def get_store():
    try:
        store = redis.Redis("127.0.0.1", socket_connect_timeout=1, port=6379, db=0)
        return store
    except (redis.exceptions.ConnectionError, ConnectionRefusedError, redis.exceptions.TimeoutError):
        print('REDIS CONNECTION ERROR')
        raise
    except:
        raise


def get_data_from_db(key):
    store = get_store()
    cashed_data = store.get(key)
    return cashed_data


def get_data_from_cache(key):
    store = get_store()
    cashed_data = store.get(key)
    return cashed_data


def save_data_to_cache(key, data):
    store = get_store()
    store.set(key, data, ex=60 * 60)
    return True


def score_generator(phone, email, birthday, gender, first_name, last_name):
    score = 0

    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5

    return score


def get_score(phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday if birthday is not None else "",
    ]

    encoded_key_parts = b','.join([str(part).encode('utf-8') for part in key_parts])
    key = "uid:" + hashlib.md5(encoded_key_parts).hexdigest()

    try:
        cashed_data = get_data_from_cache(key)

        if cashed_data is not None:
            return cashed_data.decode('utf-8')

        else:
            score = score_generator(phone, email, birthday, gender, first_name, last_name)

            # cache for 60 minutes
            save_data_to_cache(key, score)

    except redis.exceptions.TimeoutError:
        score = score_generator(phone, email, birthday, gender, first_name, last_name)

    return score


def get_interests(clients_id):
    result = {}
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]

    for cid in clients_id:

        key = "i:%s" % cid

        try:
            cashed_data = get_data_from_cache(key)

            if cashed_data is not None:
                result.update({str(cid): cashed_data.decode('utf-8').split(',')})

            else:
                data = random.sample(interests, 2)
                save_data_to_cache(key, ','.join(data))
                result.update({str(cid): data})

        except redis.exceptions.TimeoutError:
            data = random.sample(interests, 2)
            result.update({str(cid): data})

    return result
