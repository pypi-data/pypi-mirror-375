from se import SearchTool
from se.search_tool import SearchResponse


res: SearchResponse = SearchTool.baidu_search("coffee")
print(res)

res: SearchResponse = SearchTool.google_search("coffee")
print(res)

