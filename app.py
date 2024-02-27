from flask import Flask
import config
from exts import db, mail, cache, csrf, avatars, jwt, cors
from flask_migrate import Migrate
from models import auth
from apps.front import front_bp
from apps.media import media_bp
from apps.cmsapi import cmsapi_bp
from apps.scapi import sc_bp
from apps.toolsapi import tool_bp
from apps.contractMg import contract_bp
from bbscelery import make_celery
import commands


# Python中操作redis安装两个包：
# 1. pip install redis
# 2. pip install hiredis

# 在windows上使用celery，需要借助gevnet
# pip install gevent
# celery -A app.mycelery worker --loglevel=info -P gevent


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
mail.init_app(app)
cache.init_app(app)
csrf.init_app(app)
avatars.init_app(app)
jwt.init_app(app)
cors.init_app(app, resources={r"/cmsapi/*": {"origins": "*"}})
cors.init_app(app, resources={r"/scAnalysis/*": {"origins": "*"}})
cors.init_app(app, resources={r"/toolFunc/*": {"origins": "*"}})
cors.init_app(app, resources={r"/contractMg/*": {"origins": "*"}})

# 排除cmsapi的csrf验证
csrf.exempt(cmsapi_bp)
csrf.exempt(sc_bp)
csrf.exempt(tool_bp)

migrate = Migrate(app, db)

mycelery = make_celery(app)

# 注册蓝图
app.register_blueprint(front_bp)
app.register_blueprint(media_bp)
app.register_blueprint(cmsapi_bp)
app.register_blueprint(sc_bp)
app.register_blueprint(tool_bp)
app.register_blueprint(contract_bp)

# 注册命令
app.cli.command("init_boards")(commands.init_boards)
app.cli.command("init_roles")(commands.init_roles)
app.cli.command("create_test_users")(commands.create_test_users)
app.cli.command("init_developer")(commands.init_developer)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
