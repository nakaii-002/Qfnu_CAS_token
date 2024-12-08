import random
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def random_string(length):  # 获取随机字符
    aes_chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
    aes_chars_len = len(aes_chars)
    res = ''
    for _ in range(length):
        res += aes_chars[random.randint(0, aes_chars_len - 1)]
    return res


def get_aes_string(data, key, iv):  # 获取aes加密后密码
    data = data.strip()
    data = data.encode('utf-8')
    key_encoded = key.encode('utf-8')
    iv_encoded = iv.encode('utf-8')
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key_encoded), modes.CBC(iv_encoded), backend=backend)

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')

    return encrypted_base64


def get_encrypted_passwd(passwd, salt):
    return get_aes_string(random_string(64)+passwd, salt, random_string(16))


if __name__ == "__main__":
    print(get_encrypted_passwd('', 'LqqQdC3a3DIin1P1'))
