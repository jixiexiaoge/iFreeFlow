from flask import Flask, request, jsonify
import chinese_calendar as calendar
import datetime
import calendar as py_calendar
import lunarcalendar

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
