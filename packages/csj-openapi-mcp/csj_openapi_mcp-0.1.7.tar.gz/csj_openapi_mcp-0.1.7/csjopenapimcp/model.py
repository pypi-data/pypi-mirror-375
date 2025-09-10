# coding=utf-8
from pydantic import BaseModel, Field


#  创建应用
class SiteCreateParams(BaseModel):
    Status: str = Field(description="请求创建应用的状态，请求枚举仅接受2，6。 2：运行中 6：测试中")
    AppCategoryCode: str = Field(
        description="应用所属二级行业码，参考：https://bytedance.larkoffice.com/sheets/shtcncP14js8FCE9NK2MQo3dXPc?sheet=bpeEue&range=Mzoz")
    AppName: str = Field(description="创建应用的名称")
    PackageName: str = Field(description="创建应用对应的包名信息。 eg: package.com.test")
    DownloadURL: str = Field(description="创建应用对应的下载地址，或者对应的应用商店详情页地址")
    ApkSign: str = Field(description="创建应用对应的签名信息")


#  查询报表
class DataAPI(BaseModel):
    date: str = Field(description="穿山甲广告数据对应的日期，格式为yyyy-mm-dd")
