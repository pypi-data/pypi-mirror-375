# -- coding:utf-8 --
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class DecodeByte:
    # 解密
    @staticmethod
    def do_decode(key, iv, data, method="AES-128") -> bytes:
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(iv, str):
            iv = iv.encode('utf-8')
        if "AES-128" == method:
            aes = AES.new(key, AES.MODE_CBC, iv)
            if data and (len(data) % 16) != 0:
                data = pad(data, 16)
            return aes.decrypt(data)
        else:
            return None

