# iFreeFlow
开源项目解决Power Automate中国用户使用一些api服务需要高阶许可证或者需要付费，这个项目是实现用默认连接器实现一些需求。

需要安装 pip install chinesecalendar 

启动服务即可 

例如访问 http://20.41.84.42:8080/api/holiday?date=2024-02-06

得到返回

{
    "date": "2024-02-06",
    "holiday_name": "None",
    "is_holiday": false,
    "is_in_lieu": false,
    "is_workday": true,
    "week_number": 6,
    "weekday": "Tuesday"
}

后续还有更多功能添加
