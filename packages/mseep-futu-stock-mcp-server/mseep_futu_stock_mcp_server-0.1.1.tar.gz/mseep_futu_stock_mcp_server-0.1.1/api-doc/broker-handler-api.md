# 经纪队列推送接口文档

## 接口功能
用于接收订阅的股票实时经纪队列数据推送，包括经纪商买卖盘信息。

## 接口模块
Quote API - 实时数据推送模块

## 接口参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_code | string | 股票代码，格式为"市场.代码"，例如"HK.00700" |
| bid_broker_id | list | 买盘经纪商ID列表 |
| bid_broker_name | list | 买盘经纪商名称列表，与ID一一对应 |
| bid_broker_pos | list | 买盘经纪商位置列表，与ID一一对应 |
| ask_broker_id | list | 卖盘经纪商ID列表 |
| ask_broker_name | list | 卖盘经纪商名称列表，与ID一一对应 |
| ask_broker_pos | list | 卖盘经纪商位置列表，与ID一一对应 |
| timestamp | string | 时间戳 |
| broker_status | int | 经纪队列状态 |

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

class BrokerHandler(BrokerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(BrokerHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("BrokerHandler: error, msg: %s" % data)
            return RET_ERROR, data
        
        print("BrokerHandler: ", data)
        return RET_OK, data

# 创建行情连接
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置回调
handler = BrokerHandler()
quote_ctx.set_handler(handler)

# 订阅经纪队列数据
quote_ctx.subscribe(['HK.00700'], [SubType.BROKER])

# 保持连接
while True:
    time.sleep(1)

# 关闭连接
quote_ctx.close()
```

## 注意事项
1. 此接口为回调接口，需要继承BrokerHandlerBase类并实现on_recv_rsp方法
2. 在订阅经纪队列数据前需要先设置回调处理器
3. 经纪队列数据更新频率较高，建议在回调中及时处理数据
4. 需要注意处理异常情况，避免程序崩溃
5. 经纪队列数据主要用于展示经纪商买卖盘信息，建议根据实际需求选择订阅的股票 