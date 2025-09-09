from serptool import SearchTool
from serptool.search_tool import SearchResponse


res: SearchResponse = SearchTool.baidu_search("你好")
print(res)

res: SearchResponse = SearchTool.google_search("coffee")
print(res)

