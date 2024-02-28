import orjson
from pydantic import BaseModel, Field
from typing import List, DefaultDict, Annotated
from datetime import date
from collections import defaultdict
from typing import List, DefaultDict
from enum import Enum

class Result(BaseModel):
    id: str
    title: str
    description: str
    url: str
    score: float
    timestamp: int
    
class NewsArticleData(BaseModel):
    title: str
    """Title of the news"""
    date: str
    """Date of the news YYYY/MM/DD"""
    doc_id: str
    """doc_id of the news"""
    content: str
    """Content of the news"""
    hypertext: DefaultDict[str, str]
    """Hyperlinks: key: hypertext content, value: image url"""
    figcaption: DefaultDict[str, str]
    """Figure caption: key: index, value: text caption"""
    url: str
    """Url of the news"""
    class Config:
        extra = 'ignore'
        
    def __init__(self, **data):
        if type(data["hypertext"]) == str:
            try:
                data["hypertext"] = orjson.loads(data["hypertext"].replace("'", '"'))
            except orjson.JSONDecodeError:
                print(f"Error in hypertext: {data['hypertext']}")
        if type(data["figcaption"]) == str:
            try:
                data["figcaption"] = orjson.loads(data["figcaption"].replace("'", '"'))
            except orjson.JSONDecodeError:
                print(f"Error in figcaption: {data['figcaption']}")
        super().__init__(**data)
    
class NewsArticlesFragment(BaseModel):
    """Used to represent single fragment of news data (per csv file)"""
    source: str
    """Name of the news source"""
    date: date
    """Crawling data for the fragment date"""
    index: int
    """Index of the fragment"""
    articles: List[NewsArticleData]
    """List of news articles"""

class NewsArticlesBatch(BaseModel):
    """Used to represent single batch of source/combined news articles for different sources"""
    doc_ids: List[int]
    """Document IDs of the news articles"""
    indices: DefaultDict[str, List[str]]
    """Indices of the news articles for each source"""
    fragments: DefaultDict[str, List[NewsArticlesFragment]]
    """Fragments of the news articles for each source"""
    

class InvertedIndexMetadata(BaseModel):
    document_size: int
    """Number of documents in the index"""
    doc_ids_list: List[int]
    """List of document IDs"""
    
def default_dict_list():
    return defaultdict(list)

class InvertedIndex(BaseModel):
    meta: InvertedIndexMetadata
    """Metadata of the index"""
    index: DefaultDict[str, Annotated[DefaultDict[str, List[int]], Field(default_factory=default_dict_list)]]
    """Inverted index key: term, value: dictionary of doc_id and list of positions"""
class RedisKeys:
    document_size = "meta:document_size"
    doc_ids_list = "meta:doc_ids_list"
    index = lambda term: f"w:{term}"
        

if __name__ == "__main__":
    json_string = """
    {
        "meta": {
            "document_size": 6,
            "doc_ids_list": [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6"
            ]
        },
        "index": {
            "yo": {
                "0": [1, 2, 3]
            },
            "lo": {
                "3": [1, 2, 3]
            }
        }
    }
    """
    index = InvertedIndex.model_validate_json(json_string)
    print(index)    