import os

# 是否开启debug模式
DEBUG = False

# 读取数据库环境变量
if DEBUG:
    username = os.environ.get("MYSQL_USERNAME", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    db_address = os.environ.get("MYSQL_ADDRESS", "127.0.0.1:3306")
else:
    username = os.environ.get("MYSQL_USERNAME", "root")
    password = os.environ.get("MYSQL_PASSWORD", "root")
    db_address = os.environ.get("MYSQL_ADDRESS", "127.0.0.1:3306")

