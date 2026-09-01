
# PikPak VIP 自动邀请程序 (Docker 优化版)

基于 Python 和 PyWebIO 编写的 PikPak 临时会员自动邀请程序。通过提供网页端 UI，配合微软邮箱自动接收验证码，实现 PikPak 邀请奖励的自动化获取。

* **原作者**：B站纸鸢的花语
* **二改作者**：非雨
* **当前优化版**：针对 NAS 和云服务器 Docker 部署进行了深度重构与修复。

---

## ✨ 版本更新说明 (当前优化版)

此版本在原版 v1.2 的基础上进行了核心稳定性和部署兼容性的修复：
1. **彻底修复 `add_days` 崩溃 Bug**：增加了对所有网络请求返回值的严格校验，在遭遇 IP 封禁或风控时平滑处理，不再导致程序异常崩溃。
2. **多线程并发安全**：引入线程锁（`threading.Lock`），彻底解决多线程并发读写导致 `emails.txt` 账号文件被清空或覆盖的问题。
3. **解除硬编码路径**：废弃了原有的 `C:\...` 绝对路径，改为相对路径读取，完美适配 Linux/NAS 环境。
4. **现代化 CI/CD 支持**：支持利用 GitHub Actions 自动构建跨架构（x86_64 / ARM64）Docker 镜像，发布至 GitHub Packages (GHCR)。

---

## 🚀 如何在 NAS / 服务器上部署 (推荐)

本项目已支持 Docker 容器化部署，极度推荐在群晖、威联通等 NAS 或者是 Linux 云服务器上运行，不仅干净且支持 7x24 小时挂机。

### 1. 准备账号文件
在你的 NAS 或服务器本地新建一个目录（例如 `/volume1/docker/pikpak`），并在里面新建一个文本文件命名为 `emails.txt`。
在里面填入你的微软邮箱账号和密码，格式如下（每行一个）：
```text
your_email1@outlook.com----your_password1
your_email2@outlook.com----your_password2

```

### 2. 拉取并运行 Docker 镜像

通过 SSH 终端或 NAS 的任务计划程序，执行以下命令：

```bash
docker run -d \
  --name pikpak-inviter \
  --restart unless-stopped \
  -p 8081:8081 \
  -v /你的实际路径/emails.txt:/app/emails.txt \
  ghcr.io/workerspages/pikpak-inviter:latest

```

*(⚠️ 请注意将 `-v` 挂载参数中的 `/你的实际路径/` 替换为你刚刚创建 `emails.txt` 的绝对路径)*

### 3. 开始使用

容器启动后，在同一局域网内的浏览器中输入：
👉 `http://<你NAS的IP地址>:8081`

即可打开 PyWebIO 的邀请控制台。填入你的 PikPak 邀请码和卡密即可自动开始运行。

---

## 💻 本地 Python 源码运行

如果你希望在本地 Windows/Mac 电脑上运行：

1. 安装 Python 3.8+ 环境。
2. 安装依赖库：
```bash
pip install requests pywebio

```


3. 在同一目录下准备好 `emails.txt`。
4. 运行脚本：
```bash
python werbio_v1.2.py

```



---

## ⚠️ 声明与注意事项

1. **仅供学习交流**：本代码仅供 Python 网络请求及 PyWebIO 技术交流分析使用。
2. **严禁商业牟利**：严禁利用此脚本进行任何商业牟利行为（包括但不限于引流、贩卖、代刷等）。
3. **免责声明**：出现任何后果（如 PikPak 账号风控、封禁）由使用者自行承担，与源码分享者无关。如出现违反规定的侵权行为，原作者有权对违规者进行版权控诉处理。
4. **风控提示**：邀请过多可能会导致充不上 VIP 或需要换号，建议随用随充，勿恶意批量多刷。

```
