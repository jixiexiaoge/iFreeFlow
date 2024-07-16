from flask import Flask, request, jsonify, send_file, redirect, render_template_string
import chinese_calendar as calendar
import datetime
import calendar as py_calendar
import qrcode
from io import BytesIO
import requests

app = Flask(__name__)

@app.route('/api/holiday', methods=['GET'])
def get_holiday_info():
    date_str = request.args.get('date')
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    # 查询日期信息
    is_holiday = calendar.is_holiday(date)
    is_workday = calendar.is_workday(date)
    on_holiday, holiday_name = calendar.get_holiday_detail(date)
    is_in_lieu = calendar.is_in_lieu(date)

    # 获取周数和星期
    week_number = date.isocalendar()[1]
    weekday_name = py_calendar.day_name[date.weekday()]

    response = {
        'date': date_str,
        'week_number': week_number,
        'weekday': weekday_name,
        'is_holiday': is_holiday,
        'is_workday': is_workday,
        'holiday_name': holiday_name if holiday_name else 'None',
        'is_in_lieu': is_in_lieu
    }

    return jsonify(response)

@app.route('/api/sum_and_average', methods=['GET'])
def sum_and_average():
    numbers_str = request.args.get('numbers')
    try:
        numbers = [float(num) for num in numbers_str.split(',')]
    except ValueError:
        return jsonify({'error': 'Invalid numbers format. Please use comma-separated numbers.'}), 400
    
    total = sum(numbers)
    average = total / len(numbers) if numbers else 0

    response = {
        'numbers': numbers,
        'sum': total,
        'average': average
    }

    return jsonify(response)

@app.route('/api/qrcode', methods=['GET'])
def generate_qrcode():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # 创建文件名
    filename = f"{text}.png"

    # 保存二维码图像到内存中的BytesIO对象
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # 发送文件响应，触发浏览器下载
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=filename)

@app.route('/api/wechat_notify', methods=['GET'])
def wechat_notify():
    wechat_id = request.args.get('wechat_id')
    title = request.args.get('title')
    content = request.args.get('content')
    
    if not wechat_id or not title or not content:
        return jsonify({'error': 'Missing parameters. Please provide wechat_id, title, and content.'}), 400

    url = f"https://push.showdoc.com.cn/server/api/push/{wechat_id}"
    data = {
        'title': title,
        'content': content
    }

    try:
        response = requests.post(url, json=data)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(response_json)

@app.errorhandler(404)
def page_not_found(e):
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="3;url=https://github.com/jixiexiaoge/iFreeFlow/blob/main/README.md">
        <title>Page Not Found</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
            }
            #countdown {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>你输入的参数有误，请参考项目的介绍正确填写GET请求的参数！</h1>
        <p>将在 <span id="countdown">3</span> 秒后自动跳转到项目地址...</p>
        <script>
            let countdownNumber = 3;
            const countdownElement = document.getElementById('countdown');
            setInterval(() => {
                countdownNumber--;
                countdownElement.textContent = countdownNumber;
                if (countdownNumber <= 0) {
                    clearInterval();
                }
            }, 1000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
