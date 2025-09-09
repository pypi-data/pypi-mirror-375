import threading
import os
import yaml
from dbutils.pooled_db import PooledDB
import pymysql

class MySQLConnectorFactory:
    _lock = threading.Lock()
    _pools = {}
    _configs = {}

    @classmethod
    def _load_configs(cls, yaml_path="config/db_config.yaml"):
        if cls._configs:
            return
        with open(yaml_path, 'r') as f:
            cls._configs = yaml.safe_load(f)

    @classmethod
    def get_connection(cls, db_key: str, yaml_path="config/db_config.yaml"):
        """
        获取指定数据库连接（从连接池中获取一个连接）
        :param db_key: YAML 配置中的键名，如 'main_db'
        :param yaml_path: YAML 文件路径
        :return: pymysql 连接对象
        """
        cls._load_configs(yaml_path)

        if db_key not in cls._pools:
            with cls._lock:
                if db_key not in cls._pools:  # 双重检查
                    cfg = cls._configs.get(db_key)
                    if not cfg:
                        raise ValueError(f"Database config '{db_key}' not found in {yaml_path}")
                    cls._pools[db_key] = PooledDB(
                        creator=pymysql,
                        maxconnections=10,
                        mincached=2,
                        maxcached=5,
                        blocking=True,
                        host=cfg["host"],
                        port=cfg.get("port", 3306),
                        user=cfg["user"],
                        password=cfg["password"],
                        database=cfg["database"],
                        charset=cfg.get("charset", "utf8mb4")
                    )
        return cls._pools[db_key].connection()
