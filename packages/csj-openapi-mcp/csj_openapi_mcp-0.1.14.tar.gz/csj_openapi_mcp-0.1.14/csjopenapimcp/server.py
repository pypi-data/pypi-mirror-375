# coding=utf-8
from fastmcp.server import FastMCP
from csjopenapimcp.model import (DataAPI, SiteCreateParams, SiteQueryParams,
                                 CodeQueryParams, CodeCreateParams, category)
from csjopenapimcp.sign import CSJMediaUtil, get_aurora_sign
import time
import os
import requests

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
    timestamp = int(time.time())
    nonce = 123
    sign = get_aurora_sign(secret, timestamp, nonce)

    params = {
        "user_id": media_id,
        "role_id": media_id,
        "timestamp": timestamp,
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


@mcp.tool(
    name="应用行业码查询，二级行业码映射关系",
    description="应用二级行业码映射关系，key为二级行业码，value为行业名称。记录了应用所属行业名称和行业ID的关系，其中行业ID为整数"
)
def query_category():
    return category


@mcp.tool(
    name="查询穿山甲应用",
    description="应用查询接口，返回应用信息，以及应用的配置参数等"
)
def query_site(param: SiteQueryParams):
    secret = os.environ.get("CSJ_MCP_AUTH_TOKEN")
    media_id = os.environ.get("MEDIA_ID")
    timestamp = int(time.time())
    nonce = 123
    sign = get_aurora_sign(secret, timestamp, nonce)

    params = {
        "user_id": media_id,
        "role_id": media_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "version": "1.0",
        "sign": sign,

        "page": 1,
        "page_size": 10
    }
    if param.AppID != 0:
        params["app_id"] = [param.AppID]
    if param.Status != 0:
        params["status"] = [param.Status]

    response = requests.post(
        url="https://open-api.csjplatform.com/union/media/open_api/site/query",
        json=params,
    )

    return response.text


@mcp.tool(
    name="代码位查询",
    description="代码位查询接口，返回代码位信息，以及代码位的配置参数等"
)
def code_query(param: CodeQueryParams):
    secret = os.environ.get("CSJ_MCP_AUTH_TOKEN")
    media_id = os.environ.get("MEDIA_ID")
    timestamp = int(time.time())
    nonce = 123
    sign = get_aurora_sign(secret, timestamp, nonce)

    params = {
        "user_id": media_id,
        "role_id": media_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "version": "1.0",
        "sign": sign,

        "page": 1,
        "page_size": 10
    }

    if param.CodeID != 0:
        params["code_id"] = [param.CodeID]
    if param.Status != 0:
        params["status"] = [param.Status]
    if param.AppID != 0:
        params["app_id"] = [param.AppID]
    if param.Page != 0:
        params["page"] = param.Page
    if param.PageSize != 0:
        params["page_size"] = param.PageSize

    response = requests.post(
        url="https://open-api.csjplatform.com/union/media/open_api/code/query",
        json=params,
    )

    return response.text


@mcp.tool(
    name="创建穿山甲代码位",
    description="创建穿山甲代码位，返回代码位ID，用于广告投放。返回码code=0代表成功，其余失败"
)
def code_create(param: CodeCreateParams):
    secret = os.environ.get("CSJ_MCP_AUTH_TOKEN")
    media_id = os.environ.get("MEDIA_ID")
    timestamp = int(time.time())
    nonce = 123
    sign = get_aurora_sign(secret, timestamp, nonce)

    params = {
        "user_id": media_id,
        "role_id": media_id,
        "timestamp": timestamp,
        "nonce": nonce,
        "version": "1.0",
        "sign": sign,
        "app_id": [param.AppID],
        "ad_slot_type": param.AdSlotType,
        "use_mediation": param.UseMedication,
        "mask_rule_ids": [],

        "page": 1,
        "page_size": 10
    }

    response = requests.post(
        url="https://open-api.csjplatform.com/union/media/open_api/code/create",
        json=params,
    )

    return response.text


def main():
    mcp.run(transport="stdio")


if __name__ == '__main__':
    main()
