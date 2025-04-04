import requests
import config
from datetime import datetime, date
import time
import json

# 国家气象局站点ID映射（鞍山：54539）
STATION_IDS = {
    "鞍山": "54539",
    # 可扩展其他城市...
}

def get_access_token():
    """获取微信access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.app_id}&secret={config.app_secret}"
    response = requests.get(url).json()
    return response["access_token"]

def get_weather():
    """国家气象局API获取鞍山天气（含最高最低温）"""
    station_id = STATION_IDS.get(config.city)
    if not station_id:
        return weather_fallback()
    
    try:
        url = f"http://www.nmc.cn/rest/weather?stationid={station_id}"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        # 解析实时天气
        real = data["data"]["real"]
        weather = real["weather"]["info"]
        temp_now = real["weather"]["temperature"]
        
        # 解析预报数据（今天）
        today_forecast = data["data"]["predict"]["detail"][0]
        temp_max = today_forecast["max"]
        temp_min = today_forecast["min"]
        
        return {
            "weather": weather,
            "temp_now": temp_now,
            "temp_max": temp_max,
            "temp_min": temp_min
        }
        
    except Exception as e:
        print(f"气象局API错误: {str(e)[:200]}...")  # 截断长错误信息
        return weather_fallback()

def weather_fallback():
    """天气获取失败时的备用数据"""
    return {
        "weather": "未知",
        "temp_now": "N/A",
        "temp_max": "N/A",
        "temp_min": "N/A"
    }

def get_love_days():
    """计算认识天数"""
    try:
        start_date = datetime.strptime(config.love_date, "%Y-%m-%d").date()
        return str((date.today() - start_date).days)
    except Exception as e:
        print(f"计算天数失败: {e}")
        return "0"

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
    return "早安！今天是元气满满的一天~"

def send_daily_message():
    """发送每日推送"""
    access_token = get_access_token()
    weather_data = get_weather()
    
    # 构建消息数据
    data = {
        "touser": config.user[0],
        "template_id": config.template_id,
        "data": {
            "date": {"value": datetime.now().strftime("%Y-%m-%d"), "color": "#173177"},
            "city": {"value": config.city, "color": "#173177"},
            "weather": {"value": weather_data["weather"], "color": "#FF9900"},
            "min_temperature": {"value": f"{weather_data['temp_min']}℃", "color": "#0000FF"},
            "max_temperature": {"value": f"{weather_data['temp_max']}℃", "color": "#FF0000"},
            "love_day": {"value": get_love_days(), "color": "#FF00FF"},
            "message": {"value": get_morning_message(), "color": "#00AA00"}
        }
    }
    
    # 发送请求
    try:
        response = requests.post(
            "https://api.weixin.qq.com/cgi-bin/message/template/send",
            params={"access_token": access_token},
            json=data,
            timeout=10
        )
        print("推送结果：", response.json())
    except Exception as e:
        print(f"微信推送失败: {e}")

def test_weather_api():
    """测试气象局API"""
    print("\n=== 气象局API测试 ===")
    weather = get_weather()
    print("实时天气:", weather["weather"])
    print("当前温度:", weather["temp_now"])
    print("今日最高:", weather["temp_max"])
    print("今日最低:", weather["temp_min"])

if __name__ == "__main__":
    test_weather_api()
    
    print("\n等待推送时间...")
    while datetime.now().strftime("%H:%M:%S") < config.post_time:
        time.sleep(1)
    
    print("开始推送...")
    send_daily_message()
