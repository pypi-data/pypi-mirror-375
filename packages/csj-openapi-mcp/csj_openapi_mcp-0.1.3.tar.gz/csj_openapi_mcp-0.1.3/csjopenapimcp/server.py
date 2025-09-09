from fastmcp.server import FastMCP
import tools

# ==== start 该部分编写在包中，媒体import即可 ========
mcp = FastMCP(name="CSJ platform", instructions="use open api query info or edit info.")


@mcp.tool(
    name="获取天气",  # Custom tool name for the LLM
    description="获取当天当地的天气 location: 地区",  # Custom description
)
def get_weather(location: str):
    return location + " 阴天有雨"




# ===== end =======


# import 包之后，获取create_server().媒体在本地或者自身服务器上进行部署
def main():
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
