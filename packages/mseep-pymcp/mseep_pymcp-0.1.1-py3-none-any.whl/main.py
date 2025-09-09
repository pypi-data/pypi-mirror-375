from src.mcp_instance import mcp
import src.describe_tools
import src.mysql_tool
import src.web_tool


# 각 모듈에서 @mcp.tool()이 전역 등록됨
def main():
    mcp.run(transport="sse", host="0.0.0.0", port=7878, log_level="debug")