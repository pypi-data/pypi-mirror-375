# Internetsearch-mcp-server

- [English README](README.en.md)

一个用于联网搜索的MCP服务器
基于博查搜索API的MCP服务器  
需要使用博查AI的搜索服务密钥，具体文档请查阅[博查开发文档](https://bocha-ai.feishu.cn/wiki/HmtOw1z6vik14Fkdu5uc9VaInBb).

**如何使用**  
1、将仓库git clone
```bash
git clone https://github.com/mingdedi/Internetsearch-mcp-server.git
```
2、使用uv重建环境
```bash
cd Internetsearch-mcp-server
pip install uv
uv venv
./.venv/Scripts/activate.bat
uv sync
```
3、在配置文件中添加，类似格式如下
```json
{
  "mcpServers": {
    "Internetsearch-mcp-server": {
      "description": "Internetsearch-mcp-server",
      "command": "uv",
      "args": [
        "--directory",
        "/path/Internetsearch-mcp-server",
        "run",
        "Internet_search.py"
      ],
      "env": {
        "BOCHAAI_API_KEY": "sk-123456789412345678312323456789e"
      }
    }
  }
}
```

**注意**  
这里的BOCHAAI_API_KEY中的密钥仅仅是一个示例。  
如果想要获取一个实际可用的密钥请访问[博查AI](https://bochaai.com/)
