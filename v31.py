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
import os
import time

app = Flask(__name__)

UPLOAD_FOLDER = '/home/jeff/iFreeFlow/Files'

def log_request():
    with open('log.txt', 'a') as f:
        f.write(f'Requested URL: {request.url}\n')
        f.write(f'Request Method: {request.method}\n')
        f.write(f'Request Headers: {request.headers}\n')
        f.write(f'Request Body: {request.data}\n')
        f.write('\n')



@app.route('/api/translate', methods=['GET'])
def translate():
    text = request.args.get('text')
    # Default to English if not provided
    target_lang = request.args.get('target_lang', 'en')

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    if target_lang not in ['en', 'zh']:
        return jsonify({'error': 'Unsupported target language.'}), 400

    try:
        # Determine the translation direction based on the target language
        direction = ':en' if target_lang == 'en' else ':zh'
        result = subprocess.run(
            ['trans', '-b', direction, text], capture_output=True, text=True, check=True)
        translation = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Translation command failed.', 'details': str(e)}), 500
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
    dec_str = "".join(num_to_upper[digit] + unit for digit,
                      unit in zip(dec_part, units[1:]) if digit != '0')
    if not dec_str:
        dec_str = "整"
    return int_str + units[0] + dec_str

@app.route('/invoice-ocr', methods=['GET'])
def invoice_ocr():
    # 获取文件名
    file_name = request.args.get('filename')
    if not file_name:
        return jsonify({"error": "No filename provided"}), 400
    
    # 构建文件路径
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # 调用发票识别功能
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://127.0.0.1:10004/invoice-ocr', files=files)
            response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "Invoice OCR request failed", "details": str(e)}), 500

    # 返回发票识别的JSON响应
    return response.json()

@app.route('/convert', methods=['GET'])
def convert_to_pdf():
    # 获取文件名
    file_name = request.args.get('filename')
    if not file_name:
        return jsonify({"error": "No filename provided"}), 400
    
    # 构建文件路径
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # 确保是Word文件
    if not file_name.endswith(('.doc', '.docx')):
        return jsonify({"error": "Invalid file type"}), 400
    
    # 构建PDF文件名和路径
    pdf_file_name = file_name.rsplit('.', 1)[0] + '.pdf'
    pdf_file_path = os.path.join(UPLOAD_FOLDER, pdf_file_name)

    # 记录开始时间
    start_time = time.time()

    # 使用unoconv进行文件转换
    try:
        subprocess.run(['unoconv', '-f', 'pdf', file_path], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "File conversion failed", "details": str(e)}), 500

    # 记录结束时间
    end_time = time.time()

    # 计算转换时间
    conversion_time = end_time - start_time

    # 返回JSON响应
    return jsonify({
        "conversion_time": conversion_time,
        "pdf_file_path": pdf_file_path
    })

@app.route('/zip-folder', methods=['GET'])
def zip_folder():
    # 获取文件夹名称
    folder_name = request.args.get('foldername')
    if not folder_name:
        return jsonify({"error": "No folder name provided"}), 400
    
    # 构建文件夹路径
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    # 构建压缩文件路径
    zip_file_name = f"{folder_name}.zip"
    zip_file_path = os.path.join(UPLOAD_FOLDER, zip_file_name)

    # 使用zip命令进行压缩
    try:
        subprocess.run(['zip', '-r', zip_file_path, folder_path], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Folder compression failed", "details": str(e)}), 500

    # 返回JSON响应
    return jsonify({"zip_file_path": zip_file_path})

@app.route('/api/convert_amount', methods=['GET'])
def convert_amount():
    amount_str = request.args.get('amount')
    try:
        amount = float(amount_str)
    except ValueError:
        return jsonify({'error': '需要正确的格式如 12345.678'}), 400

    chinese_upper = number_to_chinese_upper(amount)

    return jsonify({'amount': amount_str, 'chinese_upper': chinese_upper})

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
