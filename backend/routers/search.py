from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from os.path import basename
from os import getenv
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from utils.basetype import Result
from utils.query_engine import boolean_test, ranked_test
from utils.redis_utils import caching_query_result, get_cache, get_docs_fields, check_cache_exists
from utils.basetype import RedisKeys, RedisDocKeys
from math import ceil

router = APIRouter(
    prefix=f"/{basename(__file__).replace('.py', '')}",
    tags=[basename(__file__).replace('.py', '')],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


class SearchResponse(BaseModel):
    results: list[Result]
    truth_value: float

@router.get("/")
async def search(
    q: str = Query(..., description="Search query", min_length=1, max_length=1024),
    year: Optional[int] = Query(None, description="Year of the result", ge=1900, le=2100),
    page: Optional[int] = Query(1, description="Page number", ge=1),
    limit: Optional[int] = Query(10, description="Results per page", ge=1, le=100)) -> SearchResponse:
    r'''
    Searching the results from the database.
    ```
        - q: query to search
        - page: page number
        - limit: results per page
    ```
    '''
    ## Search the results
    return ORJSONResponse(content={"results": ['123213'], "truth_value": 0.0})

class TestBody(BaseModel):
    field: str = Field(..., description="Test field", min_length=1, max_length=1024)
@router.post("/test")
async def test(body: TestBody):
    test_env = getenv("TESTING", "default")
    return ORJSONResponse(content={"field": body.field, "env": test_env})

@router.get("/boolean")
async def boolean_search(
    q: str = Query(..., description="Search query", min_length=1, max_length=1024),
    page: Optional[int] = Query(1, description="Page number", ge=1),
    limit: Optional[int] = Query(10, description="Results per page", ge=1, le=100)):
    r'''
    Searching the results from the database.
    ```
        - q: query to search (Must be a boolean query with AND, OR, NOT, brackets, proximity, exact match and word match)
        - page: page number (default: 1)
        - limit: results per page (default: 10)
    ```
    '''
    def pagination(results):
        """Function to get a particular page
        """
        response = {
            "results": results[0][(page-1)*limit:page*limit],
            "total_pages": ceil(len(results[0])/limit)
        }
        return response

    # uncomment this when the caching is ready
    if await check_cache_exists(RedisKeys.cache("boolean", q)):
        results = await get_cache(RedisKeys.cache("boolean", q))
        response = pagination(results)
        return ORJSONResponse(content=response)
    
    results = await boolean_test([q])
    if not results or len(results) > page*limit:
        return []
    
    # uncomment this if the document info is ready
    for idx, doc_id_list in enumerate(results):
        results[idx] = await get_docs_fields(doc_id_list, 
                                             [RedisDocKeys.title, 
                                              RedisDocKeys.url, 
                                              RedisDocKeys.source, 
                                              RedisDocKeys.date, 
                                              RedisDocKeys.sentiment, 
                                              RedisDocKeys.summary])

    response = pagination(results)
    await caching_query_result("boolean", q, results)
    
    return ORJSONResponse(content=response)

@router.get("/tfidf")
async def tfidf_search(
    q: str = Query(..., description="Search query", min_length=1, max_length=1024),
    page: Optional[int] = Query(1, description="Page number", ge=1),
    limit: Optional[int] = Query(10, description="Results per page", ge=1, le=100)):
    r'''
    Searching the results from the database.
    ```
        - q: query to search (Treat every word as a seperated term)
        - page: page number
        - limit: results per page
    ```
    '''

    def pagination(results):
        """Function to get a particular page
        """
        response = {
            "results": results[0][(page-1)*limit:page*limit],
            "total_pages": ceil(len(results[0])/limit)
        }
        return response

    if await check_cache_exists(RedisKeys.cache("tfidf", q)):
        results = await get_cache(RedisKeys.cache("tfidf", q))
        response = pagination(results)
        return ORJSONResponse(content=response)
    
    results = await ranked_test([q])
    
    for idx, result in enumerate(results):
        doc_id_list = [t[0] for t in result]
        doc_info_list = await get_docs_fields(doc_id_list,
                                                [RedisDocKeys.title, 
                                                RedisDocKeys.url, 
                                                RedisDocKeys.source, 
                                                RedisDocKeys.date, 
                                                RedisDocKeys.sentiment, 
                                                RedisDocKeys.summary,
                                                RedisDocKeys.topic])
        results[idx] = [{"score": t[1], **doc_info_list[i]} for i, t in enumerate(result)]
        
    if not results or len(results) > page*limit:
        return []

    response = pagination(results)
    
    await caching_query_result("tfidf", q, results)
    
    return ORJSONResponse(content=response)