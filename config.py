import os
from datetime import timedelta

SECRET_KEY = "asdqfsfdsfal"

# 项目根路径
BASE_DIR = os.path.dirname(__file__)

DB_USERNAME = 'root'
DB_PASSWORD = '000000'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = 'sc_platform'

# Session.permanent=True的情况下的过期时间
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (DB_USERNAME,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 邮箱配置
# 我们项目中用的是qq邮箱
# MAIL_USE_TLS: True, 端口号587
# MAIL_USE_SSL: True, 端口号465
# QQ邮箱不支持非加密方式发送邮件
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = True
MAIL_USERNAME = "475207222@qq.com"
MAIL_PASSWORD = "qbnvfgciuykebhbe"
MAIL_DEFAULT_SENDER = "475207222@qq.com"


# Celery的redis配置
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# Flask-Caching配置
CACHE_TYPE = "RedisCache"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_REDIS_HOST = "127.0.0.1"
CACHE_REDIS_PORT = 6379

# 头像配置
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, "media", "avatars")
# 帖子存放路径
POST_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, "media", "post")
# 轮播图图片存放路径
BANNER_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, "media", "banner")
# 智能合约存放路径
CONTRACT_IMAGE_SAVE_PATH = os.path.join(BASE_DIR, "media", "contracts")

CONTRACT_LOGS_SAVE_PATH = os.path.join(BASE_DIR, "media", "logs")

# 每页展示帖子的数量
PER_PAGE_COUNT = 10

# 设置JWT过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=100)

