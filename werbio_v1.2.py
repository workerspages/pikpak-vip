import poplib
import hashlib
import json
import random
import re
import time
import requests
import email
import threading # 引入线程锁

from concurrent.futures import ThreadPoolExecutor
from pywebio.input import input_group, input, TEXT
from pywebio.output import put_text, put_markdown, clear, put_html
from pywebio import start_server
from datetime import datetime

# -------------改这里-------------
# 替换为自己txt文件所在地址
file_path = r'C:\Users\admin\小米云盘\桌面\邮箱.txt'

# 定义卡密和其使用次数
card_keys = {
    "0727-0827-3382SJ2SJ": 10000,
    "替换为自己想要的卡密": 10
}
# --------------------------------

# 文件读写锁，防止多线程把文件写坏
file_lock = threading.Lock()

def read_and_process_file(file_path):
    try:
        email_user_list = []
        email_pass_list = []
        with file_lock:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            updated_lines = []
            for line in lines:
                line = line.strip()
                if "登录成功" in line or "失败" in line:
                    continue
                match = re.match(r'^(.+?)----([^\s@]+)$', line)
                if match:
                    email_addr, password = match.groups()
                    email_user_list.append(email_addr)
                    email_pass_list.append(password)
                else:
                    updated_lines.append(line)
        return email_user_list, email_pass_list
    except Exception as e:
        print("读取文件失败:", e)
        return None, None

def update_file_status(file_path, email_addr, password, status):
    try:
        with file_lock:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open(file_path, 'w', encoding='utf-8') as file:
                for line in lines:
                    if line.strip().startswith(email_addr) and "----" in line:
                        file.write(f"{line.strip()} {status}\n")
                    else:
                        file.write(line)
    except Exception as e:
        print("更新文件状态失败:", e)

def get_email_with_third_party(recipient_email, email_user, email_pass, delay=2, max_retries=40):
    pop3_server = "pop-mail.outlook.com"
    retries = 0
    while retries < max_retries:
        try:
            mail = poplib.POP3_SSL(pop3_server)
            mail.user(email_user)
            mail.pass_(email_pass)
            num_messages = len(mail.list()[1])
            for i in range(num_messages):
                response, lines, octets = mail.retr(i + 1)
                raw_email = b'\n'.join(lines)
                code = process_email(raw_email, i + 1, mail)
                if code:
                    mail.quit()
                    return code
            mail.quit()
        except Exception as e:
            pass # 屏蔽每次报错干扰
        retries += 1
        time.sleep(delay)
    return None

def process_email(raw_email, email_id, mail):
    email_message = email.message_from_bytes(raw_email)
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                body = part.get_payload(decode=True)
                body_text = body.decode('utf-8', errors='ignore')
                match = re.search(r'\d{6}', body_text)
                if match:
                    code = match.group()
                    print(f'获取到验证码: {code}')
                    return code
    else:
        body = email_message.get_payload(decode=True)
        body_text = body.decode('utf-8', errors='ignore')
        match = re.search(r'\d{6}', body_text)
        if match:
            code = match.group()
            print(f'获取到验证码: {code}')
            return code
    return None

def wxpusher(new_email, password, invitation_code):
    global randint_ip
    app_token = ""
    if app_token:
        api_url = "https://wxpusher.zjiecode.com/api/send/message"
        data = {
            "appToken": app_token,
            "summary": "邀请成功: " + invitation_code,
            "content": "<h1>PikPak运行结果通知🔔</h1><br/><h3>邀请码：" + invitation_code + "</h3><h4>账户：" + new_email + "</h4><h4>密码：" + password + "</h4>",
            "contentType": 2,
            "topicIds": [30126],
            "uids": [],
            "verifyPayType": 0
        }
        headers = {'Content-Type': 'application/json'}
        try:
            requests.post(api_url, headers=headers, data=json.dumps(data), timeout=5)
        except:
            pass

def get_proxy():
    proxies = {}
    return proxies

def get_randint_ip():
    return f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

randint_ip = get_randint_ip()

