from flask import Flask, request, jsonify, send_file, render_template_string
import chinese_calendar as calendar
import datetime
import calendar as py_calendar
import qrcode
from io import BytesIO
import requests
import logging
from logging.handlers import RotatingFileHandler
import subprocess

app = Flask(__name__)

# 设置日志记录
handler = RotatingFileHandler('log.txt', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.before_request
def log_request_info():
    app.logger.info(f"Requested URL: {request.url}, Method: {request.method}, IP: {request.remote_addr}, Params: {request.args}")

@app.route('/api/holiday', methods=['GET'])
def get_holiday_info():
    date_str = request.args.get('date')
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    is_holiday = calendar.is_holiday(date)
    is_workday = calendar.is_workday(date)
    on_holiday, holiday_name = calendar.get_holiday_detail(date)
    is_in_lieu = calendar.is_in_lieu(date)

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

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    filename = f"{text}.png"

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

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

@app.route('/api/translate', methods=['GET'])
def translate():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'No text provided.'}), 400
    
    try:
        result = subprocess.run(['trans', '-b', ':en', text], capture_output=True, text=True)
        translation = result.stdout.strip()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'original': text, 'translation': translation})

def number_to_chinese_upper(num):
    units = ["元", "角", "分"]
    big_units = ["", "万", "亿"]
    num_to_upper = {
        '0': '零', '1': '壹', '2': '贰', '3': '叁', '4': '肆',
        '5': '伍', '6': '陆', '7': '柒', '8': '捌', '9': '玖'
    }

    def four_digit_to_upper(four_digit):
        result = ""
        units = ["", "拾", "佰", "仟"]
        for i, digit in enumerate(reversed(four_digit)):
            if digit != '0':
                result = num_to_upper[digit] + units[i] + result
            elif result and not result.startswith("零"):
                result = "零" + result
        return result.rstrip('零') or '零'

    def split_number(num):
        int_part, _, dec_part = str(num).partition('.')
        int_part = int_part[::-1]
        groups = [int_part[i:i+4][::-1] for i in range(0, len(int_part), 4)]
        dec_part = dec_part.ljust(2, '0')[:2]
        return groups, dec_part

    int_part, dec_part = split_number(num)
    int_str = "".join(four_digit_to_upper(group) + big_units[i]
                      for i, group in enumerate(int_part))
    if int_str.endswith('零'):
        int_str = int_str[:-1]
    dec_str = "".join(num_to_upper[digit] + unit for digit, unit in zip(dec_part, units[1:]) if digit != '0')
    if not dec_str:
        dec_str = "整"
    return int_str + units[0] + dec_str

@app.route('/api/convert_amount', methods=['GET'])
def convert_amount():
    amount_str = request.args.get('amount')
    try:
        amount = float(amount_str)
    except ValueError:
        return jsonify({'error': 'Invalid amount format. Please provide a valid number.'}), 400
    
    chinese_upper = number_to_chinese_upper(amount)
    
    return jsonify({'amount': amount_str, 'chinese_upper': chinese_upper})

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
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
