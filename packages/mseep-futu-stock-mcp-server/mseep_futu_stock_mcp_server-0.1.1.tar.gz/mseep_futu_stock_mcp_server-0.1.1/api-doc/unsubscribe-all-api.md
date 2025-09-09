# 取消所有订阅接口文档

## 接口功能
用于取消当前连接下所有已订阅的股票、期货、期权等金融产品的实时行情数据。

## 接口模块
Quote API - 实时数据订阅模块

## 接口参数
无参数

## 接口返回结果
```json
{
    "ret_code": 0,
    "ret_msg": "SUCCESS",
    "data": {
        "is_unsubscribed_all": true
    }
}
```

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 1005 | UNSUBSCRIBE_FAILED | 取消订阅失败 |

## 示例代码
```python
from futu import *

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 取消所有订阅
ret = quote_ctx.unsubscribe_all()
if ret == RET_OK:
    print('取消所有订阅成功')
else:
    print('取消所有订阅失败:', ret)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 取消所有订阅前需要先建立行情连接
2. 此操作会取消当前连接下所有股票的订阅
3. 建议在程序退出前调用此接口，以确保清理所有订阅
4. 此操作不可逆，请谨慎使用 