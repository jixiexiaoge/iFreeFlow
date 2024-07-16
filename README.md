###项目介绍：iFreeFlow

##由于 Power Automate 本身的功能限制，某些功能需要调用 HTTP 的 API 接口或第三方连接器才能实现。然而，许多企业禁用了第三方连接器，并且普通用户仅拥有标准许可证，只能使用默认连接器。考虑到中国的特殊情况，我们特意推出了 iFreeFlow 项目，旨在为广大的 Power Automate 用户提供便捷且实用的 API 服务。
iFreeFlow 项目已经开源，大家可以直接调用 OneDrive 的“URL 上传文件”功能来使用这些 API。同时，我们欢迎大家下载本项目的解决方案，并鼓励大家在自己的服务器上进行私有化部署。请勿对该项目进行商业付费，以免上当受骗。如果你觉得这个开源项目对你有很大帮助，请考虑通过 buy me a coffee 来赞助服务器的运维费用。谢谢！



##功能亮点：免费，开源，支持私有化部署，云端Flow桌面PAD均可调用~
#节假日查询：
通过日期查询是否是节假日，是否调休，返回包含周数、星期、农历等信息的 JSON。
#数据计算：
接收一组逗号分隔的数字，计算它们的求和和平均数，并以 JSON 格式返回结果。
#二维码生成：
生成字符串对应的二维码，自动触发浏览器下载，并保存为 {字符串}.png 格式。
#微信通知推送：
接收微信 ID、标题和内容，通过 POST 请求发送微信通知，并将响应的 JSON 直接反馈给用户。

##接口文档
接口地址：http://mspa.koreacentral.cloudapp.azure.com:8080/
或者  http://20.41.84.42:8080/ 【ip地址可能不稳定】
或者 https://api.mspa.app/ 【若连接失败请使用第一个】
 
##使用说明：如下截图是最简单的一种使用演示，实际根据api的不同有所差异！

#节假日查询：
访问 URL 示例: http://mspa.koreacentral.cloudapp.azure.com:8080/api/holiday?date=2023-10-01 
返回日期信息，包含是否节假日、是否调休、周数和星期等。

#数据计算：
访问 URL 示例:http://mspa.koreacentral.cloudapp.azure.com:8080/api/sum_and_average?numbers=1,2,3,4,5 
 返回求和和平均数的计算结果。

#二维码生成：
访问 URL 示例: http://mspa.koreacentral.cloudapp.azure.com:8080/api/qrcode?text=HelloWorld 
浏览器自动下载名为 HelloWorld.png 的二维码图像文件。

#微信通知推送：
访问 URL 示例: http://mspa.koreacentral.cloudapp.azure.com:8080/api/wechat_notify?wechat_id=3be5931476f86adebd1e57f68b6ee7bb1133567420&title=免费推送微信信息&content=机械小鸽专业Power Automate玩家
URL 发送 POST 请求，并返回响应 JSON。
![最简单演示](guide.png)

还有很多功能还在完善中，欢迎大家反馈更过功能需求！


参与方式：
我们诚邀各位用户下载并使用 iFreeFlow 项目，并鼓励大家在自己的服务器上进行私有化部署。请勿对该项目进行商业付费，以免上当受骗。如果你觉得这个开源项目对你有很大帮助，请考虑通过 buy me a coffee 来赞助服务器的运维费用。谢谢！
通过 iFreeFlow，我们希望能为广大 Power Automate 用户提供更便捷的服务，提升使用体验，欢迎大家的参与和支持！

![最简单演示](buymeacoofe.png)
