📌 使用方法（Usage）

这个项目用于自动在 55188论坛 签到。

✅ 第一步：Fork 本仓库

打开本项目页面

点击右上角 Fork 按钮（复制到你自己的 GitHub 账号下）

✅ 第二步：设置 Cookie

登录 https://www.55188.com

按 F12 打开开发者工具 → 切换到 网络（Network）

刷新页面（F5），点第一个请求 → Headers → 找到 Cookie: 字段

复制整串 Cookie 值（“Cookie:”后的字符）

示例：55188_passport=xxx; cdb2_auth=yyy; passport2bbs=zzz; ...

回到你的 GitHub 仓库页面

→ 点上方 Settings → 左侧 Secrets and variables → Actions→ 点 New repository secret：

Name: MY_COOKIE

Value: 粘贴刚才的 Cookie

✅ 第三步：测试运行

点击上方 Actions

首次 Fork 在 Actions 页面点击 Enable workflows 以启用自动任务。

选择 Auto Sign-in for BBS

点击右侧 Run workflow → 等待运行完成
