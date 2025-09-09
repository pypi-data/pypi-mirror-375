#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/23 14:45
@description:
"""
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

from probeX.framework.client.HTTPClient import HttpClient
from probeX.framework.config.Config import config
from probeX.framework.utils.OTP import extract_otp
from probeX.framework.utils.log import test_logger as logger


class BaseUser():
    """
    基础用户model
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """User Httpclient object
        Returns:
            _type_: _description_
        """
        if self._client is None:
            self._client = HttpClient()  # 只在第一次初始化
        return self._client
    
    def encode_password(self, password, method, **kwargs):
        """encode password

        Args:
            password (str): _description_
            method (str): _description_

        Returns:
            _type_: _description_
        """
        if method.lower() == "rsa":
            public_key_pem = kwargs["public_key_pem"]
            return self.rsa_encode(password=password, 
                                   public_key_pem=public_key_pem)

    def rsa_encode(self, password, public_key_pem):
        """encode password with RSA

        Args:
            password (_type_): _description_
            public_key_pem (_type_): _description_

        Returns:
            _type_: _description_
        """
        public_key = RSA.import_key(public_key_pem)
        cipher_rsa = PKCS1_v1_5.new(public_key)
        encrypted_password = cipher_rsa.encrypt(password.encode())
        return base64.b64encode(encrypted_password).decode(encoding="utf-8")
    
    def get_otp_by_secret(self, secret_key):
        """Get otp code by user secret key.

        Args:
            secret_key (_type_): _description_

        Returns:
            _type_: _description_
        """
        return extract_otp(secret_key) 


if __name__ == '__main__':
    user = BaseUser()
    http_client = user.client
    http_client.add_header({"key1": "value1", "key2": "value2"})
    print(http_client.headers)
