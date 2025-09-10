# coding=utf-8
from fastmcp.server import FastMCP
from model import DataAPI, SiteCreateParams
import time

import os
import requests

from csjopenapimcp.sign import CSJMediaUtil, get_aurora_sign

mcp = FastMCP(name="CSJ platform", instructions="use open api query info or edit info.")


# 穿山甲报表数据API
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


@mcp.tool(
    name="创建穿山甲应用",
    description="创建穿山甲应用，返回应用ID，用于广告投放。返回码code=0代表成功，其余失败",
)
def create_site(param: SiteCreateParams):
    secret = os.environ.get("CSJ_MCP_AUTH_TOKEN")
    media_id = os.environ.get("MEDIA_ID")
    time_stamp = int(time.time())
    nonce = 123
    sign = get_aurora_sign(secret, time_stamp, nonce)

    params = {
        "user_id": media_id,
        "role_id": media_id,
        "time_stamp": time_stamp,
        "nonce": nonce,
        "version": "1.0",
        "status": param.Status,
        "app_category_code": param.AppCategoryCode,
        "app_name": param.AppName,
        "package_name": param.PackageName,
        "download_url": param.DownloadURL,
        "apk_sign": param.ApkSign,
        "sign": sign
    }

    response = requests.post(
        url="https://open-api.csjplatform.com/union/media/open_api/site/create",
        json=params,
    )

    return response.text


def main():
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
