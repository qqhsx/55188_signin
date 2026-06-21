import requests
import time
import os
import re
import socket
import traceback
from datetime import datetime
from wx_msg import send_wx


# =========================
# 配置：改成 IP 直连
# =========================
TARGET_IP = "1.13.12.71"
BASE_HOST = "www.55188.com"

BASE_URL = f"https://{TARGET_IP}"


corpid = os.getenv("WX_CORPID") or ""
corpsecret = os.getenv("WX_CORPSECRET") or ""
agentid = os.getenv("WX_AGENTID") or ""


# =========================
# 安全请求
# =========================
def safe_get(session, url, desc="", retry=3):

    for i in range(retry):

        try:
            print(f"[REQUEST] {desc} 第{i+1}次 -> {url}")

            return session.get(
                url,
                timeout=20,
                verify=False,   # 🔥 关键：忽略证书
                headers={
                    "Host": BASE_HOST  # 🔥 关键：伪装域名
                }
            )

        except Exception as e:
            print(f"[ERROR] {desc}: {e}")
            time.sleep(2 * (i + 1))

    raise Exception(f"{desc} 请求失败")


# =========================
# 用户名脱敏
# =========================
def mask_username(username):

    username = username.strip()

    if len(username) <= 1:
        return username
    elif len(username) == 2:
        return username[0] + "*"
    else:
        return username[0] + "*" * (len(username) - 2) + username[-1]


# =========================
# 签到逻辑
# =========================
def sign_in(cookie_str, index=1):

    print("\n" + "=" * 60)
    print(f"[START] 账号 {index}")

    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"{BASE_URL}/plugin.php?id=sign",
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
    # DNS skip（直接IP）
    # =========================
    print(f"[INFO] 使用IP直连: {TARGET_IP}")

    # =========================
    # 首页
    # =========================
    try:
        r_home = safe_get(
            session,
            f"{BASE_URL}",
            desc="HOME"
        )
        print("[HOME] STATUS:", r_home.status_code)

    except Exception as e:
        print("[HOME FAILED BUT CONTINUE]", e)

    # =========================
    # 签到页
    # =========================
    try:
        r1 = safe_get(
            session,
            f"{BASE_URL}/plugin.php?id=sign",
            desc="SIGN PAGE"
        )

        r1.encoding = r1.apparent_encoding
        html = r1.text

    except Exception:
        err = traceback.format_exc()

        send_wx(
            f"[55188] 签到失败\n\n{err}",
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
    # 判断
    # =========================
    if "游客" in html:
        msg = "❌ Cookie失效"

    elif 'id="addsign"' not in html:
        msg = "✅ 今日已签到"

    else:
        try:
            r2 = safe_get(
                session,
                f"{BASE_URL}/plugin.php?id=sign&mod=add&jump=1",
                desc="SIGN ACTION"
            )

            if "success" in r2.text:
                msg = "🎉 签到成功"
            elif "Access Denied" in r2.text:
                msg = "🛑 Access Denied"
            else:
                msg = "⚠️ 未知结果"

        except Exception:
            msg = "❌ 签到失败"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = f"""
[55188] 签到结果（IP直连模式）

账号：{username_show}
IP：{TARGET_IP}
时间：{now}

{msg}
"""

    print(result)

    send_wx(result, corpid, corpsecret, agentid)


# =========================
# main
# =========================
if __name__ == "__main__":

    cookies = os.getenv("MY_COOKIE") or ""

    if not cookies.strip():
        print("❌ 未检测到 COOKIE")
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
