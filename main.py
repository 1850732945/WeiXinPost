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
    """获取天气信息"""
    # 这里需要确保有cityinfo.py文件提供城市ID
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    headers = {
        "Referer": f"http://www.weather.com.cn/weather1d/{city_id}.shtml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    url = f"http://d1.weather.com.cn/dingzhi/{city_id}.html?_={int(time.time()*1000)}"
    response = requests.get(url, headers=headers)
    weather_data = eval(response.text.split(";")[0].split("=")[-1])
    info = weather_data["weatherinfo"]
    return info["weather"], info["temp"], info["tempn"]

def get_love_days():
    """计算认识天数"""
    start_date = datetime.strptime(config.love_date, "%Y-%m-%d").date()
    return (date.today() - start_date).days

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
    return "早安，愿今天又是美好的一天！"  # 默认文案

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
