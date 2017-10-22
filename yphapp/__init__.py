from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

app = None
db = SQLAlchemy()

def create_app(config_name):
    global app
    app = Flask(__name__)

    #配置
    cfg = config.CONFIG_CLASS[config_name]
    app.config.from_object(cfg)
    cfg.init_app(app)
    #额外配置
    app.config.from_envvar('YPH_FLASK_CONFIG_EX', True)

    #数据库
    db.init_app(app)
    from . import models

    #注册view
    from . import views

    return app
