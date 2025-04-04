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
    """使用和风天气API获取天气数据"""
    city_id = "101070301"  # 鞍山市固定ID
    key = "e2ad3377fbc34ffc99ca56707d668011"
    
    # 获取实时天气
    now_url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={key}"
    # 获取3天预报
    forecast_url = f"https://devapi.qweather.com/v7/weather/3d?location={city_id}&key={key}"
    
    try:
        # 获取实时天气
        now_data = requests.get(now_url, timeout=5).json()
        weather = now_data["now"]["text"]
        temp_now = now_data["now"]["temp"]
        
        # 获取预报数据
        forecast_data = requests.get(forecast_url, timeout=5).json()
        today_forecast = forecast_data["daily"][0]
        
        temp_max = today_forecast["tempMax"] + "℃"
        temp_min = today_forecast["tempMin"] + "℃"
        
        return weather, temp_max, temp_min
    except Exception as e:
        print(f"天气获取失败: {e}")
        return "未知", "N/A", "N/A"

def get_love_days():
    """计算认识天数（返回纯数字）"""
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
    return "希望你今天也要好好吃饭 乖乖睡觉 坏心情都与你无关！"

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
            "min_temperature": {"value": min_temp, "color": "#0000FF"},
            "max_temperature": {"value": max_temp, "color": "#FF0000"},
            "love_day": {"value": get_love_days(), "color": "#FF00FF"},
            "message": {"value": get_morning_message(), "color": "#00AA00"}
        }
    }
    
    response = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}",
        json=data
    )
    print("推送结果：", response.json())

if __name__ == "__main__":
    # 测试数据获取
    print("[测试]天气数据:", get_weather("辽宁", "鞍山"))
    print("[测试]认识天数:", get_love_days())
    print("[测试]早安文案:", get_morning_message())
    
    # 等待推送时间
    print("等待推送时间...")
    while datetime.now().strftime("%H:%M:%S") < config.post_time:
        time.sleep(1)
    
    print("开始推送...")
    send_daily_message()
