import requests
import config
from datetime import datetime, date
import time

def get_access_token():
    """获取微信access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.app_id}&secret={config.app_secret}"
    response = requests.get(url).json()
    return response["access_token"]

def get_weather(province, city):
    """使用和风天气API（稳定版）"""
    city_id = "101070301"  # 鞍山市固定ID
    key = "850912c546084a33b1e7fde37316d6b1"  # 申请地址：https://dev.qweather.com/
    
    url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={key}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        weather = data["now"]["text"]              # 天气状况（如"晴"）
        temp = data["now"]["temp"] + "℃"          # 当前温度
        temp_min = data["now"]["feelsLike"] + "℃"  # 体感温度（或改用预报API获取真实最低温）
        
        # 获取24小时预报中的真实最高最低温
        forecast_url = f"https://devapi.qweather.com/v7/weather/24h?location={city_id}&key={key}"
        forecast = requests.get(forecast_url).json()
        temp_max = forecast["hourly"][0]["temp"] + "℃"
        temp_min = forecast["hourly"][0]["feelsLike"] + "℃"
        
        return weather, temp_max, temp_min
    except Exception as e:
        print(f"天气获取失败: {e}")
        return "未知", "N/A", "N/A"
        
def get_love_days():
    """修正天数计算逻辑"""
    try:
        start_date = datetime.strptime(config.love_date, "%Y-%m-%d").date()
        days = (date.today() - start_date).days
        return f"第{days}天"  # 格式化为"第X天"
    except Exception as e:
        print(f"计算天数失败: {e}")
        return "未知"

def get_morning_message():
    """获取天行数据早安文案"""
    url = "http://api.tianapi.com/zaoan/index"
    params = {"key": config.tianxing_api_key}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.json().get("code") == 200:
            return response.json()["newslist"][0]["content"]
    except Exception as e:
        print(f"获取早安文案失败: {e}")
    return "希望你今天也要好好吃饭 乖乖睡觉 坏心情都与你无关！"  # 默认文案

def send_daily_message():
    """发送每日推送"""
    access_token = get_access_token()
    weather, max_temp, min_temp = get_weather(config.province, config.city)
    
    data = {
        "touser": config.user[0],
        "template_id": config.template_id,
        "data": {
            "date": {"value": datetime.now().strftime("%Y-%m-%d"), "color": "#173177"},
            "city": {"value": config.city, "color": "#173177"},
            "weather": {"value": weather, "color": "#FF9900"},
            "max_temperature": {"value": max_temp + "℃", "color": "#FF0000"},
            "min_temperature": {"value": min_temp + "℃", "color": "#0000FF"},
            "love_days": {"value": f"第{get_love_days()}天", "color": "#FF00FF"},
            "message": {"value": get_morning_message(), "color": "#00AA00"}
        }
    }
    
    response = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}",
        json=data
    )
    print("推送结果：", response.json())

if __name__ == "__main__":
    # 等待到达推送时间
    while datetime.now().strftime("%H:%M:%S") < config.post_time:
        time.sleep(1)
    
    send_daily_message()
