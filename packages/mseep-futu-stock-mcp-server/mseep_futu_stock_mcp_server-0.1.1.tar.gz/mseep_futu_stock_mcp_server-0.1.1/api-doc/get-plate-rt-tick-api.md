# 获取板块分时数据接口文档

## 接口功能
用于获取指定板块的实时分时数据，包括最新价、涨跌幅、成交量等。

## 接口模块
Quote API - 分时数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，格式为"market.type.code"，例如"HK.INDUSTRY.IT" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.INDUSTRY.IT",
        "plate_name": "信息技术",
        "market": "HK",
        "tick": {
            "time": "2024-03-20 16:00:00",
            "price": 105.0,
            "change_rate": 5.0,
            "volume": 1000000,
            "turnover": 100000000,
            "update_time": "2024-03-20 16:00:00"
        }
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1003 | INVALID_PLATECODE | 板块代码错误 |
| 1032 | GET_PLATE_RT_TICK_FAILED | 获取板块分时数据失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块分时数据
ret, data = quote_ctx.get_plate_rt_tick(
    plate_code="HK.INDUSTRY.IT",
    market="HK"
)
if ret == RET_OK:
    print('获取板块分时数据成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print("分时数据:")
    print(f"时间: {data['tick']['time']}")
    print(f"最新价: {data['tick']['price']}")
    print(f"涨跌幅: {data['tick']['change_rate']}%")
    print(f"成交量: {data['tick']['volume']}")
    print(f"成交额: {data['tick']['turnover']}")
    print(f"更新时间: {data['tick']['update_time']}")
else:
    print('获取板块分时数据失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块分时数据前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 分时数据会随着市场变化而实时更新
4. 分时数据主要用于实时监控市场动态
5. 需要注意处理异常情况，避免程序崩溃 