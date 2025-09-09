# 获取板块实时K线接口文档

## 接口功能
用于获取指定板块的实时K线数据，包括开盘价、收盘价、最高价、最低价、成交量等。

## 接口模块
Quote API - K线数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plate_code | string | 是 | 板块代码，格式为"market.type.code"，例如"HK.INDUSTRY.IT" |
| market | string | 否 | 市场代码，例如"HK"、"US"等 |
| kline_type | string | 否 | K线类型，可选值：K_DAY(日K)、K_WEEK(周K)、K_MONTH(月K)、K_QUARTER(季K)、K_YEAR(年K)，默认为K_DAY |
| autype | string | 否 | 复权类型，可选值：NONE(不复权)、FORWARD(前复权)、BACKWARD(后复权)，默认为NONE |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "plate_code": "HK.INDUSTRY.IT",
        "plate_name": "信息技术",
        "market": "HK",
        "kline": {
            "time": "2024-03-20 00:00:00",
            "open": 100.0,
            "close": 105.0,
            "high": 108.0,
            "low": 98.0,
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
| 1006 | INVALID_KLINETYPE | K线类型错误 |
| 1007 | INVALID_AUTYPE | 复权类型错误 |
| 1031 | GET_PLATE_RT_KLINE_FAILED | 获取板块实时K线失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取板块实时K线
ret, data = quote_ctx.get_plate_rt_kline(
    plate_code="HK.INDUSTRY.IT",
    market="HK",
    kline_type="K_DAY",
    autype="NONE"
)
if ret == RET_OK:
    print('获取板块实时K线成功')
    print(f"板块代码: {data['plate_code']}")
    print(f"板块名称: {data['plate_name']}")
    print(f"市场: {data['market']}")
    print("K线数据:")
    print(f"时间: {data['kline']['time']}")
    print(f"开盘价: {data['kline']['open']}")
    print(f"收盘价: {data['kline']['close']}")
    print(f"最高价: {data['kline']['high']}")
    print(f"最低价: {data['kline']['low']}")
    print(f"成交量: {data['kline']['volume']}")
    print(f"成交额: {data['kline']['turnover']}")
    print(f"更新时间: {data['kline']['update_time']}")
else:
    print('获取板块实时K线失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取板块实时K线前需要先建立行情连接
2. 板块代码需要按照指定格式填写
3. 实时K线数据会随着市场变化而更新
4. K线数据主要用于技术分析，建议结合其他指标一起使用
5. 需要注意处理异常情况，避免程序崩溃 