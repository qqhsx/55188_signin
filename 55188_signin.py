import requests
import time
import os

def sign_in(cookie_str):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.55188.com/plugin.php?id=sign",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    session.cookies.update(dict(i.strip().split("=", 1) for i in cookie_str.split(";") if "=" in i))

    # 1️⃣ 访问签到页，保留 server-set cookie
    r1 = session.get("https://www.55188.com/plugin.php?id=sign")
    r1.encoding = r1.apparent_encoding
    html = r1.text

    # 判断登录、签到状态
    if '您好，游客！' in html or '安全验证' in html:
        print("❌ 登录失效")
        return
    print("✅ 登录成功")
    signed = 'id="addsign"' not in html
    if signed:
        print("✅ 今天已签到")
        return
    print("❌ 今天还未签到")

    # 这里只简单延迟
    time.sleep(1)

    # 3️⃣ 发起签到请求
    r2 = session.get("https://www.55188.com/plugin.php?id=sign&mod=add&jump=1")
    r2.encoding = r2.apparent_encoding
    # print("✉️签到接口 response 状态码", r2.status_code)
    # print("✉️签到接口 response 前500字符：")
    # print(r2.text[:500])

    if 'success' in r2.text:
        print("🎉 签到成功！")
    elif 'Access Denied' in r2.text:
        print("🛑 Access Denied — 可能需要中转页token 或更完整headers")
    else:
        print("⚠️ 签到失败")

# 使用方式
if __name__ == "__main__":
    my_cookie = os.getenv("MY_COOKIE")
    if not my_cookie:
        print("❌ 未检测到环境变量 MY_COOKIE，请设置后重试")
    else:
        sign_in(my_cookie)
