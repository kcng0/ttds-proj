import orjson
import redis
import os
import asyncio
import aioredis
import time
from tqdm import tqdm
from basetype import InvertedIndex, RedisKeys, RedisDocKeys, NewsArticleData
from typing import List
from typing import Dict

BASEPATH = os.path.dirname(__file__)

# redis_async_connection = None
redis_async_connection = {
    0: None, # for index
    1: None, # for document
    2: None, # for cache
}

redis_connection = None 
redis_config = None

def get_redis_config(env="prod", is_async=True, db=0):
    # pip install python-dotenv
    from dotenv import load_dotenv

    if env == "dev":
        cfg_path = os.path.join(BASEPATH, "redis_config_dev.env")
    else:
        cfg_path = os.path.join(BASEPATH, "redis_config_prod.env")

    load_dotenv(cfg_path)

    REDIS_HOST = os.environ.get("REDIS_HOST") or os.getenv("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT") or os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or os.getenv("REDIS_PASSWORD")

    if is_async:
        config_redis = {'address': (REDIS_HOST, REDIS_PORT), "password": REDIS_PASSWORD, "db":db}
    else:
        config_redis = {"host": REDIS_HOST, "port": REDIS_PORT, "password": REDIS_PASSWORD, "db":db}

    return config_redis

# Redis Functions
def initialize_sync_redis(db=0):
    global redis_connection
    try:
        if not redis_connection:
            config_redis = get_redis_config(is_async=False, db=db)
            redis_connection = redis.StrictRedis(**config_redis)
        else:
            redis_connection.ping()
    except (redis.ConnectionError, redis.RedisError, Exception):
        config_redis = get_redis_config(is_async=False, db=db)
        redis_connection = redis.StrictRedis(**config_redis)

async def initialize_async_redis(db=0):
    global redis_async_connection
    try:
        if not redis_async_connection[db]:
            config_redis = get_redis_config(db=db)
            redis_async_connection[db] = await aioredis.create_redis_pool(**config_redis)
        else:
            await redis_async_connection[db].ping()
    except (aioredis.ConnectionClosedError, aioredis.RedisError, aioredis.ConnectionForcedCloseError, Exception):
        config_redis = get_redis_config(db=db)
        redis_async_connection[db] = await aioredis.create_redis_pool(**config_redis)

# decorator to check if the redis connection is initialized
def do_check_redis_connection(db=0):
    def check_redis_connection(func):
        def wrapper(*args, **kwargs):
            initialize_sync_redis(db=db)
            return func(*args, **kwargs)
        return wrapper
    return check_redis_connection

# decorator to check if the async redis connection is initialized
def do_check_async_redis_connection(db=0):
    def check_async_redis_connection(func):
        async def wrapper(*args, **kwargs):
            await initialize_async_redis(db=db)
            return await func(*args, **kwargs)
        return wrapper
    return check_async_redis_connection

@do_check_redis_connection(db=0)
def update_doc_size(new_size, colname="meta:document_size"):
    doc_size = redis_connection.get(colname)

    if not (doc_size):
        doc_size = new_size
    else:
        doc_size = int(doc_size)
        doc_size += new_size

    redis_connection.set(colname, doc_size)
    return True

@do_check_async_redis_connection(db=0)
async def get_doc_size() -> int:
    doc_size = await redis_async_connection[0].get(RedisKeys.document_size)
    if doc_size:
        return int(doc_size)
    else:
        return 0
@do_check_async_redis_connection(db=1)
async def check_url_exist(url_) -> int:
    is_exist = await redis_async_connection[1].sismember(RedisKeys.urls, url_)
    return bool(is_exist)

@do_check_redis_connection(db=1)
def check_batch_urls_exist(urls) -> int:
    # Create a pipeline
    pipe = redis_connection.pipeline()

    # Add sismember commands for each value to the pipeline
    for url_ in urls:
        pipe.sismember(RedisKeys.urls, url_)

    results = pipe.execute()

    return results

@do_check_async_redis_connection(db=1)
async def get_doc_fields(doc_id: int, fields_list: List[str]) -> List[str]:
    results = await redis_async_connection[1].hmget(
        RedisKeys.document(doc_id),
        *fields_list
    )
    results = [result.decode() for result in results]
    return results

@do_check_async_redis_connection(db=1)
async def get_docs_fields(doc_ids: List[int], fields_list: List[str]) -> List[str]:
    keys = [RedisKeys.document(doc_id) for doc_id in doc_ids]
    
    pipe = redis_async_connection[1].pipeline()
    for key in keys:
        pipe.hmget(key, *fields_list)
    
    results = await pipe.execute()

    for idx, result in enumerate(results):
        results[idx] = {fields_list[i]: value.decode() for i, value in enumerate(result)}
    return results

@do_check_async_redis_connection(db=1)
async def get_doc_data(doc_id):
    result = await redis_async_connection[1].hgetall(
        RedisKeys.document(doc_id)
    )
    return {key.decode('utf-8'): value.decode('utf-8') for key, value in result.items()}

@do_check_async_redis_connection(db=0)
async def get_doc_info() -> int:
    doc_size = await redis_async_connection[0].get(RedisKeys.document_size)
    return int(doc_size)

@do_check_async_redis_connection(db=0)
async def get_doc_ids_list() -> List[int]:
    doc_ids_list = await redis_async_connection[0].get(RedisKeys.doc_ids_list)
    return orjson.loads(doc_ids_list)

@do_check_redis_connection(db=0)
def get_val(key):
    start_time = time.time()
    value = redis_connection.get(key)
    value = value.decode()
    value = eval(value)
    print(f"Time taken to get {key}: {time.time() - start_time}")
    return value



