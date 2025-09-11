# file: /Users/SL/PythonProject/sl_pos2_api_tool/sl_pos2_api/common.py

import time
import json
import hashlib
import base64
from cryptography.fernet import Fernet


class Common:
    '''
    This class is used to define the common variables and methods for POS2 API.
    '''

    def __init__(self, udb_app_id, udb_device_id, sub_app_id, app_secret,pwdSh1="e2dda013dac6e18616ed2156a04790c087221060"):
        """
        Initialize the Common class with required parameters.

        Args:
            udb_app_id (str): UDB application ID
            udb_device_id (str): UDB device ID
            sub_app_id (str): Sub application ID
            app_secret (str): Application secret key
        """
        self.udb_app_id = udb_app_id
        self.udb_device_id = udb_device_id
        self.sub_app_id = sub_app_id
        self.app_secret = app_secret
        self.pwdSh1 = pwdSh1

    def gen_credit(self, user_id):
        """
        Generate encrypted credit information for authentication.

        Args:
            user_id (str): User ID for authentication

        Returns:
            str: Base64 encoded encrypted credit information
        """
        # 创建JSON数据
        json_data = {
            "verPro": 0,
            "context": "",
            "uid": user_id,
            "pwdSh1": self.pwdSh1,
            "appId": self.udb_app_id,
            "deviceId": self.udb_device_id,
            "subAppId": self.sub_app_id,
            "ip": 989390239,
            "creditType": 1,
            "pwdType": 1,
            "ext": {}
        }

        json_str = json.dumps(json_data, separators=(',', ':'))
        print(f"Credit JSON: {json_str}")

        # 加密处理
        cipher_text = self._encrypt_to_base64_string(json_str, self.app_secret)
        return cipher_text

    def _encrypt_to_base64_string(self, data, secret_key):
        """
        Encrypt data to base64 string using the secret key.

        Args:
            data (str): Data to encrypt
            secret_key (str): Secret key for encryption

        Returns:
            str: Base64 encoded encrypted string
        """
        # 如果secret_key不是32字节，需要进行处理
        key = self._prepare_key(secret_key)

        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('utf-8')

    def _prepare_key(self, secret_key):
        """
        Prepare a valid 32-byte key for Fernet encryption.

        Args:
            secret_key (str): Original secret key

        Returns:
            bytes: 32-byte key
        """
        # 使用SHA-256哈希函数生成32字节的密钥
        key = hashlib.sha256(secret_key.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(key)


# 初始化Common实例
common = Common(
    udb_app_id="1163336839",
    udb_device_id="QWER1234",
    sub_app_id="1",
    app_secret="MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYzdCaxnBnD7s+2kQLWYqgX4l82Q2ZwdtxS/WLmKcz/aBmOO0xWR5wQZZMB1qv5uxtnPlZyPvIJH9ld4PjdMYh+c0CHBgaLt6ReyZVmXUo4fbWlD4FM+P16Ww+s5E/j1ulgpUt71nVdYe7s7qp3+tBl2aUXtBN490DD9oh7Mv1TQIDAQAB"
)

# 生成加密凭证

if __name__ == '__main__':

    cipher_text = common.gen_credit(user_id="4600508114")
    print(f"Encrypted credit: {cipher_text}")
