import requests
import time
import os
import re
from datetime import datetime
from wx_msg import send_wx

corpid = os.getenv("WX_CORPID") or ""
corpsecret = os.getenv("WX_CORPSECRET") or ""
agentid = os.getenv("WX_AGENTID") or ""


def mask_username(username):
    """
    用户名脱敏
    """

    username = username.strip()

    if len(username) <= 1:
        return username

    elif len(username) == 2:
        return username[0] + "*"

    else:
        return username[0] + "*" * (len(username) - 2) + username[-1:]


def sign_in(cookie_str, index=1):

    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.55188.com/plugin.php?id=sign",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })

    session.cookies.update(
        dict(
            i.strip().split("=", 1)
            for i in cookie_str.split(";")
            if "=" in i
        )
    )

    r1 = session.get("https://www.55188.com/plugin.php?id=sign")
    r1.encoding = r1.apparent_encoding
    html = r1.text

    # 获取用户名
    username = f"账号{index}"

    patterns = [
        r'您好：([^<]+)</a>',
        r'uid=\d+[^>]*>([^<]+)</a>',
        r'space-uid-\d+[^>]*>([^<]+)</a>',
        r'title="访问我的空间"[^>]*>([^<]+)</a>',
        r'欢迎您回来，([^<]+)<',
        r'欢迎您，([^<]+)<',
    ]

    for p in patterns:
        m = re.search(p, html)
        if m:
            username = m.group(1).strip()
            break

    # 用户名脱敏
    username_show = mask_username(username)

    msg = ""
    msg1 = ""
    msg2 = ""

    # 登录检测
    if '您好，游客！' in html or '安全验证' in html:
        msg = "❌ 登录失效，请检查Cookie"

    else:
        msg1 = "✅ 登录成功\n"

        # 是否已签到
        if 'id="addsign"' not in html:
            msg = "✅ 今天已签到，无需重复操作。"

        else:
            msg2 = "❌ 今天还未签到，准备签到...\n"

            time.sleep(1)

            r2 = session.get(
                "https://www.55188.com/plugin.php?id=sign&mod=add&jump=1"
            )

            r2.encoding = r2.apparent_encoding

            if 'success' in r2.text:
                msg = "🎉 签到成功！"

            elif 'Access Denied' in r2.text:
                msg = "🛑 Access Denied，可能需要中转页token"

            else:
                msg = "⚠️ 未知错误"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    full_msg = f"""[55188] 签到结果

👤 账号：{username_show}
🕒 时间：{now}

{msg1}{msg2}{msg}
"""

    print(full_msg)

    send_wx(full_msg, corpid, corpsecret, agentid)


if __name__ == "__main__":

    # 多账号：每行一个 Cookie
    cookies = os.getenv("MY_COOKIE") or ""

    if not cookies.strip():
        print("❌ 未检测到环境变量 MY_COOKIE，请设置后重试")

    else:

        cookie_list = [
            c.strip()
            for c in cookies.split("\n")
            if c.strip()
        ]

        for idx, cookie in enumerate(cookie_list, start=1):

            print(f"\n========== 开始处理账号 {idx} ==========\n")

            try:

                sign_in(cookie, idx)

            except Exception as e:

                err_msg = f"""[55188] 签到异常

👤 账号：账号{idx}

❌ 错误：
{str(e)}
"""

                print(err_msg)

                send_wx(err_msg, corpid, corpsecret, agentid)

            time.sleep(2)
