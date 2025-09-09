from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import requests
import json
import os

# 读取密钥配置
SEARCH_API_KEY = os.getenv('BOCHAAI_API_KEY')
"""
api密钥在以下网站获取
https://bochaai.com/
"""

# Initialize FastMCP server
mcp = FastMCP("Internet-search")

@mcp.tool()
def InternetSearch(query,txt_count=5):
    """联网搜索对应问题的答案

    Args:
        query: 需要联网搜索的问题
    """
    headers = {
        "Authorization": f"Bearer {SEARCH_API_KEY}",  # 替换为你的实际 API Key
        "Content-Type": "application/json"
    }

    payload = {
        "query": f"{query}",
        "freshness": "noLimit",
        "count": txt_count,
        "answer": False,
        "stream": False
    }

    Webtxt=""

    try:
        print("开始联网搜索")
        response = requests.post(
            "https://api.bochaai.com/v1/ai-search",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # 检查 HTTP 错误 
        i=0
        for value in json.loads((response.json()["messages"][0]["content"]))["value"]:
            Webtxt=Webtxt+f"参考资料id：{i}\n"+value["summary"]+"\n"
            i+=1
        #为了兼容web-search添加的代码
        # for value in response.json()["data"]["webPages"]["value"]:
        #     Webtxt=Webtxt+f"参考资料id：{i}\n"+value["snippet"]+"\n"
        #     i+=1
         # 解析并叠加响应
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except ValueError as e:
        print(f"Failed to parse JSON response: {e}")
    return Webtxt

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')