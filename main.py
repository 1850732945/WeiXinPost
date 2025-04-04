import requests
import config
from datetime import datetime, date
import time

# 城市拼音映射表（心知天气使用拼音）
CITY_PINYIN_MAP = {
    "辽宁": {
        "鞍山": "anshan",
        "沈阳": "shenyang",
        "大连": "dalian"
    },
    "北京": {
        "北京": "beijing"
    },
    # 可继续添加其他城市...
}

def get_access_token():
    """获取微信access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.app_id}&secret={config.app_secret}"
    response = requests.get(url).json()
    return response["access_token"]

def get_weather(province, city):
    """使用心知天气API获取天气（含最高最低温）"""
    try:
        # 获取城市拼音ID
        city_pinyin = CITY_PINYIN_MAP.get(province, {}).get(city.lower())
        if not city_pinyin:
            raise ValueError(f"未找到城市 {province}{city} 的配置")
        
        # 请求每日预报（包含最高最低温）
        url = f"https://api.seniverse.com/v3/weather/daily.json?key={config.seniverse_api_key}&location={city_pinyin}&language=zh-Hans&unit=c&start=0&days=1"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # 解析数据
        daily = data["results"][0]["daily"][0]
        return {
            "weather": daily["text_day"],
            "temp_now": "N/A",  # 免费版不提供实时温度
            "temp_max": daily["high"],
            "temp_min": daily["low"]
        }
        
    except Exception as e:
        print(f"⚠️ 天气获取失败: {e}")
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
    return "早安，今天是充满希望的一天！"

def send_daily_message():
    """发送每日推送"""
    access_token = get_access_token()
    weather_data = get_weather(config.province, config.city)
    
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
    response = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}",
        json=data,
        timeout=5
    )
    print("推送结果：", response.json())

def test_all_functions():
    """测试所有功能模块"""
    print("\n=== 功能测试 ===")
    print("[天气] 鞍山:", get_weather("辽宁", "鞍山"))
    print("[天数] 认识天数:", get_love_days())
    print("[文案] 早安:", get_morning_message())
    
    # 测试微信access_token获取
    try:
        token = get_access_token()
        print("[微信] access_token 获取成功:", token[:10] + "..." if token else "空")
    except Exception as e:
        print(f"[微信] access_token 获取失败: {e}")

if __name__ == "__main__":
    # 执行测试
    test_all_functions()
    
    # 等待推送时间
    print(f"\n等待推送时间 {config.post_time}...")
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        if now >= config.post_time:
            print("\n开始推送...")
            send_daily_message()
            break
        time.sleep(1)
