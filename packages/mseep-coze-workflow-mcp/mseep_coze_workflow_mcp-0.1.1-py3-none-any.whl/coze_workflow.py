import json
import argparse
from typing import Dict, Any
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("coze-workflow")

# Coze API 配置
COZE_API_BASE = "https://api.coze.cn/v1"


# 设置命令行参数解析
def parse_args():
    parser = argparse.ArgumentParser(description="Coze 工作流 MCP 服务器")
    parser.add_argument("--docstring", type=str, help="为工作流工具设置文档字符串")
    return parser.parse_args()


# 获取文档字符串
def get_docstring():
    """从命令行参数获取文档字符串"""
    args = parse_args()
    if args.docstring:
        return args.docstring

    # 默认文档字符串
    return """运行指定的 Coze 工作流
    
该工具允许你调用 Coze 平台上的工作流并获取执行结果。
你可以通过提供工作流 ID、API 令牌和可选的参数来执行特定工作流。

Args:
    workflow_id: Coze 工作流的唯一标识符，可在 Coze 平台工作流详情页面找到
    token: Coze API 授权令牌，可在 Coze 平台的个人设置或开发者页面获取
    parameters_json: 工作流参数的 JSON 字符串，例如: {"name": "测试", "query": "内容"}
                    默认为空对象 "{}"

Returns:
    str: 格式化的 JSON 字符串，包含工作流执行结果或错误信息
"""


async def call_coze_workflow(
    workflow_id: str, token: str, parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """调用 Coze 工作流 API 并返回结果"""
    url = f"{COZE_API_BASE}/workflow/run"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"workflow_id": workflow_id, "parameters": parameters}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url, headers=headers, json=payload, timeout=60.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP 错误: {e.response.status_code}",
                "details": e.response.text,
            }
        except Exception as e:
            return {"error": f"请求错误: {str(e)}"}


@mcp.tool()
async def run_coze_workflow(
    workflow_id: str, token: str, parameters_json: str = "{}"
) -> str:
    # 动态设置文档字符串
    run_coze_workflow.__doc__ = get_docstring()

    try:
        # 解析参数 JSON
        parameters = json.loads(parameters_json)
    except json.JSONDecodeError:
        return "参数解析失败：提供的 JSON 格式无效"

    # 调用 Coze 工作流
    result = await call_coze_workflow(workflow_id, token, parameters)

    # 返回格式化的结果
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport="stdio")
