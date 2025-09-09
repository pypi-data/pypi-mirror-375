# 买卖盘推送接口文档

## 接口功能
用于接收订阅的股票实时买卖盘数据推送，包括买卖盘档位、价格、数量等信息。

## 接口模块
Quote API - 实时数据推送模块

## 接口参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_code | string | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| bid_price | list | 买盘价格列表，从高到低排序 |
| bid_volume | list | 买盘数量列表，与买盘价格一一对应 |
| ask_price | list | 卖盘价格列表，从低到高排序 |
| ask_volume | list | 卖盘数量列表，与卖盘价格一一对应 |
| update_time | string | 更新时间 |

## 接口返回结果
无返回结果，此接口为回调接口，用于接收推送数据。

## 接口异常情况
| 错误码 | 错误信息 | 说明 |
|--------|----------|------|
| 2001 | PUSH_DATA_ERROR | 推送数据错误 |
| 2002 | PUSH_DATA_TIMEOUT | 推送数据超时 |

## 示例代码
```python
from futu import *

class OrderBookHandler(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("OrderBookHandler: error, msg: %s" % data)
            return RET_ERROR, data
        
        print("OrderBookHandler: ", data)
        return RET_OK, data

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置回调
handler = OrderBookHandler()
quote_ctx.set_handler(handler)

# 订阅买卖盘数据
quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK])

# 保持连接
while True:
    time.sleep(1)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 此接口为回调接口，需要继承OrderBookHandlerBase类并实现on_recv_rsp方法
2. 在订阅买卖盘数据前需要先设置回调处理器
3. 买卖盘数据会实时更新，建议在回调中及时处理数据
4. 买卖盘数据通常包含多个档位，需要注意数据的完整性
5. 需要注意处理异常情况，避免程序崩溃 