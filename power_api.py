
import requests

API_URL = "http://202.192.240.231/scp-api/electricity-recharge/getCurrentRemaining_v2"

#如果要在其他学校使用，需要替换成相应的地址喵，这个只能在wyu校园网内网访问

API_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    # 很多学校靠 Cookie 鉴权，如果需要自行抓包，wyu不需要喵
    # "Cookie": "JSESSIONID=xxxx; 其他=yyy",
    # "Referer": "https://学校电费查询页面地址",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
}


def build_payload(building: str, room: str) -> dict:
    return {
        "userTypeID": "1",
        "building": building,
        "room": room,
    }


def parse_response(raw) -> dict:
    try:
        if not raw.get("success"):
            return {
                "success": False,
                "remaining": 0,
                "used": 0,
                "msg": f"接口返回失败: {raw.get('message')}",
            }

        data = raw["data"]
        return {
            "success": True,
            "remaining": float(data["resamp"]),   # 剩余电量
            "used": float(data["usedamp"]),       # 已用电量
            "room_name": data.get("roomName", ""),
            "apart_name": data.get("apartName", ""),
            "updated": data.get("updatedt", ""),
            "status": data.get("status"),
            "msg": "ok",
        }
    except Exception as e:
        return {"success": False, "remaining": 0, "used": 0, "msg": f"解析失败: {e} | {str(raw)[:200]}"}


def query_power(building: str, room: str) -> dict:
    try:
        resp = requests.post(
            API_URL,
            data=build_payload(building, room),
            headers=API_HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        try:
            return parse_response(resp.json())
        except ValueError:
            resp.encoding = resp.apparent_encoding
            return {"success": False, "remaining": 0, "used": 0, "msg": f"返回不是JSON: {resp.text[:200]}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "remaining": 0, "used": 0, "msg": f"请求失败: {e}"}


if __name__ == "__main__":
    print(query_power("1", "101"))