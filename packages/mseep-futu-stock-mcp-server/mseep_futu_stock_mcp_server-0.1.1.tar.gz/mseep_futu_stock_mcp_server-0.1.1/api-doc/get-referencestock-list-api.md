# 获取参考股票列表接口文档

## 接口功能
用于获取指定股票的参考股票列表，包括相关股票、行业龙头等。

## 接口模块
Quote API - 相关衍生品模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_list | list | 是 | 股票代码列表，格式为["市场.代码"]，例如["HK.00700"] |
| market | string | 否 | 市场代码，例如"HK"、"US"等，默认为空 |
| reference_type | string | 否 | 参考类型，可选值：INDUSTRY(行业)、CONCEPT(概念)、REGION(地区)，默认为空(获取所有类型) |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "reference_stock_list": [
            {
                "code": "HK.00700",
                "update_time": "2024-03-20 10:00:00",
                "reference_stocks": [
                    {
                        "reference_code": "HK.03690",
                        "reference_name": "美团-W",
                        "reference_type": "INDUSTRY",
                        "reference_desc": "互联网行业",
                        "correlation": 0.8,
                        "weight": 0.3
                    },
                    {
                        "reference_code": "HK.09988",
                        "reference_name": "阿里巴巴-SW",
                        "reference_type": "INDUSTRY",
                        "reference_desc": "互联网行业",
                        "correlation": 0.7,
                        "weight": 0.2
                    },
                    {
                        "reference_code": "HK.09888",
                        "reference_name": "百度集团-SW",
                        "reference_type": "CONCEPT",
                        "reference_desc": "人工智能",
                        "correlation": 0.6,
                        "weight": 0.1
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
| 1008 | INVALID_REFERENCETYPE | 参考类型错误 |
| 1024 | GET_REFERENCESTOCK_LIST_FAILED | 获取参考股票列表失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取参考股票列表
ret, data = quote_ctx.get_referencestock_list(
    ['HK.00700'],
    reference_type='INDUSTRY'
)
if ret == RET_OK:
    print('获取参考股票列表成功')
    for ref in data:
        print(f"股票代码: {ref['code']}")
        print(f"更新时间: {ref['update_time']}")
        print("参考股票信息:")
        for stock in ref['reference_stocks']:
            print(f"参考股票代码: {stock['reference_code']}")
            print(f"参考股票名称: {stock['reference_name']}")
            print(f"参考类型: {stock['reference_type']}")
            print(f"参考描述: {stock['reference_desc']}")
            print(f"相关性: {stock['correlation']}")
            print(f"权重: {stock['weight']}")
            print("-------------------")
else:
    print('获取参考股票列表失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取参考股票列表前需要先建立行情连接
2. 可以同时获取多个股票的参考股票列表
3. 参考股票列表更新频率较低，建议缓存使用
4. 参考股票列表主要用于分析股票相关性，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 