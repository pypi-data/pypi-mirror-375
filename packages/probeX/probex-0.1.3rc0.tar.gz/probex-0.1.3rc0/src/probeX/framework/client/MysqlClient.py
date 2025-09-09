#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: yanggyc
@created: 2024/5/28 13:56
@description: 
"""
import mysql.connector
from mysql.connector import Error

from airstest.utils.Config import config

class MySQLConnector:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port,
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=3306,
            )
            if self.connection.is_connected():
                print("Connection successful")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def execute_query(self, query, params=None):
        if self.connection is None:
            print("Connection not established.")
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"Error: {e}")

    def fetch_data(self, query, params=None):
        if self.connection is None:
            print("Connection not established.")
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed")


mysql_connector = MySQLConnector(host=config.get("db_host"),
                                 database=config.get("db_name"),
                                 user=config.get("db_user"),
                                 password=config.get("db_password"),
                                 port=config.get("db_port"))

# Usage example:
# connector = MySQLConnector(host="localhost", database="test_db", user="user", password="password")
# connector.connect()
# connector.execute_query("CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(50))")
# connector.execute_query("INSERT INTO test_table (id, name) VALUES (%s, %s)", (1, 'Alice'))
# data = connector.fetch_data("SELECT * FROM test_table")
# print(data)
# connector.close()