def r(e, t):
    n = max(t - 1, 0)
    r_val = e[n]
    u = r_val["row"] // 2 + 1
    c = r_val["column"] // 2 + 1
    f = r_val["matrix"][u][c]
    l = t + 1 if (t + 1) < len(e) else t
    d = e[l]
    p = l % d["row"]
    h = l % d["column"]
    g = d["matrix"][p][h]
    y = e[t]
    m = 3 % y["row"]
    v = 7 % y["column"]
    w = y["matrix"][m][v]
    b = i(f) + o(w)
    x = i(w) - o(f)
    return [s(a(i(f), o(f))), s(a(i(g), o(g))), s(a(i(w), o(w))), s(a(b, x))]

def i(e): return int(e.split(",")[0])
def o(e): return int(e.split(",")[1])
def a(e, t): return str(e) + "^^" + str(t)

def s(e):
    t = 0
    for char in e:
        t = u(31 * t + ord(char))
    return t

def u(e):
    t = -2147483648
    n = 2147483647
    if e > n: return t + (e - n) % (n - t + 1) - 1
    if e < t: return n - (t - e) % (n - t + 1) + 1
    return e

def c(e, t):
    return s(e + "⁣" + str(t))

def img_jj(e, t, n):
    return {"ca": r(e, t), "f": c(n, t)}

def uuid():
    return ''.join([random.choice('0123456789abcdef') for _ in range(32)])

