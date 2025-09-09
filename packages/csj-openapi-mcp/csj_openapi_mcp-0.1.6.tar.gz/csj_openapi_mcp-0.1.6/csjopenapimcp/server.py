from fastmcp.server import FastMCP
from pydantic import BaseModel, Field
import os
import requests

from csjopenapimcp.common import CSJMediaUtil

# ==== start 该部分编写在包中，媒体import即可 ========
mcp = FastMCP(name="CSJ platform", instructions="use open api query info or edit info.")


class DataAPI(BaseModel):
    date: str = Field(description="穿山甲广告数据对应的日期，格式为yyyy-mm-dd")


@mcp.tool(
    name="查询穿山甲数据报表",
    description="查询穿山甲广告数据，获取指定日期内的广告数据，包括以下返回参数，ad_slot_id:代码位ID,request:请求量，return:返回量，fill_rate:填充率，show:展示量，click:点击量，click_rate:点击率，revenue:预估收益，ecpm:预估ecpm。",
)
def query_csj_data(data: DataAPI):
    secret = os.environ.get("CSJ_MCP_AUTH_TOKEN")
    media_id = os.environ.get("MEDIA_ID")

    params = {
        "currency": "cny",
        "date": data.date,
        "region": "cn",
    }
    CSJMediaUtil.user_id = media_id  # 请替换为自己的穿山甲user_id
    CSJMediaUtil.role_id = media_id  # 请替换为自己的穿山甲role_id，可在穿山甲网站上查看到
    CSJMediaUtil.secure_key = secret
    url = CSJMediaUtil.get_media_rt_income(params)
    # 请求url返回地址
    response = requests.get(url)
    return response.text


# ===== end =======


def main():
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
