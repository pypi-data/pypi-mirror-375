## 在 claude 客户端上安装此 MCP Server

打开 Claude 配置文件
如果你电脑上有安装 VS Code：
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
如果你电脑上没有安装 VS Code:
可以执行：
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
如果文件不存在，先创建文件:
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

将下列内容粘贴到 Claude 配置文件中：

```
{
    "mcpServers": {
    "coze-workflow": {
        "command": "uv",
        "args": [
            "--directory",
            "/Users/username/projects/coze-mcp",
            "run",
            "coze_workflow.py"
        ]
    }
    }
}
```

## 在 cursor 中安装此 MCP Server

在 cursor mcp 配置中，类型选择 command，command 中贴入以下内容：
`uv --directory /Users/username/projects/coze-mcp run coze_workflow.py`