def md5(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()

def get_sign(xid, t):
    e = [
        {"alg": "md5", "salt": "KHBJ07an7ROXDoK7Db"},
        {"alg": "md5", "salt": "G6n399rSWkl7WcQmw5rpQInurc1DkLmLJqE"},
        {"alg": "md5", "salt": "JZD1A3M4x+jBFN62hkr7VDhkkZxb9g3rWqRZqFAAb"},
        {"alg": "md5", "salt": "fQnw/AmSlbbI91Ik15gpddGgyU7U"},
        {"alg": "md5", "salt": "/Dv9JdPYSj3sHiWjouR95NTQff"},
        {"alg": "md5", "salt": "yGx2zuTjbWENZqecNI+edrQgqmZKP"},
        {"alg": "md5", "salt": "ljrbSzdHLwbqcRn"},
        {"alg": "md5", "salt": "lSHAsqCkGDGxQqqwrVu"},
        {"alg": "md5", "salt": "TsWXI81fD1"},
        {"alg": "md5", "salt": "vk7hBjawK/rOSrSWajtbMk95nfgf3"}
    ]
    md5_hash = f"YvtoWO6GNHiuCl7xundefinedmypikpak.com{xid}{t}"
    for item in e:
        md5_hash += item["salt"]
        md5_hash = md5(md5_hash)
    return md5_hash

# 为了节省篇幅，所有网络请求我加上了默认返回值 {}，防止后续引发异常
def init(xid, mail):
    global randint_ip
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {"client_id": "YvtoWO6GNHiuCl7x", "action": "POST:/v1/auth/verification", "device_id": xid, "captcha_token": "", "meta": {"email": mail}}
    headers = {'host': 'user.mypikpak.com', 'user-agent': 'MainWindow Mozilla/5.0...', 'content-type': 'application/json', 'x-device-id': xid, 'X-Forwarded-For': str(randint_ip)}
    for _ in range(3):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('初始安全验证')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def get_new_token(xid, captcha):
    for _ in range(3):
        try:
            resp = requests.get(f"https://user.mypikpak.com/credit/v1/report?deviceid={xid}&captcha_token={captcha}&type=pzzlSlider&result=0", proxies=get_proxy(), timeout=5)
            return resp.json()
        except:
            time.sleep(1)
    return {}

def verification(captcha_token, xid, mail):
    url = 'https://user.mypikpak.com/v1/auth/verification'
    body = {"email": mail, "target": "ANY", "usage": "REGISTER", "locale": "zh-CN", "client_id": "YvtoWO6GNHiuCl7x"}
    headers = {'host': 'user.mypikpak.com', 'content-type': 'application/json', 'x-captcha-token': captcha_token, 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('发送验证码')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def verify(xid, verification_id, code):
    url = 'https://user.mypikpak.com/v1/auth/verification/verify'
    body = {"verification_id": verification_id, "verification_code": code, "client_id": "YvtoWO6GNHiuCl7x"}
    headers = {'host': 'user.mypikpak.com', 'content-type': 'application/json', 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('验证码验证结果')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def signup(xid, mail, code, verification_token):
    url = 'https://user.mypikpak.com/v1/auth/signup'
    body = {"email": mail, "verification_code": code, "verification_token": verification_token, 'name': f'qihang{random.randint(1, 10000000)}vip', "password": "qwe103", "client_id": "YvtoWO6GNHiuCl7x"}
    headers = {'host': 'user.mypikpak.com', 'content-type': 'application/json', 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('验证注册结果')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def init1(xid, access_token, sub, sign, t):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {"client_id": "YvtoWO6GNHiuCl7x", "action": "POST:/vip/v1/activity/invite", "device_id": xid, "captcha_token": access_token, "meta": {"captcha_sign": "1." + sign, "client_version": "undefined", "package_name": "mypikpak.com", "user_id": sub, "timestamp": t}}
    headers = {'host': 'user.mypikpak.com', 'content-type': 'application/json', 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('通过二次安全验证')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def invite(access_token, captcha_token, xid):
    url = 'https://api-drive.mypikpak.com/vip/v1/activity/invite'
    body = {"apk_extra": {"invite_code": ""}}
    headers = {'host': 'api-drive.mypikpak.com', 'content-type': 'application/json', 'authorization': 'Bearer ' + access_token, 'x-captcha-token': captcha_token, 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('确认邀请')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def init2(xid, access_token, sub, sign, t):
    url = 'https://user.mypikpak.com/v1/shield/captcha/init'
    body = {"client_id": "YvtoWO6GNHiuCl7x", "action": "post:/vip/v1/order/activation-code", "device_id": xid, "captcha_token": access_token, "meta": {"captcha_sign": "1." + sign, "client_version": "undefined", "package_name": "mypikpak.com", "user_id": sub, "timestamp": t}}
    headers = {'host': 'user.mypikpak.com', 'content-type': 'application/json', 'x-device-id': xid}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('通过三次安全验证')
            return resp.json()
        except:
            time.sleep(1)
    return {}

def activation_code(access_token, captcha, xid, in_code):
    global randint_ip
    url = 'https://api-drive.mypikpak.com/vip/v1/order/activation-code'
    body = {"activation_code": in_code, "page": "invite"}
    headers = {'host': 'api-drive.mypikpak.com', 'content-type': 'application/json', 'authorization': 'Bearer ' + access_token, 'x-captcha-token': captcha, 'x-device-id': xid, 'X-Forwarded-For': str(randint_ip)}
    for _ in range(2):
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=5)
            print('开始填写邀请码')
            return resp.json()
        except:
            time.sleep(1)
    return {}

# -------------------------- 主逻辑处理 --------------------------
invitation_records = {}

def main(incode, num_invitations=1):
    now = datetime.now()
    print("当前日期: ", now)
    start_time = time.time()
    success_count = 0
    global invitation_records
    current_time = time.time()

    if incode in invitation_records:
        last_submissions = [t for t in invitation_records[incode] if current_time - t < 36000]
        if len(last_submissions) >= 1:
            return "10小时内已提交，请稍后再试。"
        invitation_records[incode] = last_submissions
    else:
        invitation_records[incode] = []

    while success_count < num_invitations:
        try:
            xid = uuid()
            email_users, email_passes = read_and_process_file(file_path)

            if not email_users or not email_passes:
                return "未能读取邮箱或密码，请检查文本格式"

            for email_user, email_pass in zip(email_users, email_passes):
                mail = email_user

                Init = init(xid, mail)
                if not Init: continue  # 网络请求失败兜底

                captcha_token_info = get_new_token(xid, Init.get('captcha_token', ''))
                Verification = verification(captcha_token_info.get('captcha_token', ''), xid, mail)
                
                if not Verification.get('verification_id'):
                    print("未获取到 verification_id，触发限制")
                    continue

                code = get_email_with_third_party(mail, email_user, email_pass)
                if not code:
                    print(f"无法从邮箱获取验证码: {mail}")
                    continue

                verification_response = verify(xid, Verification.get('verification_id'), code)
                signup_response = signup(xid, mail, code, verification_response.get('verification_token', ''))
                
                if 'access_token' not in signup_response:
                    print(f"注册失败或被风控: {signup_response}")
                    update_file_status(file_path, email_user, email_pass, "失败")
                    continue

                curr_t = str(int(time.time()))
                sign = get_sign(xid, curr_t)
                
                init1_response = init1(xid, signup_response['access_token'], signup_response.get('sub',''), sign, curr_t)
                invite(signup_response['access_token'], init1_response.get('captcha_token', ''), xid)
                
                init2_response = init2(xid, signup_response['access_token'], signup_response.get('sub',''), sign, curr_t)
                activation = activation_code(signup_response['access_token'], init2_response.get('captcha_token', ''), xid, incode)

                end_time = time.time()
                run_time = f'{(end_time - start_time):.2f}'

                # 【核心修复点】对 activation 增加合法性以及 NoneType 的校验
                if isinstance(activation, dict) and activation.get('add_days') == 5:
                    result = f"邀请成功 邀请码: {incode} email: {mail} 密码：qwe103"
                    print(result)
                    success_count += 1
                    invitation_records[incode].append(time.time())
                    update_file_status(file_path, email_user, email_pass, "登录成功")
                    # wxpusher(mail, "qwe103", incode) # 推送通知可选
                    return f"邀请成功: {incode} 运行时间: {run_time}秒<br> 邮箱: {mail} <br> 密码: qwe103"
                elif isinstance(activation, dict) and activation.get('add_days') == 0:
                    result = f'邀请码: {incode} 邀请失败, 重试...'
                    print(result)
                    update_file_status(file_path, email_user, email_pass, "失败")
                    return result
                else:
                    result = f"未知情况/接口被限制: {activation}"
                    print(result)
                    update_file_status(file_path, email_user, email_pass, "失败")
                    return result

        except Exception as e:
            if "add_days" in str(e):
                result = f"异常: 取不到add_days字段，可能遭遇网络屏蔽或风控。"
            else:
                result = f'运行时抛出异常: {e}'
            print(result)
            return result


# html页面
def web_app():
    put_html('''
        <style>
            .footer { display: none !important; }
            .pywebio_header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
            .km_title { text-align: center; color: #495057; font-size: 12px; }
        </style>
    ''')

    put_html('<script>document.title = "PIKPAK临时会员邀请程序";</script>')
    put_html('<div class="pywebio_header">PIKPAK临时会员邀请程序</div>')
    put_html('<div class="km_title">随用随充次日会员会掉 邀请超50人充不上需要换号 多刷无效<br> 服务器断开/页面卡住解决方法: 复制网址到微信消息里访问</div>')

    form_data = input_group("", [
        input("请输入你的邀请码6-8位数字:", name="incode", type=TEXT, required=True, placeholder="打开pikpak我的界面-引荐奖励计划-获取邀请码数字"),
        input("请输入卡密:", name="card_key", type=TEXT, required=True, placeholder="请输入卡密")
    ])

    incode = form_data['incode']
    card_key = form_data['card_key']

    if card_key not in card_keys or card_keys[card_key] <= 0:
        put_text("卡密无效或次数用尽，请联系客服")
        return

    card_keys[card_key] -= 1
    clear()
    
    put_html('''
        <div id="countdown" style="text-align: center;">
            正在邀请中...请不要退出页面， <span id="time">30</span> 秒 <br>
            页面倒计时为1秒还未跳转请刷新页面重试一遍
        </div>
        <script>
            var timeLeft = 30;
            var countdownTimer = setInterval(function(){
                if(timeLeft <= 0){
                    clearInterval(countdownTimer);
                    pywebio.output.put_markdown("## 邀请结果");
                } else {
                    document.getElementById("time").innerHTML = timeLeft;
                }
                timeLeft -= 1;
            }, 1000);
        </script>
    ''')

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(main, incode) for _ in range(1)]
        for future in futures:
            result = future.result()
            print(result)
            results.append(result)

    clear()
    put_markdown("## 邀请结果")
    put_html('<style>.result-container { text-align: center; font-size: 18px; margin-top: 20px; }</style>')
    for result in results:
        put_html(f'<div class="result-container">{result}</div>')

if __name__ == '__main__':
    start_server(web_app, host='0.0.0.0', port=8081)
