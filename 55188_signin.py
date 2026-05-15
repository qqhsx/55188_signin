import requests
import time
import os
from wx_msg import send_wx  # 导入推送函数

corpid = os.getenv("WX_CORPID") or "ww3f27d938d39d2801"
corpsecret = os.getenv("WX_CORPSECRET") or "Qecy2ITn0KiFjg4qP09cKCFxfhsaUsDDa3BkLES9KyA"
agentid = os.getenv("WX_AGENTID") or "1000003"

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

    r1 = session.get("https://www.55188.com/plugin.php?id=sign")
    r1.encoding = r1.apparent_encoding
    html = r1.text
    msg = ""    # 主状态
    msg1 = ""   # 登录状态
    msg2 = ""   # 签到前状态

    if '您好，游客！' in html or '安全验证' in html:
        msg = "❌ 登录失效，请检查Cookie"
    else:
        msg1 = "✅ 登录成功\n"

        if 'id="addsign"' not in html:
            msg = "✅ 今天已签到，无需重复操作。"
        else:
            msg2 = "❌ 今天还未签到，准备签到...\n"
            time.sleep(1)
            r2 = session.get("https://www.55188.com/plugin.php?id=sign&mod=add&jump=1")
            r2.encoding = r2.apparent_encoding

            if 'success' in r2.text:
                msg = "🎉 签到成功！"
            elif 'Access Denied' in r2.text:
                msg = "🛑 Access Denied，可能需要中转页token"
            else:
                msg = "⚠️ 未知错误"

    # 最后统一输出和推送
    full_msg = f"[55188] 签到结果：\n{msg1}{msg2}{msg}"
    print(full_msg)
    send_wx(full_msg, corpid, corpsecret, agentid)


# 使用方式
if __name__ == "__main__":
    my_cookie = os.getenv("MY_COOKIE") or ""
    if not my_cookie:
        print("❌ 未检测到环境变量 MY_COOKIE，请设置后重试")
    else:
        sign_in(my_cookie)
