# 获取市场状态接口文档

## 接口功能
用于获取指定市场的交易状态信息，包括开市、休市、午休等状态。

## 接口模块
Quote API - 基础数据模块

## 接口参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码，例如"HK"、"US"等 |

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "market_state": {
            "market": "HK",
            "market_state": 1,
            "market_state_desc": "开市",
            "update_time": "2024-03-20 10:00:00"
        }
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1001 | INVALID_PARAM | 参数错误 |
| 1002 | INVALID_MARKET | 市场代码错误 |
| 1014 | GET_MARKET_STATE_FAILED | 获取市场状态失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取市场状态
ret, data = quote_ctx.get_market_state("HK")
if ret == RET_OK:
    print('获取市场状态成功')
    print(f"市场: {data['market']}")
    print(f"状态: {data['market_state']}")
    print(f"状态描述: {data['market_state_desc']}")
    print(f"更新时间: {data['update_time']}")
else:
    print('获取市场状态失败:', data)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 获取市场状态前需要先建立行情连接
2. 市场状态会实时更新，建议定期获取最新状态
3. 不同市场的交易时间不同，需要注意时区差异
4. 市场状态会影响交易操作，建议在交易前先检查市场状态
5. 需要注意处理异常情况，避免程序崩溃 