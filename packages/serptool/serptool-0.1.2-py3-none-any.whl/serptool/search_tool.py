from typing import Optional
from pydantic import BaseModel
from serpapi import GoogleSearch,BaiduSearch
from dotenv import load_dotenv
import os
load_dotenv()

assert os.environ['SERP_API_KEY'], "you shoule first set SERP_API_KEY env variable"
api_key: str = os.environ['SERP_API_KEY']


class SearchItem(BaseModel):
    position: int
    link: str
    snippet: Optional[str] = None


class SearchResponse(BaseModel):
    items: list[SearchItem]


class SearchTool:
    def __init__(self) -> None:
        pass

    @staticmethod
    def baidu_search(query: str) -> SearchResponse:
        search = BaiduSearch({"q": query,"api_key": api_key})
        data = search.get_dict()
        return SearchResponse(items=data['organic_results'])
    
    @staticmethod
    def google_search(query: str) -> SearchResponse:
        params = {
            "q": query,
            "location": "Austin, Texas, United States",
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": api_key
        }
        search = GoogleSearch(params)
        data = search.get_dict()
        return SearchResponse(items=data['organic_results'])