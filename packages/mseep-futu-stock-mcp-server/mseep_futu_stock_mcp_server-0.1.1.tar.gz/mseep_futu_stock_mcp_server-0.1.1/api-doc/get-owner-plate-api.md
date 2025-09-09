# 获取所属板块接口文档

## 接口功能
用于获取指定股票所属的板块信息，包括行业板块、概念板块等。

## 接口模块
Quote API - 基础数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "owner_plate_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "industry_plates": [
                    {
                        "plate_code": "HK.INDUSTRY.IT",
                        "plate_name": "信息技术",
                        "plate_type": "INDUSTRY"
                    }
                ],
                "concept_plates": [
                    {
                        "plate_code": "HK.CONCEPT.GAME",
                        "plate_name": "游戏",
                        "plate_type": "CONCEPT"
                    },
                    {
                        "plate_code": "HK.CONCEPT.SOCIAL",
                        "plate_name": "社交",
                        "plate_type": "CONCEPT"
                    }
                ],
                "region_plates": [
                    {
                        "plate_code": "HK.REGION.HK",
                        "plate_name": "香港",
                        "plate_type": "REGION"
                    }
                ]
            }
        ]
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_CODE | 股票代码格式错误 |
| 1018 | GET_OWNER_PLATE_FAILED | 获取所属板块数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取所属板块数据
ret, data = quote_ctx.get_owner_plate(['HK.00700'])
if ret == RET_OK:
    print('获取所属板块数据成功')
    for plate in data:
        print(f"股票代码: {plate['code']}")
        print(f"更新时间: {plate['update_time']}")
        print("行业板块:")
        for industry in plate['industry_plates']:
            print(f"板块代码: {industry['plate_code']}")
            print(f"板块名称: {industry['plate_name']}")
            print(f"板块类型: {industry['plate_type']}")
            print("-------------------")
        print("概念板块:")
        for concept in plate['concept_plates']:
            print(f"板块代码: {concept['plate_code']}")
            print(f"板块名称: {concept['plate_name']}")
            print(f"板块类型: {concept['plate_type']}")
            print("-------------------")
        print("地区板块:")
        for region in plate['region_plates']:
            print(f"板块代码: {region['plate_code']}")
            print(f"板块名称: {region['plate_name']}")
            print(f"板块类型: {region['plate_type']}")
            print("-------------------")
else:
    print('获取所属板块数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取所属板块数据前需要先建立行情连接
2. 可以同时获取多个股票的所属板块数据
3. 所属板块数据更新频率较低，建议缓存使用
4. 所属板块数据主要用于分析股票所属的行业、概念等信息，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 