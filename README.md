## 北京安博通科技股份有限公司 http://www.abtnetworks.com/
## 概述

为智能终端提供即时通讯服务的免费应用程序

## 配置动作

### 1.本文消息推送

微信公众号推送本文消息

#### 参数

| 参数    | 参数别名 | **描述**                   | **Required** | **示例** |
| ------- | -------- | -------------------------- | ------------ | -------- |
| msgtype | 消息类型 | 消息类型，此时固定为：text | 是           | text     |
| content | 消息内容 | 发送消息的内容             | 是           | HELLO    |

#### 返回

```
send success
```


#### 返回json字段说明

```json
{
    "data":"信息发送状态",
    "schema":{
        "type":"STRING"
    },
    "status":"Success"
}
```

#### 返回示例

```json
{
    "data": "send success",
	"schema": {
		"type": "STRING"
	},
    "status": "Success"
}
```
