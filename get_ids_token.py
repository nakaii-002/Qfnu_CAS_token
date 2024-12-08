from bs4 import BeautifulSoup
import requests
import time
from ids_utils.passwd_encrypt import get_encrypted_passwd
from ids_utils.captcha_ocr import get_ocr_res

session = requests.session()


def get_salt_and_execution(redir_uri):  # 拿到密码加密所需的盐和execution
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/117.0.5938.63 Safari/537.36",
        "Referer": "http://libyy.qfnu.edu.cn/"
    }
    response_data = session.get(url=redir_uri, headers=headers).text
    soup_decoded_data = BeautifulSoup(response_data, "html.parser")
    execution_data = soup_decoded_data.find(id='execution').get('value')
    salt_data = soup_decoded_data.find(id='pwdEncryptSalt').get('value')
    return salt_data, execution_data


def captcha_check(username):  # 检查是否需要验证码
    uri = "http://ids.qfnu.edu.cn/authserver/checkNeedCaptcha.htl"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/117.0.5938.63 Safari/537.36"
    }
    data = {
        "username": username,
        "_": int(round(time.time() * 1000))
    }
    res = session.get(url=uri, params=data, headers=headers)
    if "true" in res.text:
        return True
    else:
        return False


def get_captcha():  # 获取验证码
    uri = "http://ids.qfnu.edu.cn/authserver/getCaptcha.htl?" + str(int(round(time.time() * 1000)))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/117.0.5938.63 Safari/537.36"
    }
    res = session.get(url=uri, headers=headers)
    return res.content


def get_token(username, password, redir_uri):  # 返回带有ticket的链接
    cap_res = ""
    salt, execution_data = get_salt_and_execution(redir_uri)
    print("[+]-----正在检查是否需要验证码")
    if captcha_check(username):
        print("[+]-----需要验证码，正在尝试获取验证码")
        try:
            cap_pic = get_captcha()
            cap_res = get_ocr_res(cap_pic)
            cap_res = cap_res.lower()
        except :
            print("[+]-----获取或识别验证码失败")
    else:
        print("[+]-----无需验证码，尝试获取Token")

    enc_passwd = get_encrypted_passwd(password, salt)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/117.0.5938.63 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": username,
        "password": enc_passwd,
        "captcha": cap_res,
        "_eventId": "submit",
        "cllt": "userNameLogin",
        "dllt": "generalLogin",
        "lt": "",
        "execution": execution_data
    }

    res = session.post(url=redir_uri, headers=headers, data=data, allow_redirects=False)
    return res.headers["Location"]


if __name__ == '__main__':
    print(get_token('your_account', 'your_password',
                    "http://ids.qfnu.edu.cn/authserver/login?service=http%3A%2F%2Fzhjw.qfnu.edu.cn%2Fsso.jsp"))