@do_check_async_redis_connection(db=0)
async def set_data(key, value):
    await redis_async_connection[0].set(key, value)

@do_check_async_redis_connection(db=0)
async def batch_push(batches):
    # Define keys and values to set
    for batch in tqdm(batches, desc="PUSH"):
        # Perform SET operations in parallel
        tasks = [set_data(key, value) for key, value in batch.items()]
        await asyncio.gather(*tasks)

@do_check_async_redis_connection(db=1)
async def set_news_data(article: NewsArticleData):
    # Get metadata
    # TODO: Update the sentiment and summary
    doc_title = article.title
    doc_url = article.url
    doc_id = RedisKeys.document(article.doc_id)
    doc_date = article.date
    doc_sentiment = 'positive'
    doc_summary = ".".join(article.content.split('.')[:3])
    doc_source = article.url.split('.')[1]

    # Set the values
    lua_script = f"""
        redis.call('hset', ARGV[1], '{RedisDocKeys.url}', ARGV[2])
        redis.call('hset', ARGV[1], '{RedisDocKeys.title}', ARGV[3])
        redis.call('hset', ARGV[1], '{RedisDocKeys.date}', ARGV[4])
        redis.call('hset', ARGV[1], '{RedisDocKeys.sentiment}', ARGV[5])
        redis.call('hset', ARGV[1], '{RedisDocKeys.summary}', ARGV[6])
        redis.call('hset', ARGV[1], '{RedisDocKeys.source}', ARGV[7])
        redis.call('sadd', '{RedisKeys.urls}', ARGV[2])
    """
    # Run the Lua script
    await redis_async_connection[1].eval(
        lua_script, 
        keys=[], 
        args=[
            doc_id, #1 
            doc_url, #2
            doc_title, #3
            doc_date, #4
            doc_sentiment, #5
            doc_summary, #6
            doc_source
            ]
        )
    
@do_check_async_redis_connection(db=1)
async def set_news_data_col(doc_id: str, colname: RedisDocKeys, value: str):
    await redis_async_connection[1].hset(doc_id, colname, value)

@do_check_async_redis_connection(db=1)
async def batch_push_news_data(news_batch):
    # Define keys and values to set
    tasks = []
    for _source in news_batch.fragments:
        if type(_source) != str:
            continue
        for fragment in news_batch.fragments[_source]:
            for article in fragment.articles:
                tasks.append(set_news_data(article))
    await asyncio.gather(*tasks)

@do_check_async_redis_connection(db=0)
async def update_index(inverted_index: InvertedIndex):
    tasks = []
    for term in inverted_index.index:
        tasks.append(update_index_term(term, inverted_index))
    await asyncio.gather(*tasks)
    
    doc_size = await redis_async_connection[0].get(RedisKeys.document_size) 
    doc_ids_list = await redis_async_connection[0].get(RedisKeys.doc_ids_list) 
    if not doc_size:
        doc_size = inverted_index.meta.document_size
    else:
        doc_size = int(doc_size) + inverted_index.meta.document_size

    
    if not doc_ids_list:
        doc_ids_list = inverted_index.meta.doc_ids_list
    else:
        doc_ids_list = orjson.loads(doc_ids_list)
        doc_ids_list.extend(inverted_index.meta.doc_ids_list)
    
    await redis_async_connection[0].mset({
        RedisKeys.document_size: doc_size,
        RedisKeys.doc_ids_list: orjson.dumps(doc_ids_list)
    })
            
async def update_index_term(term, inverted_index: InvertedIndex):
    db_value = await redis_async_connection[0].get(RedisKeys.index(term))
    if not db_value:
        db_value = {}
    else:
        db_value = orjson.loads(db_value)
    
    for doc_id, pos in inverted_index.index[term].items():
        db_value[doc_id] = pos
    
    await redis_async_connection[0].set(RedisKeys.index(term), orjson.dumps(db_value))
    
@do_check_async_redis_connection(db=0)
async def get_json_value(key: str) -> Dict:
    value = await redis_async_connection[0].get(key)
    return orjson.loads(value)

@do_check_async_redis_connection(db=0)
async def get_json_values(keys: List[str]) -> List[Dict]:
    values_list = await redis_async_connection[0].mget(*keys)
    values_list = [orjson.loads(value) for value in values_list]
    return values_list

@do_check_async_redis_connection(db=0)
async def get_idf_value(key: str) -> float:
    value = await redis_async_connection[0].get(key)
    return float(value)

@do_check_redis_connection(db=0)
def clear_redis():
    redis_connection.flushall()
    return True

@do_check_async_redis_connection(db=0)
async def is_key_exists(key):
    return await redis_async_connection[0].exists(key)

@do_check_async_redis_connection(db=2)
async def set_cache(key: str, value: str):
    print("Setting cache")
    # set expiration time to 5 minutes
    await redis_async_connection[2].setex(key, 300, value)

@do_check_async_redis_connection(db=2)
async def caching_query_result(method: str, query: str, result):
    key = f"{method}:{query}"
    # non-blocking set operation
    asyncio.create_task(set_cache(key, orjson.dumps(result)))

@do_check_async_redis_connection(db=2)
async def check_cache_exists(key: str):
    return await redis_async_connection[2].exists(key)

@do_check_async_redis_connection(db=2)
async def get_cache(key: str):
    asyncio.create_task(redis_async_connection[2].expire(key, 300))
    return orjson.loads(await redis_async_connection[2].get(key))
    

async def test():
    print(await get_json_values([RedisKeys.index('man'), RedisKeys.index("woman")]))
    

if __name__ == "__main__":
    # clear_redis()
    asyncio.run(test())
