import requests
import time
import os
import re
import socket
import traceback
from datetime import datetime
from wx_msg import send_wx


corpid = os.getenv("WX_CORPID") or ""
corpsecret = os.getenv("WX_CORPSECRET") or ""
agentid = os.getenv("WX_AGENTID") or ""


# =========================
# 请求增强：重试 + 超时分类
# =========================
def safe_get(session, url, desc="", retry=3, timeout=20):

    for i in range(retry):

        try:
            print(f"[REQUEST] {desc} 第{i+1}次 -> {url}")

            return session.get(url, timeout=timeout)

        except requests.exceptions.SSLError as e:
            print(f"[SSL ERROR] {desc}: {e}")

        except requests.exceptions.ConnectTimeout as e:
            print(f"[CONNECT TIMEOUT] {desc}: {e}")

        except requests.exceptions.ReadTimeout as e:
            print(f"[READ TIMEOUT] {desc}: {e}")

        except requests.exceptions.ConnectionError as e:
            print(f"[CONNECTION ERROR] {desc}: {e}")

        except Exception as e:
            print(f"[UNKNOWN ERROR] {desc}: {e}")

        time.sleep(2 * (i + 1))

    raise Exception(f"[FAILED] {desc} 多次重试失败 -> {url}")


def mask_username(username):

    username = username.strip()

    if len(username) <= 1:
        return username
    elif len(username) == 2:
        return username[0] + "*"
    else:
        return username[0] + "*" * (len(username) - 2) + username[-1]


def sign_in(cookie_str, index=1):

    print("\n" + "=" * 60)
    print(f"[START] 账号 {index}")

    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.55188.com/plugin.php?id=sign",
        "Connection": "keep-alive",
    })

    session.cookies.update(
        dict(
            i.strip().split("=", 1)
            for i in cookie_str.split(";")
            if "=" in i
        )
    )

    # =========================
    # DNS
    # =========================
    try:
        ip = socket.gethostbyname("www.55188.com")
        print(f"[DNS] www.55188.com -> {ip}")
    except Exception:
        print("[DNS ERROR]")
        traceback.print_exc()

    # =========================
    # 首页（可失败）
    # =========================
    try:
        home = safe_get(
            session,
            "https://www.55188.com",
            desc="HOME"
        )

        print(f"[HOME] STATUS -> {home.status_code}")

    except Exception as e:
        print("[HOME FAILED BUT CONTINUE]")
        print(e)

    # =========================
    # 签到页（核心）
    # =========================
    try:
        r1 = safe_get(
            session,
            "https://www.55188.com/plugin.php?id=sign",
            desc="SIGN PAGE"
        )

        print(f"[SIGN] STATUS -> {r1.status_code}")

        r1.encoding = r1.apparent_encoding
        html = r1.text

    except Exception as e:

        err = traceback.format_exc()

        send_wx(
            f"""[55188] 签到失败

账号：{index}

{err}
""",
            corpid,
            corpsecret,
            agentid
        )
        return

    # =========================
    # 用户名
    # =========================
    username = f"账号{index}"

    patterns = [
        r'您好：([^<]+)</a>',
        r'欢迎您回来，([^<]+)<',
        r'欢迎您，([^<]+)<',
    ]

    for p in patterns:
        m = re.search(p, html)
        if m:
            username = m.group(1).strip()
            break

    username_show = mask_username(username)

    # =========================
    # 状态判断
    # =========================
    msg = ""

    if "游客" in html or "安全验证" in html:
        msg = "❌ Cookie失效"

    else:

        if 'id="addsign"' not in html:
            msg = "✅ 今日已签到"
        else:

            try:

                r2 = safe_get(
                    session,
                    "https://www.55188.com/plugin.php?id=sign&mod=add&jump=1",
                    desc="SIGN ACTION"
                )

                if "success" in r2.text:
                    msg = "🎉 签到成功"
                elif "Access Denied" in r2.text:
                    msg = "🛑 Access Denied"
                else:
                    msg = "⚠️ 未知返回"

            except Exception:
                msg = "❌ 签到失败"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = f"""
[55188] 签到结果

账号：{username_show}
时间：{now}

{msg}
"""

    print(result)

    send_wx(result, corpid, corpsecret, agentid)


if __name__ == "__main__":

    cookies = os.getenv("MY_COOKIE") or ""

    if not cookies.strip():
        print("❌ 未检测到 MY_COOKIE")
        exit()

    cookie_list = [c.strip() for c in cookies.split("\n") if c.strip()]

    for i, cookie in enumerate(cookie_list, 1):

        try:
            sign_in(cookie, i)

        except Exception:
            err = traceback.format_exc()

            print(err)

            send_wx(
                f"[55188] 全局异常\n账号{i}\n\n{err}",
                corpid,
                corpsecret,
                agentid
            )

        time.sleep(2)
