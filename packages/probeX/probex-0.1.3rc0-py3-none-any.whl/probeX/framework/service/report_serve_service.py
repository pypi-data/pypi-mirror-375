#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   report_serve_service.py
@Time    :   2025/04/29 15:06:57
@Author  :   yanggy 
@Version :   1.0
@Contact :   yangguangyu_cn@163.com
@License :   (C)Copyright 2021-2022, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib
import os
import subprocess
import sys
import signal
from multiprocessing import Process, Event
from http.server import HTTPServer, SimpleHTTPRequestHandler
from probeX.framework.config.Config import config
from probeX.framework.utils.log import test_logger


# 配置
PORT = 8008
DIRECTORY = config.test_report_dir
PID_FILE = config.test_data_dir.joinpath("report_server.pid")

def _serve_report_server():
    os.chdir(DIRECTORY)
    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    test_logger.info(f"Serving {DIRECTORY} at http://127.0.0.1:{PORT}")
    server.serve_forever()

def start_report_server(args):
    if os.path.exists(PID_FILE):
        test_logger.info("Server already running.")
        return
    cmd = [
        sys.executable,
        __file__,
        "--_serve"
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))
    test_logger.info(f"Report server started with PID {process.pid}")

def stop_report_server(args):
    if not os.path.exists(PID_FILE):
        test_logger.info("No running server.")
        return
    with open(PID_FILE, "r") as f:
        pid = int(f.read())
    try:
        os.kill(pid, signal.SIGTERM)
        test_logger.info(f"Stopped server with PID {pid}")
    except ProcessLookupError:
        test_logger.info("Process already gone.")
    os.remove(PID_FILE)

def status_report_server(args):
    if not os.path.exists(PID_FILE):
        test_logger.info("Server not running.")
        return
    with open(PID_FILE, "r") as f:
        pid = int(f.read())
    try:
        os.kill(pid, 0)
        test_logger.info(f"Server is running with PID {pid}")
    except ProcessLookupError:
        test_logger.info("PID file exists but no process.")
        os.remove(PID_FILE)

# 内部使用的 _serve，直接运行此模块时调用
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--_serve", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--dir", type=str)
    args = parser.parse_args()

    if args._serve:
        _serve_report_server()