#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/27 11:32
@description: 
"""
import getopt
import pyotp
from PIL import Image    #未找到PIL，暂时注释掉
from pyzbar.pyzbar import decode
import re
import sys
import os
from pathlib import Path

from probeX.framework.utils.log import test_logger as logger


# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（假设项目根目录是当前目录的上两级）
project_root = os.path.dirname(os.path.dirname(current_dir))
# 将项目根目录添加到 sys.path
sys.path.append(project_root)

# 从图像中提取密钥
def extract_secret_key(image_path):
    # gen
    img = Image.open(image_path)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode("utf-8")
    return None


def is_base32(s):
    # 验证密钥是否为有效的 Base32 编码
    base32_chars = re.compile(r'^[A-Z2-7]+$')
    return base32_chars.match(s) is not None


def extract_otp(secret_key):
    # 生成OTP
    # 打印密钥以检查其内容
    logger.info("Extracted secret key: {secret_key}".format(secret_key=secret_key))
    # 从 otpauth URL 中提取 Base32 密钥
    if secret_key.startswith('otpauth://'):
        # 提取密钥部分
        query_params = secret_key.split('?', 1)[1]
        params = dict(param.split('=') for param in query_params.split('&'))
        secret_key = params.get('secret', None)
    if secret_key and is_base32(secret_key):
        # 实例化 TOTP 对象
        totp = pyotp.TOTP(secret_key)
         # 生成 OTP
        otp = totp.now()
        # 打印 OTP
        logger.info(f"Generated OTP: {otp}".format(otp=otp))
        return otp
    else:
        logger.error("The extracted key is not a valid Base32 string.")
        return None


def gen_secret_key_from_pic(pic_file):
    current_dir = Path.cwd()
    pic_file_path = current_dir.joinpath(pic_file)
    if not pic_file_path.exists():
        raise RuntimeError("Secret key pic is not provided.")
    secret_key = extract_secret_key(pic_file)
    logger.info(f"Secret Key: {secret_key}")
